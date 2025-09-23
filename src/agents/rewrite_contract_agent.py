from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from agents.plugins.doc_gen_plugin import DocGenPlugin
from agents.plugins.search_plugin import SearchPlugin
from processors.document_processor import DocumentProcessor

def get_rewrite_analysis_agent(processor: DocumentProcessor, kernel: Kernel) -> ChatCompletionAgent:

    rewrite_analysis_prompt = processor.prompt_service.load_prompt("rewrite_analysis.prompty")
    instructions = processor.prompt_service.render_prompt_as_string(rewrite_analysis_prompt, {
        "desired_terms": processor.desired_terms,
    })
    
    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="rewrite_analysis_contract",
        description="Analyze the contracts to prepare to rewrite the contract.",
        instructions=instructions,
        kernel=kernel,
        plugins=[SearchPlugin(processor.search_service)],
    )
    return agent

def get_rewrite_contract_agent(processor: DocumentProcessor, kernel: Kernel) -> ChatCompletionAgent:

    rewrite_rewrite_prompt = processor.prompt_service.load_prompt("rewrite_contract.prompty")
    instructions = processor.prompt_service.render_prompt_as_string(rewrite_rewrite_prompt, {
        "desired_terms": processor.desired_terms,
    })
    
    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="rewrite_rewrite_contract",
        description="Rewrite the contract using the style of the uploaded contract, rewrite the entire document based on the template and desired terms using the word document plugin to create a word file.",
        instructions=instructions,
        kernel=kernel,
        plugins=[DocGenPlugin(processor.document_service)],
    )
    return agent