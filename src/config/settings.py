import os
from azure.core.credentials import AzureKeyCredential
import dotenv

dotenv.load_dotenv()

class Config:
    # Azure Search Configuration
    AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_API_KEY = os.environ.get("AZURE_SEARCH_API_KEY")
    AZURE_SEARCH_INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME", "agentcon-index")
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
    AZURE_OPENAI_MODEL_NAME = os.environ.get("AZURE_OPENAI_MODEL_NAME", "text-embedding-3-large")
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4.1")
    
    # Document Intelligence Configuration
    AZURE_DOCUMENTINTELLIGENCE_SERVICE = os.getenv("AZURE_DOCUMENTINTELLIGENCE_SERVICE", "doci-agentcon")
    AZURE_DOCUMENTINTELLIGENCE_API_KEY = os.getenv("AZURE_DOCUMENTINTELLIGENCE_API_KEY", "")

    # Embedding Configuration
    EMBED_DIM = int(os.environ.get("EMBED_DIM", "3072"))
    
    # Reference Location Configuration
    STOPWORDS_LEGAL_PATH = "reference/stopwords/legal.txt"
    STOPWORDS_ENGLISH_PATH = "reference/stopwords/english.txt"
    DESIRED_TERMS_PATH = "reference/terms/desired_terms.md"
    PROMPTS_DIRECTORY = "reference/prompts"

    # Credentials
    @property
    def search_credential(self):
        return AzureKeyCredential(self.AZURE_SEARCH_API_KEY)
    
    @property
    def document_intelligence_credential(self):
        return AzureKeyCredential(self.AZURE_DOCUMENTINTELLIGENCE_API_KEY)
    
    @property
    def openai_credential(self):
        return AzureKeyCredential(self.AZURE_OPENAI_API_KEY)

config = Config()