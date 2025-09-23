import chainlit as cl
import os
from dotenv import load_dotenv
from typing import List

from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.functions import kernel_function

from processors.document_processor import DocumentProcessor
from agents.compare_clause_agent import get_compare_clause_agent
from agents.analyze_clause_agent import get_analyze_clause_agent
from agents.compare_contract_agent import get_compare_contract_agent
from agents.assistant_agent import get_assistant_agent

load_dotenv()

processor = DocumentProcessor()


class CreateFileDownloadPlugin:
    """A plugin to create a file download link."""

    def __init__(self, message: cl.Message = None):
        self.message = message

    @kernel_function(name="create_chainlit_file_download", description="Create a Chainlit file download link for the given filename.")
    async def create_file_download(self, filename: str) -> cl.File:
        """Create a file download link for the given filename."""
        
        elements = [ 
            cl.File(
                name=filename,
                path=filename,
                display="inline"
            )
        ]
        if self.message:
             await cl.Message(
                content="File Link", elements=elements
            ).send()

@cl.set_starters
async def set_starters():
    """Set starters for the chat."""
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
            message="Analyze the uploaded contract with the template contract and rewrite a new version of the contract that combines the best clauses from both contracts into a new contract."
        )
    ]

@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat with an agent."""
    agent = get_assistant_agent(processor)
    agent.kernel.add_plugin(CreateFileDownloadPlugin(cl.Message(content="")))
    
    cl.SemanticKernelFilter(kernel=agent.kernel)
    cl.user_session.set("agent", agent)

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    agent = cl.user_session.get("agent")
    thread = cl.user_session.get("thread", None)

    # Check if there are files attached to the message
    if message.elements:
        await cl.Message(content="Processing your uploaded files...").send()
        await process_files(message.elements)

    current_filename = cl.user_session.get("filename", "sample-01.pdf") # Hardcoded for debugging
    
    if not thread:
        message = f"Using your plugins to retrieve the template contract and the uploaded contract using the file name: {current_filename}, perform the following: {message.content}"
    else:
        message = message.content
    
    await stream_agent_response(
        agent=agent, 
        thread=thread, 
        answer=cl.Message(content=""), 
        message=message
    )

async def stream_agent_response(agent: ChatCompletionAgent, thread: ChatHistoryAgentThread, answer: cl.Message, message: str):
    """Stream the agent's response."""

    async for response in agent.invoke_stream(messages=message, thread=thread):
        content = getattr(getattr(response, "content", None), "content", None)
        if content:
            await answer.stream_token(content)
        thread = getattr(response, "thread", thread)
    
    await answer.update()
    cl.user_session.set("thread", thread)
    await answer.send()

async def process_files(files: List[cl.File]):
    """Process uploaded files."""
   
    if len(files) > 1:
        await cl.Message(content="Only one file is supported at a time. Please upload a single file.").send()
        return

    filename = ""
    for file in files:
        filename = file.name
        
        await cl.Message(content=f"Ingesting file: {filename} ...").send()

        with open(file.path, "rb") as f:
            stats = await processor.process_file(f, filename)
            print(f"Processed {stats.clauses_created} clauses from {stats.total_pages} pages")

        # Send confirmation back to user
        await cl.Message(content=f"Successfully ingested file: {filename}").send()
        cl.user_session.set("filename", filename)

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)