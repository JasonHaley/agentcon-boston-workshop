# From Static Files to Smart Agents: Unlocking Document Intelligence

This repository contains the instructions and code for the 90 minute workshop.

![Contract Review Agent](assets/logo_small.png)

This workshop uses an [AI Scenario](https://adoption.microsoft.com/en-us/scenario-library/) to help set the stage with a business domain and desired functionality: [Using AI Agents to create a contract review agent](https://adoption.microsoft.com/en-us/scenario-library/legal/automated-contract-review-agent/). 

> NOTE: Since a lot of the matrial on that site is geared toward using Copilot, I need to mention I have only used the requirements as inspiration in this workshop, **we do not use Copilot in this solution**

## Workshop Goals

The exercises in this workshop are to provide a hands-on experience to help you understand how you can start with content in unstructured data, process it and use agents to provide a system that can unlock the value for your users.

## Learning Objectives

- **Contract ingestion** - learn to process a pdf using [Azure AI Document Intillegence](https://azure.microsoft.com/en-us/products/ai-services/ai-document-intelligence), identify and create metadata to use in filtering, modify embedded text to be more effective in retrieval.
- **Contract comparison** - 
- **Risk identification and Clause suggestions** - 
- **Rewrite a contract with suggestions** - 

## Prerequisistes

Please install the software ahead of the workshop:
- [VS Code](https://code.visualstudio.com/download)
- [Python 3.12 and PIP](https://www.python.org/downloads/), also recommend installing the [VS Code Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) - this will allow you to debug and step through code later
- (Optional) [Prompty Extension](https://prompty.ai/guides/extension/) - this will allow you to test prompts in VS Code
- [Git](https://git-scm.com/downloads) and [Github login](https://github.com) - these will make working with the workshop easier on you
- [Azure subscription](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account/search) - in order to use Azure AI Document Intelligence and Azure AI Search you'll need a subscription (unless you are in the workshop on September 27, 2025 - see note below)

> NOTE: For those of you in the workshop on September 27, 2025 - I will be providing you with the api keys to use predeployed Azure resources **for the day only**.

## Labs

| Lab                                         |         Link to start page    |
|---------------------------------------------|-------------------------------|
| Lab 0 - Getting started                     | [Link](./labs/lab0/readme.md) |
| Lab 1 - Processing PDFs to be useful in RAG | [Link](./labs/lab1/readme.md) |
| Lab 2 - Create your first agent             | [Link](./labs/lab2/readme.md) |
| Lab 3 - Refactor to use multiple agents     | [Link](./labs/lab3/readme.md) |
| Lab 4 - Doc Gen with a plugin               | [Link](./labs/lab4/readme.md) |

## Contributors

### Jason Haley

Jason is an independent Full Stack Solution Architect with a deep focus on Azure and Microsoft technologies. He is currently focused on helping customers integrate Gen AI functionality into their applications. He also helps run the Boston Azure AI user group, enjoys roasting his own coffee at home and runs ultra marathons every now and then.

[LinkedIn](https://www.linkedin.com/in/jason-a-haley/) | [Twitter](https://x.com/haleyjason) | [Jason's Blog](https://jasonhaley.com/) | [Email](mailto://info@jasonhaley.com)

## Other Resources
- [azure-search-openai-demo](https://github.com/azure-Samples/azure-search-openai-demo/) is an open source RAG sample. A lot of the embedding service and saerch service logic was modeled after this project.
- [Office-Word-MCP-Server](https://github.com/GongRzhe/Office-Word-MCP-Server) is an open source MCP server for creating docx files. A lot of the document service logic is modeled after this project.
