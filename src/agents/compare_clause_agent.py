from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from agents.plugins.search_plugin import SearchPlugin
from processors.document_processor import DocumentProcessor

def get_compare_clause_agent(processor: DocumentProcessor) -> ChatCompletionAgent:
    compare_clause = processor.prompt_service.load_prompt("compare_clause.prompty")
    instructions = processor.prompt_service.render_prompt_as_string(compare_clause, {
        "desired_terms": processor.desired_terms,
    })

    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="compare_clause",
        description="Compare the entire uploaded contract with the template and highlight any differences.",
        instructions=instructions,
        plugins=[SearchPlugin(processor.search_service)],
    )
    return agent