import chainlit as cl
import os
from dotenv import load_dotenv
from typing import List

# TODO: Add document_processor import here

load_dotenv()

# TODO: Initialize your document processor here

@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat with an agent."""
    # TODO: Agents will be added here later

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    
    # Check if there are files attached to the message
    if message.elements:
        await cl.Message(content="Processing your uploaded files...").send()
        await process_files(message.elements)
    else:
        await cl.Message(content="No files uploaded. Please attach a file using the paperclip icon.").send()

async def process_files(files: List[cl.File]):
    """Process uploaded files."""
   
   # TODO: Add file processing logic here

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)