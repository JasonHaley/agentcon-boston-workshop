from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from agents.plugins.search_plugin import SearchPlugin
from processors.document_processor import DocumentProcessor

def get_analyze_clause_agent(processor: DocumentProcessor) -> ChatCompletionAgent:
    
    analyze_prompt = processor.prompt_service.load_prompt("analyze_clause.prompty")
    instructions = processor.prompt_service.render_prompt_as_string(analyze_prompt, {
        "desired_terms": processor.desired_terms,
    })

    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="analyze_clause",
        description="Analyze a specific clause in the uploaded contract and suggest improvements based on best practices.",
        instructions=instructions,
        plugins=[SearchPlugin(processor.search_service)],
    )
    return agent