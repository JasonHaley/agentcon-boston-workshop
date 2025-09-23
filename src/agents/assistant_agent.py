from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from agents.analyze_clause_agent import get_analyze_clause_agent
from agents.compare_clause_agent import get_compare_clause_agent
from agents.compare_contract_agent import get_compare_contract_agent

from processors.document_processor import DocumentProcessor
from agents.rewrite_contract_agent import get_rewrite_analysis_agent, get_rewrite_contract_agent

def get_assistant_agent(processor: DocumentProcessor) -> ChatCompletionAgent:
    
    compare_clause_agent = get_compare_clause_agent(processor)
    analyze_clause_agent = get_analyze_clause_agent(processor)
    compare_contract_agent = get_compare_contract_agent(processor)

    kernel = Kernel()
    analysis_agent = get_rewrite_analysis_agent(processor, kernel)
    rewrite_agent = get_rewrite_contract_agent(processor, kernel)
    
    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="contract_assistant",
        description="A versatile assistant for contract analysis and comparison.",
        instructions="You are a versatile legal assistant capable of comparing clauses, analyzing clauses, comparing entire contracts and rewriting contracts based on user requests. Use the appropriate tool based on the user's needs.",
        kernel=kernel,
        plugins=[compare_clause_agent, analyze_clause_agent, compare_contract_agent, analysis_agent, rewrite_agent],
    )
    return agent