
import hashlib
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ==================================
# 1. LOAD LOCAL EMBEDDING MODEL
# ==================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully!")


# ==================================
# 2. INITIALIZE CHROMADB
# ==================================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="pdf_documents_local",
    metadata={"hnsw:space": "cosine"}
)


# ==================================
# 3. TEXT CHUNKING
# ==================================

def split_page_text(
    text,
    chunk_size=2000,
    overlap=250
):

    chunks = []
    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        if end < len(text):

            boundary = text.rfind(
                "\n",
                start + int(chunk_size * 0.7),
                end
            )

            if boundary == -1:

                boundary = text.rfind(
                    " ",
                    start + int(chunk_size * 0.7),
                    end
                )

            if boundary != -1:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return chunks


# ==================================
# 4. GENERATE LOCAL EMBEDDINGS
# ==================================

def generate_embeddings(texts):

    embeddings = embedding_model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True
    )

    return embeddings.tolist()


# ==================================
# 5. STORE DOCUMENT
# ==================================

def store_document(
    pages,
    document_id,
    document_name="Document"
):

    # Avoid unnecessary re-embedding
    if document_exists(document_id):
        print(f"{document_name} is already indexed.")
        return 0

    all_chunks = []
    all_metadatas = []

    for page_number, page_text in enumerate(
        pages,
        start=1
    ):

        page_chunks = split_page_text(page_text)

        for chunk in page_chunks:

            all_chunks.append(chunk)

            all_metadatas.append({
                "document_id": document_id,
                "document_name": document_name,
                "page_number": page_number
            })

    if not all_chunks:
        raise ValueError("No text chunks found in document.")

    print(f"Generating embeddings for {len(all_chunks)} chunks...")

    embeddings = generate_embeddings(all_chunks)

    ids = [
        hashlib.sha256(
            f"{document_id}_{i}".encode()
        ).hexdigest()
        for i in range(len(all_chunks))
    ]

    collection.add(
        ids=ids,
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=all_metadatas
    )

    print(f"Stored {len(all_chunks)} chunks successfully.")

    return len(all_chunks)


# ==================================
# 6. SEARCH DOCUMENTS
# ==================================

def search_document(
    question,
    document_ids,
    n_results=6,
    distance_threshold=0.50
):

    if not document_ids:
        return []

    question_embedding = generate_embeddings(
        [question]
    )[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results,
        where={
            "document_id": {
                "$in": document_ids
            }
        },
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_chunks = []

    if not results["documents"]:
        return retrieved_chunks

    for i, document in enumerate(results["documents"][0]):

        distance = results["distances"][0][i]

        if distance > distance_threshold:
            continue

        metadata = results["metadatas"][0][i]

        retrieved_chunks.append({
            "text": document,
            "page": metadata["page_number"],
            "document_name": metadata["document_name"],
            "distance": distance
        })

    return retrieved_chunks


# ==================================
# 7. LIST STORED DOCUMENTS
# ==================================

def list_documents():

    results = collection.get(
        include=["metadatas"]
    )

    documents = {}

    for metadata in results["metadatas"]:

        doc_id = metadata["document_id"]

        if doc_id not in documents:

            documents[doc_id] = {
                "name": metadata["document_name"],
                "chunks": 0
            }

        documents[doc_id]["chunks"] += 1

    return documents


# ==================================
# 8. CHECK DOCUMENT EXISTENCE
# ==================================

def document_exists(document_id):

    results = collection.get(
        where={"document_id": document_id},
        limit=1
    )

    return len(results["ids"]) > 0


# ==================================
# 9. DELETE DOCUMENT
# ==================================

def delete_document(document_id):

    collection.delete(
        where={"document_id": document_id}
    )

    return True
