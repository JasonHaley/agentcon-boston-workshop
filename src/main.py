import chainlit as cl
import os
from dotenv import load_dotenv
from typing import List

from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
# TODO: Add kernel_function import here

# TODO: Add document_processor import here
# TODO: Add the get_compare_clause_agent import here
# TODO: Add the get_analyze_clause_agent import here
# TODO: Add the get_compare_contract_agent import here
# TODO: Add the get_assistant_agent import here

load_dotenv()

# TODO: Initialize your document processor here

# TODO: Add starters

# TODO: Add CreateFileDownloadPlugin here

@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat with an agent."""
    # TODO: Agents will be added here later

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    #TODO: get the agent and thread for the user session if there (replace the whole method content)

    # Check if there are files attached to the message
    if message.elements:
        await cl.Message(content="Processing your uploaded files...").send()
        await process_files(message.elements)
    

async def process_files(files: List[cl.File]):
    """Process uploaded files."""
   
   # TODO: Add file processing logic here

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)