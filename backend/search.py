import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ARXIV_NS = "http://www.w3.org/2005/Atom"


def search_arxiv(meaning: dict, max_results: int = 10) -> list[dict]:
    """
    Search ArXiv using extracted meaning dict from extract_paper_meaning().
    Returns a list of paper records with metadata and abstracts.
    """
    query = build_arxiv_query(meaning)
    print(f"ArXiv query: {query}")

    params = urllib.parse.urlencode({
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    })

    url = f"http://export.arxiv.org/api/query?{params}"
    with urllib.request.urlopen(url) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    papers = []

    for entry in root.findall(f"{{{ARXIV_NS}}}entry"):
        arxiv_id = entry.find(f"{{{ARXIV_NS}}}id").text.strip()

        papers.append({
            "arxiv_id":  arxiv_id,
            "title":     entry.find(f"{{{ARXIV_NS}}}title").text.strip(),
            "abstract":  entry.find(f"{{{ARXIV_NS}}}summary").text.strip(),
            "published": entry.find(f"{{{ARXIV_NS}}}published").text[:10],
            "authors":   [a.find(f"{{{ARXIV_NS}}}name").text for a in entry.findall(f"{{{ARXIV_NS}}}author")],
            "link":      f"https://arxiv.org/abs/{arxiv_id.split('/abs/')[-1]}",
            "pdf_link":  f"https://arxiv.org/pdf/{arxiv_id.split('/abs/')[-1]}",
        })

    return index_papers(papers)


def build_arxiv_query(meaning: dict) -> str:
    """Builds an ArXiv query from extracted meaning. No LLM needed."""
    concept_terms = " ".join(meaning["concepts"][:4])
    cats = " OR ".join(meaning["arxiv_categories"])
    return f"abs:{concept_terms} AND ({cats})"

def index_papers(papers: list[dict]) -> list[dict]:
    return [{**paper, "index": i} for i, paper in enumerate(papers)]


if __name__ == "__main__":
    # sample meaning dict as returned by extract_paper_meaning()
    sample_meaning = {
        "concepts": ["sparse attention", "transformer", "hierarchical", "complexity"],
        "arxiv_categories": ["cs.LG", "cs.CL"]
    }

    papers = search_arxiv(sample_meaning)
    for p in papers:
        print(f"{p['published']} | {p['title']}")
        print(f"  {p['link']}\n")

    print(papers)