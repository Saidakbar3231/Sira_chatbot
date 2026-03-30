import os
from pathlib import Path


def load_documents(data_dir: str = "data") -> list[dict]:
    """Load all PDF, TXT, and DOCX files from data_dir.
    Returns list of {"source": filename, "text": content} dicts.
    """
    docs = []
    data_path = Path(data_dir)
    if not data_path.exists():
        data_path.mkdir(parents=True)
        return docs

    for file in data_path.iterdir():
        if file.suffix.lower() == ".txt":
            docs.extend(_load_txt(file))
        elif file.suffix.lower() == ".pdf":
            docs.extend(_load_pdf(file))
        elif file.suffix.lower() == ".docx":
            docs.extend(_load_docx(file))

    return docs


def _load_txt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    chunks = _split_text(text)
    return [{"source": path.name, "text": chunk} for chunk in chunks]


def _load_pdf(path: Path) -> list[dict]:
    try:
        import pypdf
        reader = pypdf.PdfReader(str(path))
        full_text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()
        chunks = _split_text(full_text)
        return [{"source": path.name, "text": chunk} for chunk in chunks]
    except ImportError:
        raise RuntimeError("Install pypdf to load PDF files: pip install pypdf")


def _load_docx(path: Path) -> list[dict]:
    try:
        from docx import Document
        doc = Document(str(path))
        full_text = "\n".join(p.text for p in doc.paragraphs).strip()
        chunks = _split_text(full_text)
        return [{"source": path.name, "text": chunk} for chunk in chunks]
    except ImportError:
        raise RuntimeError("Install python-docx to load DOCX files: pip install python-docx")


def _split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return [c for c in chunks if c.strip()]
