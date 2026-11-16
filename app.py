
import streamlit as st
import os
import hashlib

from pathlib import Path
from io import BytesIO
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

from vector_store import (
    store_document,
    search_document,
    list_documents,
    document_exists,
    delete_document
)


# ==========================================
# 1. CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="DocuMind | AI PDF Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# 2. CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
    color: #F1F5F9;
}

[data-testid="stSidebar"] {
    background-color: #151B26;
    border-right: 1px solid #293244;
}

.main-title {
    font-size: 38px;
    font-weight: 750;
    letter-spacing: -1.5px;
    color: #F8FAFC;
    margin-bottom: 5px;
}

.subtitle {
    color: #94A3B8;
    font-size: 15px;
    margin-bottom: 25px;
}

.metric-card {
    background: #171F2D;
    border: 1px solid #293548;
    padding: 20px;
    border-radius: 14px;
}

.metric-label {
    color: #94A3B8;
    font-size: 13px;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #F8FAFC;
    margin-top: 5px;
}

.welcome-card {
    background: #171F2D;
    border: 1px solid #293548;
    border-radius: 16px;
    padding: 28px;
    margin-top: 25px;
}

.welcome-title {
    font-size: 23px;
    font-weight: 700;
    color: #F8FAFC;
}

.welcome-text {
    color: #94A3B8;
    line-height: 1.7;
}

.section-heading {
    font-size: 17px;
    font-weight: 650;
    margin-top: 20px;
    margin-bottom: 12px;
    color: #E2E8F0;
}

