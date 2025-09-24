import json
import logging
from pathlib import Path
from typing import BinaryIO, List, Optional, AsyncGenerator
from dataclasses import dataclass

from langchain.text_splitter import MarkdownHeaderTextSplitter

from models.document import File
from models.clause import Clause
from services.document_intelligence import DocumentIntelligenceService
from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from services.prompt_service import PromptyService
from services.search_service import SearchService
from utils.text_processing import load_stopwords, clean_text
from utils.clause_classifier import classify_clause_heading
from config.settings import config


@dataclass
class ProcessingStats:
    """Track processing statistics for monitoring and debugging."""
    filename: str
    total_pages: int
    total_characters: int
    total_chunks: int
    clauses_created: int


class DocumentProcessor:
    """Processes documents by extracting text, splitting into chunks, and indexing clauses."""
    
    # Class constants
    DEFAULT_HEADERS = [
        ("#", "Header 1"),
        ("##", "Header 2"), 
        ("###", "Header 3"),
    ]
    
    def __init__(
        self,
        doc_intelligence: Optional[DocumentIntelligenceService] = None,
        embedding_service: Optional[EmbeddingService] = None,
        search_service: Optional[SearchService] = None,
        prompt_service: Optional[PromptyService] = None,
        document_service: Optional[DocumentService] = None,
        headers_to_split_on: Optional[List[tuple]] = None
    ):
        """Initialize the DocumentProcessor with necessary services and configurations."""
        self.doc_intelligence = doc_intelligence or DocumentIntelligenceService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.search_service = search_service or SearchService(self.embedding_service)
        self.prompt_service = prompt_service or PromptyService()
        self.document_service = document_service or DocumentService()
        self.logger = logging.getLogger(__name__)
        
        # TODO: Initialize text splitter
                
        # Load stopwords once during initialization
        self._load_stopwords()
                
        # Load desired terms if configured
        self.desired_terms = self._load_desired_terms()
    
    def _load_stopwords(self) -> None:
        """Load stopwords from configuration paths."""
        try:
            self.stopwords = load_stopwords(
                config.STOPWORDS_LEGAL_PATH, 
                config.STOPWORDS_ENGLISH_PATH
            )
            self.logger.info(f"Loaded {len(self.stopwords)} stopwords")
        except Exception as e:
            self.logger.error(f"Failed to load stopwords: {e}")
            self.stopwords = set()  # Fallback to empty set
    
    def _load_desired_terms(self) -> str:
        """Load desired terms file content as a single string."""
        try:
            desired_terms_path = getattr(config, "DESIRED_TERMS_PATH", None)
            if not desired_terms_path:
                self.logger.warning("No DESIRED_TERMS_PATH configured")
                return ""
            with open(desired_terms_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.logger.info(f"Loaded desired terms file ({len(content)} characters)")
            return content
        except Exception as e:
            self.logger.error(f"Failed to load desired terms: {e}")
            return ""

    async def process_file(self, file: BinaryIO, filename: str) -> ProcessingStats:
        """Process a single file and return processing statistics.
        
        Args:
            file: Binary file object to process
            filename: Name of the file being processed
            
        Returns:
            ProcessingStats object with processing details
            
        Raises:
            Exception: If processing fails at any stage
        """
        self.logger.info(f"Starting processing: {filename}")
        
        try:
            # TODO: Parse document into pages
            
            # TODO: Combine all page text
                        
            # TODO: Split into chunks and create clauses
                        
            await self._index_clauses(clauses)

            stats = self._create_stats(filename, pages, full_text, [], clauses)
            self.logger.info(f"Successfully processed {filename}: {stats.clauses_created} clauses indexed")
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to process {filename}: {e}")
            raise
    
    async def _extract_pages(self, file: BinaryIO, filename: str) -> List:
        """Extract pages from document using document intelligence service."""
        file_obj = File(content=file)
        
        try:
            pages = [page async for page in self.doc_intelligence.parse_document(file_obj)]
            
            for page in pages:
                self.logger.debug(
                    f"Extracted page {page.page_num} with {len(page.text)} characters"
                )
            
            return pages
            
        finally:
            file_obj.close()
    
    def _combine_page_text(self, pages: List) -> str:
        """Combine text from all pages into a single string."""
        full_text = "".join(page.text for page in pages)
        self.logger.debug(f"Combined text length: {len(full_text)} characters")
        return full_text
    
    async def _create_clauses(self, full_text: str, filename: str) -> List[Clause]:
        """Split text into chunks and create Clause objects."""
        chunks = self.markdown_splitter.split_text(full_text)
        clauses = []
        
        for chunk_index, chunk in enumerate(chunks):
            clause = self._create_single_clause(chunk, chunk_index, filename)
            clauses.append(clause)
            
            self.logger.debug(
                f"Created clause {chunk_index} for {filename}: "
                f"type={clause.clause_type}, header={clause.section}"
            )
        
        return clauses
    
    def _create_single_clause(self, chunk, chunk_index: int, filename: str) -> Clause:
        """Create a single Clause object from a text chunk."""
        # Get the most specific header available
        section_header = self._extract_section_header(chunk.metadata)
        
        # Classify the clause type
        clause_type = classify_clause_heading(section_header, "")
        
        # Create unique ID for this clause
        file_id = Path(filename).stem  # Remove extension for cleaner ID
        clause_id = f"{file_id}_{chunk_index}"
        
        return Clause(
            id=clause_id,
            doc_id=filename,
            section_index=chunk_index,
            section=section_header,
            text_full=chunk.page_content,
            # TODO: populate clean text property
            entity_type="clause" if clause_type else "",
            clause_type=clause_type or "",
            is_template=self._is_template_file(filename)
        )
    
    def _extract_section_header(self, metadata: dict) -> str:
        """Extract the most specific header from chunk metadata."""
        return (
            # TODO: Extract actual header from metadata
            "Unknown"
        )
    
    def _is_template_file(self, filename: str) -> bool:
        """Check if filename indicates this is a template file."""
        return "template" in filename.lower()
    
    async def _index_clauses(self, clauses: List[Clause]) -> None:
        """Create embeddings for clauses and upload to search index."""
        # Extract clean text for embedding generation
        texts = [clause.text_clean for clause in clauses]
        
        # Create embeddings
        # TODO create embeddings
        
        # Upload to search index
        # TODO upload to search index
        
        self.logger.info(f"Successfully indexed {len(clauses)} clauses")
    
    def _create_stats(
        self, 
        filename: str, 
        pages: List, 
        full_text: str, 
        chunks: List, 
        clauses: List[Clause]
    ) -> ProcessingStats:
        """Create processing statistics object."""
        return ProcessingStats(
            filename=filename,
            total_pages=len(pages),
            total_characters=len(full_text),
            total_chunks=len(chunks),
            clauses_created=len(clauses)
        )


# If you need to create the search index in Azure Search, you can run this script directly.
async def main():
    processor = DocumentProcessor()
    processor.search_service.create_index_if_needed();

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())