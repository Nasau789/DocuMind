# DocuMind — AI-Powered PDF Assistant

**Chat with your PDFs using Retrieval-Augmented Generation (RAG).**

DocuMind is an AI-powered PDF assistant that allows users to upload multiple PDF documents and ask questions about their contents using natural language.

It uses locally generated text embeddings, ChromaDB for semantic search, and Google's Gemini model to generate context-aware answers based on the uploaded documents.

## Features

- **Multiple PDF uploads:** Upload and work with multiple PDF documents.
- **Retrieval-Augmented Generation (RAG):** Retrieve relevant passages before generating answers.
- **Local embeddings:** Generate text embeddings using Sentence Transformers.
- **Semantic search:** Find relevant information using ChromaDB.
- **Source references:** View the document name and page number associated with retrieved passages.
- **Persistent document library:** Keep indexed documents available between application sessions.
- **Document management:** Select and delete indexed documents.
- **Conversation history:** Ask follow-up questions within the same conversation.
- **Relevance filtering:** Filter out retrieved passages that are not sufficiently relevant.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web interface |
| Google Gemini | AI-powered answer generation |
| Sentence Transformers | Local text embedding generation |
| all-MiniLM-L6-v2 | Embedding model |
| ChromaDB | Vector database |
| PyPDF | PDF text extraction |
| python-dotenv | Environment variable management |

## How It Works

DocuMind follows a Retrieval-Augmented Generation (RAG) pipeline.

1. **PDF Upload:** The user uploads one or more PDF documents.
2. **Text Extraction:** PyPDF extracts text from each document page.
3. **Text Chunking:** Extracted text is divided into smaller overlapping chunks.
4. **Embedding Generation:** Sentence Transformers converts each chunk into a numerical vector.
5. **Vector Storage:** ChromaDB stores the embeddings along with document and page metadata.
6. **Semantic Retrieval:** When the user asks a question, the application converts the question into an embedding and searches for relevant chunks.
7. **Answer Generation:** Retrieved passages are provided as context to Gemini, which generates an answer grounded in the available document content.

## Project Structure

```text
ai-pdf-assistant/
│
├── app.py                  # Streamlit application
├── vector_store.py         # Embeddings, vector storage and retrieval
├── requirements.txt        # Python dependencies
├── .env                    # API key configuration
├── .gitignore              # Files excluded from Git
│
└── chroma_db/              # Persistent ChromaDB storage
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/DocuMind.git
cd DocuMind
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Get an API key from [Google AI Studio](https://aistudio.google.com/).

### 5. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

## Usage

1. Launch DocuMind.
2. Upload one or more PDF documents.
3. Wait for the documents to be processed and indexed.
4. Select the documents you want to query.
5. Enter a question in the chat interface.
6. Review the generated answer and its supporting document passages.

## Technical Highlights

- **Local inference for embeddings:** Document and query embeddings are generated locally using Sentence Transformers.
- **Cosine similarity search:** ChromaDB uses cosine distance to retrieve semantically relevant passages.
- **Overlapping text chunks:** Chunk overlap helps preserve context across text boundaries.
- **Metadata-based retrieval:** Each chunk retains its document identifier, document name, and page number.
- **Persistent vector storage:** Indexed document data is stored locally using ChromaDB.
- **Context-grounded generation:** Gemini receives retrieved document passages rather than relying solely on general model knowledge.

## Limitations

- PDF extraction quality depends on the document's structure and whether its text is extractable.
- Scanned PDFs may require OCR support.
- Answer quality depends on the relevance and quality of retrieved passages.
- The local vector database is stored on the machine running the application.
- Gemini API usage is subject to Google's model availability, quotas, and rate limits.

## Future Improvements

- OCR support for scanned PDFs.
- Support for additional document formats.
- Improved retrieval using hybrid search.
- Reranking for more relevant context selection.
- Exporting conversations and generated answers.
- Cloud deployment with persistent storage.
- User authentication and document-level access controls.

## Author

Developed as a personal project to explore Large Language Models, semantic search, vector databases, and Retrieval-Augmented Generation.

**Built with Python, Streamlit, Ch