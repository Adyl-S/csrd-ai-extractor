import fitz  # PyMuPDF
from typing import List, Dict

class PDFParser:
    def __init__(self, path: str):
        self.doc = fitz.open(path)
        self.total_pages = len(self.doc)

    def get_relevant_context(self, keywords: List[str], max_pages=25) -> str:
        """
        Scans document for keywords and returns the text of the most relevant pages.
        """
        page_scores = {}
        
        # Scoring phase
        for page_num, page in enumerate(self.doc):
            text = page.get_text().lower()
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                page_scores[page_num] = score

        # Sort by relevance
        top_pages = sorted(page_scores.items(), key=lambda x: x[1], reverse=True)[:max_pages]
        top_pages.sort(key=lambda x: x[0]) # Re-sort by page order for logical flow

        # Extraction phase
        context = []
        for page_num, _ in top_pages:
            text = self.doc[page_num].get_text()
            context.append(f"--- PAGE {page_num + 1} ---\n{text}")

        return "\n\n".join(context)