from semantic_kernel.functions import kernel_function

class SearchPlugin:
    """A plugin for searching."""

    def __init__(self, search_service):
        self.search_service = search_service

    @kernel_function(name="search_for_clause_in_uploaded_contract", description="Search for a clause in the uploaded contract based on the search text and return the full clause text.")
    async def search_for_clause_in_uploaded_contract(self, search_text: str, uploaded_contract_filename: str) -> str:
        print(f"Searching for clause in uploaded contract: {uploaded_contract_filename} with search text: {search_text}")

        uploaded_contract_clause = await self.search_service.search_single_hybrid(query=search_text, filter=f"doc_id eq '{uploaded_contract_filename}'")
        if not uploaded_contract_clause:
            return "No matching clause found in the uploaded document. Please try another clause."
        return uploaded_contract_clause.text_full

    @kernel_function(name="search_for_clause_in_template_contract", description="Search for a clause in the template based on the search text and return the full clause text.")
    async def search_for_clause_in_template_contract(self, search_text: str) -> str:
        print(f"Searching for clause in template with search text: {search_text}")

        template_clause = await self.search_service.search_single_hybrid(query=search_text, filter=f"is_template eq true")
        if not template_clause:
            return "No matching clause found in the template. Please try another clause."
        return template_clause.text_full

    @kernel_function(name="get_all_clauses_in_uploaded_contract", description="Get the complete uploaded contract.")
    async def get_all_clauses_in_uploaded_contract(self, uploaded_contract_filename: str) -> str:
        print(f"Getting all clauses in uploaded contract: {uploaded_contract_filename}")

        clauses = await self.search_service.search_clauses_by_filter(filter=f"doc_id eq '{uploaded_contract_filename}'")
        if not clauses or len(clauses) == 0:
            return "No clauses found in the uploaded document."
        return "\n\n".join([f"{clause.clause_type}: {clause.text_full}" for clause in clauses])
    
    @kernel_function(name="get_all_clauses_in_template_contract", description="Get the complete template contract.")
    async def get_all_clauses_in_template_contract(self) -> str:
        print(f"Getting all clauses in template contract")

        clauses = await self.search_service.search_clauses_by_filter(filter=f"is_template eq true")
        if not clauses or len(clauses) == 0:
            return "No clauses found in the template."
        return "\n\n".join([f"{clause.clause_type}: {clause.text_full}" for clause in clauses])