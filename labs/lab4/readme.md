# Lab 4: Doc Gen with MCP

## Learning Objectives

1. Get the Word Document MCP server running
2. Create a plugin to connect to an MCP server
3. Create an agent that uses the MCP Server plugin
4. Wire up Chainlit to test

## Prerequisites

1. Lab 0 is required to have the development environment configured and all dependencies installed
2. This lab is designed to follow Lab 1, not 100% necessary but you are on your own to figure out the missing pieces if you haven't done it

## Get the Word Document MCP server running

TODO:
1. https://github.com/GongRzhe/Office-Word-MCP-Server

## Create a plugin to connect to an MCP server

1. In the **plugins** folder, create a new file named **word_document_plugin.py** and add the following contents:
```
from semantic_kernel.connectors.mcp import MCPSsePlugin

async def get_word_document_plugin() -> MCPSsePlugin:
    """Get the Word Document Plugin."""
    
    plugin = MCPSsePlugin(
        name="WordPlugin",
        description="Word Document MCP Server Plugin",
        url="http://localhost:9090/sse",
    )
    
    await plugin.connect()

    return plugin
```

## Create an agent that uses the MCP Server plugin

1. In the **agents** folder, create a new file named **rewrite_contract_agent.py** and add the following:
```
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from agents.plugins.search_plugin import SearchPlugin
from agents.plugins.word_document_plugin import get_word_document_plugin
from processors.document_processor import DocumentProcessor

async def get_rewrite_contract_agent(processor: DocumentProcessor) -> ChatCompletionAgent:

    rewrite_prompt = processor.prompt_service.load_prompt("rewrite_contract.prompty")
    instructions = processor.prompt_service.render_prompt_as_string(rewrite_prompt, {
        "desired_terms": processor.desired_terms,
    })
    word_document_plugin = await get_word_document_plugin()

    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="rewrite_contract",
        description="Using the style of the uploaded contract, rewrite the entire document based on the template and desired terms using the word document plugin to create a word file.",
        instructions=instructions,
        plugins=[SearchPlugin(processor.search_service), word_document_plugin],
    )
    return agent
```

2. Modify the **assistant_agent.py** file to match the following:
```
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from agents.analyze_clause_agent import get_analyze_clause_agent
from agents.compare_clause_agent import get_compare_clause_agent
from agents.compare_contract_agent import get_compare_contract_agent

from agents.rewrite_contract_agent import get_rewrite_contract_agent
from processors.document_processor import DocumentProcessor

async def get_assistant_agent(processor: DocumentProcessor) -> ChatCompletionAgent:

    compare_clause_agent = get_compare_clause_agent(processor)
    analyze_clause_agent = get_analyze_clause_agent(processor)
    compare_contract_agent = get_compare_contract_agent(processor)
    rewrite_contract_agent = await get_rewrite_contract_agent(processor)

    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="contract_assistant",
        description="A versatile assistant for contract analysis and comparison.",
        instructions="You are a versatile legal assistant capable of comparing clauses, analyzing clauses, and comparing entire contracts based on user requests. Use the appropriate tool based on the user's needs.",
        plugins=[compare_clause_agent, analyze_clause_agent, compare_contract_agent, rewrite_contract_agent],
    )
    return agent
```
The following items changed:
- async is needed now due to the `get_rewrite_contract_agent` being async
- added the line for `rewrite_contract_agent`
- added `rewrite_contract_agent` to the list of plugins

## Wire up Chainlit to test

1. In **main.py** add a new starter to the `set_starters` return, so the array now looks like:
```
    return [
        cl.Starter(
            label="Compare Clause",
            message="Compare the IP clause of the uploaded contract with the template clause and highlight any differences."
        ),
        cl.Starter(
            label="Analyze Clause",
            message="Analyze the retainer clause of the uploaded contract and suggest improvements."
        ),
        cl.Starter(
            label="Compare Contract",
            message="Compare the uploaded contract with the template contract and highlight any differences."
        ),
        cl.Starter(
            label="Rewrite Contract",
            message="Using the word document plugin, get the uploaded contract clauses and the template clauses and create a word document of a new version of the contract."
        )
    ]
```

2. In **main.py** change the call to `get_assistant_agent` to the following:
```
    agent = await get_assistant_agent(processor)
```