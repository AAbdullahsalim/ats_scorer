"""
DOCX text and block extraction using python-docx.
Extracts paragraphs with font metadata for section classification.
"""

import io
from pathlib import Path
from typing import Union

from docx import Document

from .text_cleaner import sanitize_unicode


def _get_stream(file_source: Union[str, Path, io.BytesIO, bytes]) -> io.BytesIO:
    """Convert any file source to a BytesIO stream."""
    if isinstance(file_source, bytes):
        return io.BytesIO(file_source)
    elif isinstance(file_source, (str, Path)):
        path = Path(file_source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_source}")
        with open(path, "rb") as f:
            return io.BytesIO(f.read())
    elif isinstance(file_source, io.BytesIO):
        file_source.seek(0)
        return file_source
    else:
        raise ValueError(f"Unsupported file source type: {type(file_source)}")


def extract_blocks_from_docx(
    file_source: Union[str, Path, io.BytesIO, bytes]
) -> list[dict]:
    """
    Extract text blocks from a DOCX with font metadata.

    Returns a list of dicts with keys:
        text, is_bold, font_size, is_heading_style, bbox, y0
    """
    stream = _get_stream(file_source)
    doc = Document(stream)
    blocks = []

    for idx, paragraph in enumerate(doc.paragraphs):
        text = sanitize_unicode(paragraph.text.strip())
        if not text:
            continue

        style_name = str(paragraph.style.name).lower() if paragraph.style else ""
        is_heading_style = "heading" in style_name

        is_bold = (
            any(run.bold for run in paragraph.runs if run.bold is not None)
            or is_heading_style
        )

        font_size = 12.0
        for run in paragraph.runs:
            if run.font and run.font.size:
                font_size = max(font_size, float(run.font.size.pt))

        blocks.append({
            "text": text,
            "is_bold": is_bold,
            "font_size": font_size,
            "is_heading_style": is_heading_style,
            "bbox": (0, idx * 20, 500, (idx + 1) * 20),
            "x0": 0, "y0": idx * 20,
            "x1": 500, "y1": (idx + 1) * 20,
            "page_num": 1,
        })

    return blocks
