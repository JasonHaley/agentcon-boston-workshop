from collections.abc import AsyncGenerator
from enum import Enum
from typing import Union
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from models.document import Page, File
from config.settings import config

class ObjectType(Enum):
    NONE = -1
    TABLE = 0
    FIGURE = 1

class DocumentIntelligenceService:
    def __init__(self):
        self.endpoint = f"https://{config.AZURE_DOCUMENTINTELLIGENCE_SERVICE}.cognitiveservices.azure.com"
        self.credential = config.document_intelligence_credential

    async def parse_document(self, file: File) -> AsyncGenerator[Page, None]:
        print(f"Extracting text from '{file.content.name}' using Azure Document Intelligence")
        model_id = "prebuilt-layout"
        
        content_bytes = file.content.read()
        
        async with DocumentIntelligenceClient(
            endpoint=self.endpoint, 
            credential=self.credential
        ) as client:
            poller = await client.begin_analyze_document(
                model_id=model_id,
                body=content_bytes,
                content_type="application/octet-stream",
                output_content_format="markdown"
            )

            analyze_result: AnalyzeResult = await poller.result()
            print("Document analysis completed successfully")
            print(f"Analyzed document with {len(analyze_result.pages)} pages")
            
            offset = 0
            for page in analyze_result.pages:
                page_offset = page.spans[0].offset
                page_length = page.spans[0].length
                mask_chars: list[tuple[ObjectType, Union[int, None]]] = [
                    (ObjectType.NONE, None)
                ] * page_length
                                
                page_text = ""
                for idx, mask_char in enumerate(mask_chars):
                    object_type, object_idx = mask_char
                    if object_type == ObjectType.NONE:
                        page_text += analyze_result.content[page_offset + idx]
                
                # Clean up the page text
                page_text = page_text.replace("<!-- PageBreak -->", "")
                page_text = page_text.strip()
                
                pg = Page(page_num=page.page_number, offset=offset, text=page_text)
                yield pg
                offset += len(page_text)
