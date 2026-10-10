"""Extract paragraph-level responses from documents.

Prebuilt layout returns paragraphs/lines, not semantic survey responses.
This demo treats each paragraph as a candidate response; real forms need
question/answer mapping, filtering and human validation.
"""
from pathlib import Path


def extract_txt(path: Path) -> list[dict]:
    """One nonempty line per synthetic survey response."""
    return [{"source": path.name, "page": None, "feedback": x.strip()}
            for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def extract_pdf(path: Path, endpoint: str, key: str) -> list[dict]:
    """Azure Document Intelligence prebuilt-layout extraction (paid Azure call)."""
    try:
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.core.credentials import AzureKeyCredential
    except ImportError as exc:
        raise RuntimeError("Install optional Azure packages: pip install -e '.[azure]'") from exc
    client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    with path.open("rb") as document:
        result = client.begin_analyze_document("prebuilt-layout", document).result()
    rows = []
    if result.paragraphs:
        for para in result.paragraphs:
            content = (para.content or "").strip()
            if not content:
                continue
            page = None
            if para.bounding_regions:
                page = para.bounding_regions[0].page_number
            rows.append({"source": path.name, "page": page, "feedback": content})
    else:
        for page in result.pages:
            for line in page.lines or []:
                if line.content.strip():
                    rows.append({"source": path.name, "page": page.page_number,
                                 "feedback": line.content.strip()})
    return rows
