# Lab 1: Processing PDFs to be useful in RAG

## Learning Objectives

1. Parse a pdf contract file using Azure AI Document Intelligence
2. Use LangChain to split the file into clauses
3. Create metadata about the clauses and remove legal stop words
4. Create embeddings for the clauses
5. Save clauses to an Azure AI Search Index
6. Wire up Chainlit to test

## Prerequisites

1. Lab 0 is required to have the development environment configured and all dependencies installed

## High level overview of what is provided

In order for this workshop not to be the specifics about how to implement a RAG system, I have provided most of the RAG implementation. This lab should be a quick walkthrough of the pieces and adding some code that wires it together. However, I did want the lab to be provide you with a realistic scenario and useful code that resembles a real code project.

![Starter Files](assets/lab1-img1.png)

- The **config** folder: Contains a utility class that provides access to the environment variables and credentials used by the system.
- The **data** folder: Contains two sample contract pdf files.
- The **models** folder: Contains a few models used by the document parsing and processing.
- The **processors** folder: Contains the document_processor.py file, which is the main class we'll be working with in Lab 1.
- The **prompts** folder: Contains the prompts used by the agents are located
- The **public** folder: Is a Chainlit folder and contains the logo file you'll see soon
- The **reference** folder: Contains refrence files used by the system, some for data processing and others for LLM interaction
- The **services** folder: Contains the Azure, OpenAI resource and prompty interaction logic.
- The **utils** folder: Contains some utility code used during document processing.
- The **main.py** file: Is the file that contains the Chainlit event handlers and will be the place all things get wired to the UI

> NOTE: As I'm sure you are probably aware of, whitespace means something to python, so you may need to change some of the indentations when copying and pasting code.

## Parse a pdf contract file using Azure AI Document Intelligence

1. Open the src/processors/**document_processor.py** file in VS Code
2. Locate the **process_file** method (should start around line 98) and find the comment `# TODO: Parse document into pages`. Replace it with the following:
```
            # Parse document into pages
            pages = await self._extract_pages(file, filename)
            if not pages:
                raise ValueError(f"No pages extracted from {filename}")
```
This code has the internal method (right below the process_file method) _extract_pages, use the doc_intelligence service to parse the uploaded pdf and return a list of the Page class (in the models/document.py file).

The bulk of the work is performed by the DocumentIntelligenceService parse_document method (shown below):
![Parse Document](assets/lab1-img2.png)

As you can see, the document is set to be parse as markdown, then due to the way the DocumentIntelligence SDK works, you need to await a poller.result() to know when the anaysis is complete. Once the result is returned, the pages are enumerated the Page model is populated with the text and offsets.

3. Back in the **process_file** method, find the comment `# TODO: Combine all page text` and replace it with the following:
```
            # Combine all page text
            full_text = self._combine_page_text(pages)
```
This code uses the interal method _combine_page_text to aggregate all the text in the document into the `full_text` variable.

Now we have all the text from the pdf.

> ## RAG Note
> 
> When you are parsing files in order to use for a retrieval system, it is important to know what is in those documents in order to make your retrieval more effective. The old saying "Garbage in, Garbage out" applies here.
> 
> If you open the sample pdf files in the data directory, you will notice the clauses of the contract are nicely separated by headings.
> This is why we are using markdown to parse these files.
>
> We don't have any tables, figures or images in these files, but if you did - it is at this point in the project you would want to
> think through how you are going to make that data useful for a retrieval system. 

## Use LangChain to split the file into clauses

LangChain has a great text splitter that will take the PDF text and create chunks broken on the headings for us: [MarkdownHeaderTextSplitter](https://python.langchain.com/docs/how_to/markdown_header_metadata_splitter/)

1. In the **document_processor.py** file, around line 34, you can see the constant `DEFAULT_HEADERS` defined:

![DEFAULT HEADERS](assets/lab1-img3.png)

This will be used to configure the splitter to split on the 3rd level of markdown headers if it finds them, otherwise the 2nd and then the 1st if it doesn't find 2nd level.

2. Locate the comment `# TODO: Initialize text splitter` and replace it with the following:
```
        # Initialize text splitter
        headers = headers_to_split_on or self.DEFAULT_HEADERS
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers,
            strip_headers=True
        )
```
This instantiates the splitter, sets the heading levels and indicates the section headers should be stripped from the text.

> **Question**: Why am I removing the header text from the chunks?
> 
> **Answer**: This has to do with knowing the data and how we want it to be useful for retrieval. The system is going to work with clauses of the contract, we don't need the heading in that clause - so we will use it as metadata instead.

3. Again navigate to the **process_file** method and locate the comment `# TODO: Split into chunks and create clauses` and replace it with this:
```
            clauses = await self._create_clauses(full_text, filename)
            if not clauses:
                self.logger.warning(f"No clauses created for {filename}")
                return self._create_stats(filename, pages, full_text, [], [])
```
This code uses the internal method `_create_clauses` which splits the `full_text` using the markdown splitter, then uses another internal method `_create_single_clause` which populates a `Clause` model. This is also the method that populates useful metadata on the Clause model. The result ends up being a list of clauses along with meaningful metadata.

![_create_clasues](assets/lab1-img4.png)

## Create metadata about the clauses and remove legal stop words

So far the PDF has been parsed as markdown and split into the contract clauses using the markdown splitter. Next what can we do in addition to just having the text chunk from pdf to help our retrieval system?

### Metadata
Metadata we can use and get from the content and context of the chunks:
- heading
- use the heading to categorize the clause
- index of the clause
- indicate if it is a template file or not

### Stop words
Another technique we can use, is the removal of legal stop words from the pdf text chunk before we calculate embeddings on the text. Stop words are common words that occur often but carry very little substantive information, removing them should "sharpen" the effectiveness of our embedding for the retrieval system.

> NOTE: we could also add the section headings to the "clean_text" to add more signal to our embedding - however I'll leave this as an exercise to the user to try out.

1. 

## Create embeddings for the clauses

## Save clauses to an Azure AI Search Index

## Wire up Chainlit to test