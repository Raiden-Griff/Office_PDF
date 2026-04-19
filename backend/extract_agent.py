from google import genai
from google.genai import types
import json
import os


from config import API_KEY, GEMINI_MODEL

client = genai.Client(api_key=API_KEY)

ARXIV_CATEGORIES = [
    "cs.AI", "cs.CL", "cs.CV", "cs.LG", "cs.RO", "cs.NE", "cs.IR",
    "stat.ML", "stat.TH", "stat.AP",
    "math.OC", "math.ST", "math.PR",
    "quant-ph", "physics.comp-ph",
    "q-bio.NC", "q-bio.GN", "q-bio.QM",
    "econ.GN", "econ.EM",
]

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "thesis":       {"type": "string", "description": "One sentence: the core claim or contribution"},
        "domain":       {"type": "string", "description": "Primary field + subfield (e.g. Machine Learning / Reinforcement Learning)"},
        "concepts":     {"type": "array", "items": {"type": "string"}, "description": "5-8 key concepts or terms"},
        "methodology":  {"type": "string", "description": "One sentence: how they did it (study type, techniques, data)"},
        "search_query": {"type": "string", "description": "Dense 2-3 sentence description optimised for semantic similarity search"},
        "arxiv_categories": {
            "type": "array",
            "items": {"type": "string", "enum": ARXIV_CATEGORIES},
            "description": "1-3 most relevant ArXiv category codes"
        },
    },
    "required": ["thesis", "domain", "concepts", "methodology", "search_query", "arxiv_categories"]
}


def extract_paper_meaning(text: str) -> dict:
    """Extracts structured meaning from paper text. Returns a meaning dict."""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction="You extract structured meaning from academic paper text.",
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA
        ),
        contents=f"Extract meaning from this paper text:\n\n{text[:4000]}"
    )
    return json.loads(response.text)


def build_arxiv_query(meaning: dict) -> str:
    """Builds an ArXiv query from extracted meaning. No LLM needed."""
    concept_terms = " ".join(meaning["concepts"][:4])
    cats = " OR ".join(meaning["arxiv_categories"])
    return f"abs:{concept_terms} AND ({cats})"


if __name__ == "__main__":
    sample = """
    We propose a novel attention mechanism that reduces transformer complexity from O(n²) 
    to O(n log n) while maintaining performance on NLP benchmarks. Our method, Sparse Hierarchical 
    Attention (SHA), segments input sequences into hierarchical blocks and computes attention 
    within and across blocks selectively. Experiments on GLUE, SQuAD, and long-document tasks 
    show SHA matches full attention within 0.3% while cutting memory use by 60% on sequences 
    over 4096 tokens.
    """

    meaning = extract_paper_meaning(sample)
    print(json.dumps(meaning, indent=2))

    query = build_arxiv_query(meaning)
    print(f"\nArXiv query: {query}")