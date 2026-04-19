from google import genai
from google.genai import types
import json
import os

from config import API_KEY, GEMINI_MODEL

client = genai.Client(api_key=API_KEY)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "groups": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label":         {"type": "string", "description": "Short name for this group"},
                    "rationale":     {"type": "string", "description": "One sentence: why these papers belong together"},
                    "paper_indices": {"type": "array", "items": {"type": "integer"}},
                },
                "required": ["label", "rationale", "paper_indices"]
            }
        },
        "reading_order": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "All paper indices in recommended reading order, foundational first"
        },
    },
    "required": ["groups", "reading_order"]
}


def build_grouping_prompt(papers: list[dict]) -> str:
    lines = []
    for p in papers:
        lines.append(f"[{p['index']}] {p['title']}\n{p['abstract']}\n")
    return "\n".join(lines)


def group_papers(papers: list[dict]) -> dict:
    """
    Takes indexed papers from search_arxiv(), returns groups and reading order.
    """
    prompt = build_grouping_prompt(papers)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction="""You are a research assistant grouping academic papers by theme.
Group the papers into 2-5 meaningful clusters based on their abstracts.
Order papers in each group from most foundational to most advanced.
The reading_order should be a global ordering across all papers — foundational and broad papers first, specific and advanced last.""",
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA
        ),
        contents=prompt
    )

    return json.loads(response.text)


if __name__ == "__main__":
    # sample — replace with output from search_arxiv()
    sample_papers = [
        {"index": 0, "title": "Attention Is All You Need", "abstract": "We propose the Transformer..."},
        {"index": 1, "title": "BERT: Pre-training of Deep Bidirectional Transformers", "abstract": "We introduce BERT..."},
        {"index": 2, "title": "Sparse Transformers", "abstract": "We present sparse attention patterns..."},
    ]

    result = group_papers(sample_papers)
    print(json.dumps(result, indent=2))