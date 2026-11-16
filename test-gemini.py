
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).parent / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise SystemExit("API key not found")

client = genai.Client(api_key=api_key)

print("Testing Gemini Flash Lite...")

start = time.perf_counter()

try:
    response = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input="Reply with only the word HELLO."
    )

    print("Response:", response.output_text)
    print("Time:", round(time.perf_counter() - start, 2), "seconds")

except Exception as e:
    print("Error:", repr(e))
    print("Time:", round(time.perf_counter() - start, 2), "seconds")
