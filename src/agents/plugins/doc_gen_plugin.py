from semantic_kernel.functions import kernel_function

class DocGenPlugin:
    """A plugin for generating documents."""

    def __init__(self, document_service):
        self.document_service = document_service

    @kernel_function(name="create_document", description="Create a new Word document with optional metadata.")
    async def create_document(self, filename: str, title: str, author: str) -> str:
        
        print(f"Creating document: {filename}, title: {title}, author: {author}")
        
        return await self.document_service.create_document(filename, title, author)

    @kernel_function(name="add_section", description="Adds a heading and list of strings as paragraphs to a Word document.")
    async def add_section(self, filename: str, heading: str, heading_level: int, paragraphs: list[str]) -> str:

        print(f"Adding section to document: {filename}, heading: {heading}, paragraphs: {paragraphs}")

        await self.document_service.add_heading(filename, heading, heading_level)
        for paragraph in paragraphs:
            await self.document_service.add_paragraph(filename, paragraph)
        
        return f"Section '{heading}' added to document '{filename}'."

    @kernel_function(name="add_heading", description="Add a heading to a Word document.")
    async def add_heading(self, filename: str, text: str, level: int) -> str:
        
        print(f"Adding heading to document: {filename}, text: {text}, level: {level}")  
        
        return await self.document_service.add_heading(filename, text, level)
    
    @kernel_function(name="add_paragraph", description="Add a paragraph to a Word document.")
    async def add_paragraph(self, filename: str, text: str) -> str:
        
        print(f"Adding paragraph to document: {filename}, text: {text}")

        return await self.document_service.add_paragraph(filename, text)