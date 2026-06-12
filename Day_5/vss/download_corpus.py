"""
download_corpus.py - Download 200+ arXiv ML/AI papers as PDFs
Uses the arXiv API to search for papers and download them into ./corpus/
"""

import os
import sys
import time
import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from tqdm import tqdm

# ── Config ──────────────────────────────────────────────────────────────────
CORPUS_DIR = Path(__file__).parent / "corpus"
METADATA_FILE = Path(__file__).parent / "corpus_metadata.json"
TARGET_PAPERS = 210
BATCH_SIZE = 50  # arXiv API max results per request
ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_DELAY = 3  # seconds between API calls (arXiv policy)

# arXiv categories for ML/AI
SEARCH_QUERIES = [
    "cat:cs.LG",       # Machine Learning
    "cat:cs.AI",       # Artificial Intelligence
    "cat:cs.CL",       # Computation and Language (NLP)
    "cat:cs.CV",       # Computer Vision
]

# ── Helpers ─────────────────────────────────────────────────────────────────

def parse_arxiv_response(xml_text: str) -> list[dict]:
    """Parse arXiv Atom XML response into a list of paper metadata dicts."""
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    root = ET.fromstring(xml_text)
    papers = []

    for entry in root.findall("atom:entry", ns):
        # Extract arXiv ID from the id URL
        id_url = entry.find("atom:id", ns).text.strip()
        arxiv_id = id_url.split("/abs/")[-1]

        # Remove version suffix for clean ID
        clean_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

        title = entry.find("atom:title", ns).text.strip().replace("\n", " ")

        # Published date → year
        published = entry.find("atom:published", ns).text.strip()
        year = published[:4]

        # Authors
        authors = []
        for author_el in entry.findall("atom:author", ns):
            name = author_el.find("atom:name", ns).text.strip()
            authors.append(name)

        # Categories
        categories = []
        for cat_el in entry.findall("atom:category", ns):
            categories.append(cat_el.get("term"))

        # PDF link
        pdf_link = None
        for link_el in entry.findall("atom:link", ns):
            if link_el.get("title") == "pdf":
                pdf_link = link_el.get("href")
                break

        if pdf_link and not pdf_link.endswith(".pdf"):
            pdf_link += ".pdf"

        # Summary/abstract
        summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")

        papers.append({
            "arxiv_id": clean_id,
            "title": title,
            "authors": authors,
            "year": year,
            "categories": categories,
            "pdf_url": pdf_link,
            "abstract": summary[:500],
        })

    return papers


def search_arxiv(query: str, start: int = 0, max_results: int = 50) -> list[dict]:
    """Query the arXiv API and return parsed paper metadata."""
    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    resp = requests.get(ARXIV_API, params=params, timeout=30)
    resp.raise_for_status()
    return parse_arxiv_response(resp.text)


def download_pdf(url: str, save_path: Path) -> bool:
    """Download a PDF file. Returns True on success."""
    try:
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()

        # Verify it's actually a PDF
        content_type = resp.headers.get("content-type", "")
        if "pdf" not in content_type and not resp.content[:5] == b"%PDF-":
            return False

        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        # Verify file size (skip tiny files that are probably error pages)
        if save_path.stat().st_size < 10_000:
            save_path.unlink()
            return False

        return True
    except Exception as e:
        print(f"  ⚠ Download failed: {e}")
        if save_path.exists():
            save_path.unlink()
        return False


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)

    # Check if we already have enough papers
    existing_pdfs = list(CORPUS_DIR.glob("*.pdf"))
    if len(existing_pdfs) >= TARGET_PAPERS:
        print(f"✅ Already have {len(existing_pdfs)} PDFs in {CORPUS_DIR}")
        print("   To re-download, delete the corpus/ directory first.")
        return

    all_metadata = []
    downloaded_ids = set()

    # Load existing metadata if present
    if METADATA_FILE.exists():
        with open(METADATA_FILE, "r") as f:
            existing = json.load(f)
            for p in existing:
                downloaded_ids.add(p["arxiv_id"])
            all_metadata.extend(existing)

    # Also track already-downloaded PDFs
    for pdf in existing_pdfs:
        downloaded_ids.add(pdf.stem)

    print(f"📚 Target: {TARGET_PAPERS} papers | Already have: {len(downloaded_ids)}")
    print(f"📁 Saving to: {CORPUS_DIR}\n")

    remaining = TARGET_PAPERS - len(downloaded_ids)
    papers_per_query = (remaining // len(SEARCH_QUERIES)) + 20  # extra buffer

    for query in SEARCH_QUERIES:
        if len(downloaded_ids) >= TARGET_PAPERS:
            break

        print(f"\n🔍 Searching: {query}")
        batch_start = 0

        while len(downloaded_ids) < TARGET_PAPERS and batch_start < papers_per_query:
            time.sleep(ARXIV_DELAY)

            papers = search_arxiv(query, start=batch_start, max_results=BATCH_SIZE)
            if not papers:
                print(f"  No more results for {query}")
                break

            for paper in tqdm(papers, desc=f"  Downloading ({query})", leave=False):
                if len(downloaded_ids) >= TARGET_PAPERS:
                    break

                if paper["arxiv_id"] in downloaded_ids:
                    continue

                if not paper["pdf_url"]:
                    continue

                # Sanitize filename
                safe_id = paper["arxiv_id"].replace("/", "_").replace(".", "_")
                pdf_path = CORPUS_DIR / f"{safe_id}.pdf"

                if pdf_path.exists():
                    downloaded_ids.add(paper["arxiv_id"])
                    continue

                success = download_pdf(paper["pdf_url"], pdf_path)
                if success:
                    downloaded_ids.add(paper["arxiv_id"])
                    paper["local_filename"] = pdf_path.name
                    all_metadata.append(paper)

                time.sleep(1)  # Be polite

            batch_start += BATCH_SIZE
            time.sleep(ARXIV_DELAY)

    # Save metadata
    with open(METADATA_FILE, "w") as f:
        json.dump(all_metadata, f, indent=2)

    final_count = len(list(CORPUS_DIR.glob("*.pdf")))
    print(f"\n{'='*60}")
    print(f"✅ Download complete!")
    print(f"   Total PDFs: {final_count}")
    print(f"   Metadata saved: {METADATA_FILE}")
    print(f"   Corpus directory: {CORPUS_DIR}")
    print(f"{'='*60}")

    if final_count < TARGET_PAPERS:
        print(f"\n⚠ Only got {final_count}/{TARGET_PAPERS} papers.")
        print("  Run the script again to continue downloading.")


if __name__ == "__main__":
    main()
