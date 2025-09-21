from typing import TypedDict
import tiktoken
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)
from openai import AsyncAzureOpenAI, RateLimitError
from config.settings import config

class EmbeddingBatch:
    def __init__(self, texts: list[str], token_length: int):
        self.texts = texts
        self.token_length = token_length

SUPPORTED_BATCH_AOAI_MODEL = {
    "text-embedding-ada-002": {"token_limit": 8100, "max_batch_size": 16},
    "text-embedding-3-small": {"token_limit": 8100, "max_batch_size": 16},
    "text-embedding-3-large": {"token_limit": 8100, "max_batch_size": 16},
}

class EmbeddingService:
    def __init__(self):
        self.model_name = config.AZURE_OPENAI_MODEL_NAME
        self.dimensions = config.EMBED_DIM

    def calculate_token_length(self, text: str) -> int:
        encoding = tiktoken.encoding_for_model(self.model_name)
        return len(encoding.encode(text))

    async def create_client(self) -> AsyncAzureOpenAI:
        return AsyncAzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            azure_deployment=config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            api_version="2024-06-01"
        )

    def split_text_into_batches(self, texts: list[str]) -> list[EmbeddingBatch]:
        batch_info = SUPPORTED_BATCH_AOAI_MODEL.get(self.model_name)
        if not batch_info:
            raise NotImplementedError(
                f"Model {self.model_name} is not supported with batch embedding operations"
            )

        batch_token_limit = batch_info["token_limit"]
        batch_max_size = batch_info["max_batch_size"]
        batches: list[EmbeddingBatch] = []
        batch: list[str] = []
        batch_token_length = 0
        
        for text in texts:
            text_token_length = self.calculate_token_length(text)
            if batch_token_length + text_token_length >= batch_token_limit and len(batch) > 0:
                batches.append(EmbeddingBatch(batch, batch_token_length))
                batch = []
                batch_token_length = 0

            batch.append(text)
            batch_token_length = batch_token_length + text_token_length
            if len(batch) == batch_max_size:
                batches.append(EmbeddingBatch(batch, batch_token_length))
                batch = []
                batch_token_length = 0

        if len(batch) > 0:
            batches.append(EmbeddingBatch(batch, batch_token_length))

        return batches

    def before_retry_sleep(self, retry_state):
        print("Rate limited on the OpenAI embeddings API, sleeping before retrying...")

    async def create_embedding_batch(self, texts: list[str], dimensions: int) -> list[list[float]]:
        batches = self.split_text_into_batches(texts)
        embeddings = []
        client = await self.create_client()
        
        for batch in batches:
            async for attempt in AsyncRetrying(
                retry=retry_if_exception_type(RateLimitError),
                wait=wait_random_exponential(min=15, max=60),
                stop=stop_after_attempt(15),
                before_sleep=self.before_retry_sleep,
            ):
                with attempt:
                    emb_response = await client.embeddings.create(
                        model=self.model_name, 
                        input=batch.texts, 
                        dimensions=dimensions
                    )
                    embeddings.extend([data.embedding for data in emb_response.data])
                    print(
                        f"Computed embeddings in batch. Batch size: {len(batch.texts)}, "
                        f"Token count: {batch.token_length}"
                    )

        return embeddings

    async def create_embeddings(self, texts: list[str]) -> list[list[float]]:
        return await self.create_embedding_batch(texts, self.dimensions)
    
    async def compute_text_embedding(self, q: str):
        
        class ExtraArgs(TypedDict, total=False):
            dimensions: int

        dimensions_args: ExtraArgs = (
            {"dimensions": self.dimensions}
        )
        client = await self.create_client()
        embedding = await client.embeddings.create(
            model=self.model_name,
            input=q,
            **dimensions_args,
        )
        return embedding.data[0].embedding