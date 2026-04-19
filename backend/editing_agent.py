from google import genai
from google.genai import types
import json
import os

from config import API_KEY, GEMINI_MODEL

client = genai.Client(api_key=API_KEY)


SECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type":        {"type": "string", "enum": ["paper", "blurb"]},
                    "paper_index": {"type": "integer", "description": "Only set when type is paper"},
                    "text":        {"type": "string",  "description": "Only set when type is blurb"},
                },
                "required": ["type"]
            }
        }
    },
    "required": ["sections"]
}


def build_editor_prompt(papers: list[dict], groups: dict) -> str:
    paper_lookup = {p["index"]: p for p in papers}

    lines = ["PAPERS:"]
    for idx in groups["reading_order"]:
        p = paper_lookup[idx]
        lines.append(f"[{idx}] {p['title']}\n{p['abstract']}\n")

    lines.append("GROUPS:")
    for g in groups["groups"]:
        indices = ", ".join(str(i) for i in g["paper_indices"])
        lines.append(f"- {g['label']} (papers {indices}): {g['rationale']}")

    lines.append(f"\nREADING ORDER: {groups['reading_order']}")

    return "\n".join(lines)


def run_editor(papers: list[dict], groups: dict) -> dict:
    """
    Takes indexed papers + grouping output, returns a structured document
    of interleaved paper and blurb sections ready for pdf_builder.
    """
    prompt = build_editor_prompt(papers, groups)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction="""You are an academic editor composing a reading guide from a set of papers.
You will receive papers in reading order, their thematic groups, and must produce a structured document.

Rules:
- Follow the reading order exactly for paper sections
- Write a blurb before every paper to introduce it
- Write a blurb after every paper to transition to the next, or conclude if it's the last
- Blurbs should be 1-2 paragraphs, written for an academic audience
- Intro blurb sets up the whole collection
- Conclusion blurb ties everything together
- Reference papers by their title, not their index
- Each blurb will occupy a full page — write with that in mind, be substantive""",
            response_mime_type="application/json",
            response_schema=SECTION_SCHEMA
        ),
        contents=prompt
    )

    return json.loads(response.text)

def validate_editor_output(result: dict, reading_order: list[int]) -> dict:
    """Ensure every paper in reading_order appears exactly once, in order."""
    paper_sections = [s for s in result["sections"] if s["type"] == "paper"]
    found_order = [s["paper_index"] for s in paper_sections]

    if found_order != reading_order:
        raise ValueError(f"Paper order mismatch.\nExpected: {reading_order}\nGot:      {found_order}")

    return result


if __name__ == "__main__":
    sample_papers = [
        {"index": 0, "title": "Attention Is All You Need",                  "abstract": "We propose the Transformer..."},
        {"index": 1, "title": "Sparse Transformers",                         "abstract": "We present sparse attention patterns..."},
        {"index": 2, "title": "BERT: Pre-training of Deep Bidirectional Transformers", "abstract": "We introduce BERT..."},
    ]

    sample_groups = {
        "reading_order": [0, 2, 1],
        "groups": [
            {"label": "Foundational Transformers", "paper_indices": [0, 2], "rationale": "Core architecture papers"},
            {"label": "Efficient Attention",        "paper_indices": [1],    "rationale": "Optimising the attention mechanism"},
        ]
    }

    result = run_editor(sample_papers, sample_groups)
    print(json.dumps(result, indent=2))