.source-card {
    background: #171F2D;
    border-left: 3px solid #60A5FA;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}

.stChatMessage {
    border-radius: 12px;
}

button[kind="primary"] {
    background-color: #2563EB;
    border-radius: 8px;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. LOAD GEMINI
# ==========================================

load_dotenv(Path(__file__).parent / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found. Check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


# ==========================================
# 4. SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_doc_ids" not in st.session_state:
    st.session_state.active_doc_ids = []

if "selection_signature" not in st.session_state:
    st.session_state.selection_signature = None


# ==========================================
# 5. SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## 📚 DocuMind")

    st.caption("Your intelligent document workspace")

    st.divider()

    st.markdown("### Upload documents")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:

        for uploaded_file in uploaded_files:

            file_bytes = uploaded_file.getvalue()

            pdf_id = hashlib.sha256(
                file_bytes
            ).hexdigest()

            if document_exists(pdf_id):

                st.info(
                    f"Already indexed: {uploaded_file.name}"
                )

            else:

                try:

                    with st.spinner(
                        f"Processing {uploaded_file.name}..."
                    ):

                        reader = PdfReader(
                            BytesIO(file_bytes)
                        )

                        pages = [
                            page.extract_text() or ""
                            for page in reader.pages
                        ]

                        if not any(
                            page.strip() for page in pages
                        ):

                            st.warning(
                                f"No selectable text found: "
                                f"{uploaded_file.name}"
                            )
                            continue

                        number_of_chunks = store_document(
                            pages,
                            pdf_id,
                            uploaded_file.name
                        )

                    st.success(
                        f"Indexed {uploaded_file.name}: "
                        f"{number_of_chunks} chunks"
                    )

                except Exception as e:

                    st.error(
                        f"Could not process "
                        f"{uploaded_file.name}: {e}"
                    )

    st.divider()

    st.markdown("### Your document library")

    documents = list_documents()

    selected_doc_ids = []

    if documents:

        for doc_id, info in documents.items():

            with st.container():

                col1, col2 = st.columns([5, 1])

                with col1:

                    selected = st.checkbox(
                        info["name"],
                        value=True,
                        key=f"select_{doc_id}"
                    )

                    if selected:
                        selected_doc_ids.append(doc_id)

                    st.caption(
                        f"📄 {info['chunks']} indexed chunks"
                    )

                with col2:

                    if st.button(
                        "🗑️",
                        key=f"delete_{doc_id}",
                        help="Delete document"
                    ):

                        delete_document(doc_id)

                        st.session_state.messages = []

                        st.rerun()

    else:

        st.info(
            "Your library is empty. Upload a PDF to get started."
        )

    st.divider()

    st.caption(
        f"📁 {len(documents)} documents in your library"
    )

    st.caption("Local embeddings • ChromaDB • Gemini")


# ==========================================
# 6. DOCUMENT SELECTION
# ==========================================

selection_signature = tuple(
    sorted(selected_doc_ids)
)

if selection_signature != st.session_state.selection_signature:

    st.session_state.messages = []

    st.session_state.selection_signature = selection_signature

st.session_state.active_doc_ids = selected_doc_ids


# ==========================================
# 7. MAIN HEADER
# ==========================================

st.markdown(
    '<div class="main-title">DocuMind</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Chat with your documents using Retrieval-Augmented Generation.'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# 8. DASHBOARD METRICS
# ==========================================

documents = list_documents()

total_documents = len(documents)

total_chunks = sum(
    info["chunks"]
    for info in documents.values()
)

selected_count = len(selected_doc_ids)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total documents</div>
            <div class="metric-value">{total_documents}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Indexed chunks</div>
            <div class="metric-value">{total_chunks}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Selected documents</div>
            <div class="metric-value">{selected_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# 9. WELCOME SCREEN
# ==========================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="welcome-card">

            <div class="welcome-title">
                👋 Welcome to your document workspace
            </div>

            <p class="welcome-text">
                Upload your PDFs and start asking questions.
                DocuMind retrieves relevant passages from your
                documents and uses Gemini to generate answers.
            </p>

            <p class="welcome-text">
                You can query multiple documents simultaneously,
                compare information and inspect the source passages
                behind each answer.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-heading">Try asking</div>',
        unsafe_allow_html=True
    )

    examples = [
        "Summarize the main concepts in my documents.",
        "Explain the most important topics.",
        "Compare the information across my PDFs."
    ]

    example_cols = st.columns(3)

    for i, example in enumerate(examples):

        with example_cols[i]:

            if st.button(
                example,
                key=f"example_{i}",
                use_container_width=True
            ):

                st.session_state.pending_prompt = example
                st.rerun()


# ==========================================
# 10. DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            with st.expander("📖 View sources"):

                for source in message["sources"]:

                    st.markdown(
                        f"**{source['document_name']} "
                        f"— Page {source['page']}**"
                    )

                    st.caption(source["text"])


# ==========================================
# 11. CLEAR CONVERSATION
# ==========================================

if st.session_state.messages:

    if st.button("🧹 Clear conversation"):

        st.session_state.messages = []

        st.rerun()


# ==========================================
# 12. USER INPUT
# ==========================================

prompt = st.chat_input(
    "Ask anything about your selected documents..."
)

if "pending_prompt" in st.session_state:

    prompt = st.session_state.pending_prompt

    del st.session_state.pending_prompt


# ==========================================
# 13. RAG QUESTION ANSWERING
# ==========================================

if prompt:

    if not st.session_state.active_doc_ids:

        st.warning(
            "Please upload and select at least one document."
        )

    else:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            placeholder = st.empty()

            answer = ""

            try:

                # ------------------------------
                # RETRIEVAL
                # ------------------------------

                with st.spinner(
                    "Searching your documents..."
                ):

                    relevant_chunks = search_document(
                        prompt,
                        st.session_state.active_doc_ids,
                        n_results=6,
                        distance_threshold=0.50
                    )

                if not relevant_chunks:

                    warning = (
                        "I couldn't find sufficiently relevant "
                        "information in the selected documents. "
                        "Try rephrasing your question."
                    )

                    placeholder.warning(warning)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": warning,
                        "sources": []
                    })

                else:

                    # ------------------------------
                    # PREPARE CONTEXT
                    # ------------------------------

                    retrieved_context = ""

                    for chunk in relevant_chunks:

                        retrieved_context += f"""
Document: {chunk['document_name']}
Page: {chunk['page']}

Content:
{chunk['text']}

--------------------
"""

                    # ------------------------------
                    # CONVERSATION HISTORY
                    # ------------------------------

                    previous_messages = (
                        st.session_state.messages[:-1]
                    )[-8:]

                    conversation_history = ""

                    for message in previous_messages:

                        conversation_history += (
                            f"{message['role']}: "
                            f"{message['content']}\n"
                        )

                    # ------------------------------
                    # GEMINI PROMPT
                    # ------------------------------

                    document_context = f"""
You are DocuMind, an AI document assistant.

Answer the user's question using the retrieved
information from the selected PDF documents.

You may compare information across documents
when the retrieved context supports it.

Maintain conversational context for follow-up questions.

If the retrieved information does not contain
the answer, clearly say that the documents
do not provide enough information.

Do not invent facts, citations or page references.

Mention document names and page numbers when relevant.

RETRIEVED DOCUMENT CONTEXT:

{retrieved_context}

PREVIOUS CONVERSATION:

{conversation_history}

CURRENT QUESTION:

{prompt}
"""

                    # ------------------------------
                    # GENERATE ANSWER
                    # ------------------------------

                    placeholder.markdown("Thinking...")

                    stream = client.interactions.create(
                        model="gemini-3.5-flash-lite",
                        input=document_context,
                        stream=True
                    )

                    for event in stream:

                        if (
                            event.event_type == "step.delta"
                            and hasattr(event.delta, "text")
                        ):

                            answer += event.delta.text

                            placeholder.markdown(answer)

                    if answer:

                        sources = [
                            {
                                "document_name": chunk["document_name"],
                                "page": chunk["page"],
                                "text": chunk["text"]
                            }
                            for chunk in relevant_chunks
                        ]

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })

                        with st.expander("📖 View sources"):

                            for source in sources:

                                st.markdown(
                                    f"**{source['document_name']} "
                                    f"— Page {source['page']}**"
                                )

                                st.caption(source["text"])

                    else:

                        placeholder.warning(
                            "Gemini returned an empty response."
                        )

            except Exception as e:

                placeholder.error(
                    f"Something went wrong: {e}"
                )
