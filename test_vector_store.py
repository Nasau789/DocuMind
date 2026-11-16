
from vector_store import store_document, search_document

sample_pages = [
    """
    The Solar System consists of the Sun and all objects
    that orbit around it.

    There are eight planets in our Solar System.
    Earth is the third planet from the Sun.
    """,

    """
    Jupiter is the largest planet in our Solar System.

    The Sun is a star at the centre of the Solar System.
    It provides light and heat to the planets.
    """
]

document_id = "test_document_v2"

print("Storing document...")

number_of_chunks = store_document(
    sample_pages,
    document_id
)

print(f"Stored {number_of_chunks} chunks!")

print("\nSearching document...")

results = search_document(
    "Which is the largest planet?",
    document_id
)

for result in results:

    print("\n--------------------")
    print("Page:", result["page"])
    print("Distance:", round(result["distance"], 4))
    print("Text:", result["text"])
