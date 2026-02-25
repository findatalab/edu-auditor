import re

import arxiv
import requests

from tqdm import tqdm



def fetch_papers(keyword, max_results=10):
    """
    Fetches paper information from Arxiv
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=keyword,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    papers = []
    for result in tqdm(client.results(search), desc="Fetching papers...", total=max_results ):
        papers.append({
            'title': result.title,
            'authors': [a.name for a in result.authors],
            'summary': result.summary,
            'pdf_url': next(filter(lambda item: item.title == "pdf", result.links)).href
        })
    return papers


def download_pdf(url: str, save_path: str) -> None:
    """Download a PDF from URL and save to local path."""
    with requests.get(url, stream=True) as response:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

if __name__ == "__main__":
    save_path = "C:\\main\\GitHub\\documentReviewSystem\\data"
    papers = fetch_papers("machine learning", 10)
    for paper in tqdm(papers, desc="Downloading papers..."):
        download_pdf(paper["pdf_url"], save_path=save_path+f"\\{re.sub(r":", r"_", paper["title"])}.pdf")
