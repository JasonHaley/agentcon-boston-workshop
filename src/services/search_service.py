from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import (
    QueryType,
    VectorQuery,
    VectorizedQuery,
)

from models.clause import Clause
from config.settings import config
from services.embedding_service import EmbeddingService

class SearchService:
    """Service for managing Azure Search index and performing search operations."""
    def __init__(self, embedding_service: EmbeddingService):
        self.endpoint = config.AZURE_SEARCH_ENDPOINT
        self.index_name = config.AZURE_SEARCH_INDEX_NAME
        self.credential = config.search_credential
        self.dimensions = config.EMBED_DIM
        self.embedding_service = embedding_service

    def create_index_if_needed(self):
        """Create the search index in Azure Search if it does not already exist."""
        sic = SearchIndexClient(self.endpoint, self.credential)
        existing = [i.name for i in sic.list_indexes()]
        if self.index_name in existing:
            return

        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SimpleField(name="doc_id", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="section_index", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SimpleField(name="section", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="entity_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="clause_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="is_template", type=SearchFieldDataType.Boolean, filterable=True),
            SearchableField(name="text_full", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
            SearchableField(name="text_clean", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
            SearchField(
                name="embeddings",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                filterable=False,
                sortable=False,
                facetable=False,
                vector_search_dimensions=self.dimensions,
                vector_search_profile_name="embeddings-profile"
            ),
        ]

        # Configure vectorizer
        text_vectorizer = AzureOpenAIVectorizer(
            vectorizer_name="embeddings-vectorizer",
            parameters=AzureOpenAIVectorizerParameters(
                resource_url=config.AZURE_OPENAI_ENDPOINT,
                deployment_name=config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                model_name=config.AZURE_OPENAI_MODEL_NAME,
            ),
        )
        
        # Configure algorithm
        text_vector_algorithm = HnswAlgorithmConfiguration(
            name="hnsw_config",
            parameters=HnswParameters(metric="cosine"),
        )
        
        # Configure compression
        text_vector_compression = BinaryQuantizationCompression(
            compression_name="embeddings-compression",
            truncation_dimension=1024, 
            rescoring_options=RescoringOptions(
                enable_rescoring=True,
                default_oversampling=10,
                rescore_storage_method=VectorSearchCompressionRescoreStorageMethod.PRESERVE_ORIGINALS,
            ),
            rerank_with_original_vectors=None,
            default_oversampling=None,
        )
        
        # Configure profile
        text_vector_search_profile = VectorSearchProfile(
            name="embeddings-profile",
            algorithm_configuration_name=text_vector_algorithm.name,
            compression_name=text_vector_compression.compression_name,
            vectorizer_name=text_vectorizer.vectorizer_name,
        )

        vs = VectorSearch(
            profiles=[text_vector_search_profile],
            algorithms=[text_vector_algorithm],
            compressions=[text_vector_compression],
            vectorizers=[text_vectorizer],
        )

        idx = SearchIndex(
            name=self.index_name, 
            fields=fields, 
            semantic_search=SemanticSearch(
                default_configuration_name="default",
                configurations=[
                    SemanticConfiguration(
                        name="default",
                        prioritized_fields=SemanticPrioritizedFields(
                            title_field=SemanticField(field_name="section"),
                            content_fields=[SemanticField(field_name="text_clean")],
                        ),
                    )
                ],
            ),
            vector_search=vs
        )
        sic.create_index(idx)

    def create_search_client(self) -> SearchClient:
        """Create an asynchronous search client for the index."""
        return SearchClient(
            endpoint=self.endpoint, 
            index_name=self.index_name, 
            credential=self.credential
        )

    async def upload_clauses(self, clauses: list[Clause], embeddings: list[list[float]]):
        """Upload clauses with their embeddings to the search index."""
        MAX_BATCH_SIZE = 1000
        clause_batches = [
            clauses[i : i + MAX_BATCH_SIZE] 
            for i in range(0, len(clauses), MAX_BATCH_SIZE)
        ]

        async with self.create_search_client() as search_client:
            for batch_index, batch in enumerate(clause_batches):
                start_idx = batch_index * MAX_BATCH_SIZE
                end_idx = start_idx + len(batch)
                batch_embeddings = embeddings[start_idx:end_idx]
                
                documents = []
                for i, clause in enumerate(batch):
                    doc = clause.to_dict()
                    doc["embeddings"] = batch_embeddings[i]
                    documents.append(doc)
                
                await search_client.upload_documents(documents)

    async def search_clauses_by_filter(self, filter: str) -> list[Clause]:
        """Search for clauses matching a filter and return all results ordered by section index."""
        async with self.create_search_client() as search_client:
            results = await search_client.search(
                search_text="*", 
                filter=filter,
                order_by=["section_index asc"],
            )

            clauses = [] 

            async for page in results.by_page():
                async for result in page:
                    clauses.append(Clause.from_dict(result))
                    
            return clauses
    
    async def search_single_clause_by_filter(self, filter: str) -> Clause | None:
        """Search for a single clause matching a filter."""
        async with self.create_search_client() as search_client:
            results = await search_client.search(
                search_text="*",
                filter=filter,
                top=1,
            )

            async for page in results.by_page():
                async for result in page:
                    return Clause.from_dict(result)
            return None

    async def search_single_hybrid(self, query: str, filter: str) -> Clause | None:
        """Search for a single clause using hybrid search (semantic + vector)."""
        vector_query = await self.create_vector_query(query)
        
        async with self.create_search_client() as search_client:
            results = await search_client.search(
                search_text=query,
                filter=filter,
                query_type=QueryType.SEMANTIC,
                vector_queries=[vector_query],
                top=1,
                semantic_configuration_name="default",
                semantic_query=query,
            )

            async for page in results.by_page():
                async for result in page:
                    return Clause.from_dict(result)
            return None

    async def search_single_semantic(self, query: str, filter: str) -> Clause | None:
        """Search for a single clause using semantic search with vector fallback."""
        vector_query = await self.create_vector_query(query)
        
        async with self.create_search_client() as search_client:
            results = await search_client.search(
                filter=filter,
                query_type=QueryType.SEMANTIC,
                vector_queries=[vector_query],
                top=1,
                semantic_configuration_name="default",
                semantic_query=query,
            )

            async for page in results.by_page():
                async for result in page:
                    return Clause.from_dict(result)
            return None
        
    async def create_vector_query(self, text: str) -> VectorQuery:
        """Create a vector query for the given text."""
        query_vector = await self.embedding_service.compute_text_embedding(text)
        return VectorizedQuery(vector=query_vector, k_nearest_neighbors=50, fields="embeddings")