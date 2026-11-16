print("PDF reader started!")

from pypdf import PdfReader

# Load PDF
reader = PdfReader("sample.pdf")

# Extract text
for page_number, page in enumerate(reader.pages):
    text = page.extract_text()

    print(f"--- Page {page_number + 1} ---")
    print(text)
