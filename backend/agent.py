from ollama import chat
from ollama import ChatResponse

SYSTEM_PROMPT = """
You are a helpful assistant that summarizes PDFs.

Return a clean Markdown summary with:

1. High-level idea (2-3 sentences)
2. Bullet list of main points
3. Optional key insights section if useful
"""

MODEL = "gemma:latest"  # or "llama3.1:8b", etc.
OLLAMA_URL = "http://localhost:11434/api/chat"

def describe_text(text: str) -> str:
    response = chat(
        model=MODEL,
        messages=[
            {
                'role': 'system',
                'content': SYSTEM_PROMPT
            },
            {
                'role': 'user',
                'content': f"Summarize the following passage:\n\n{text}"
            }
        ]
    )
    
    return response['message']['content']