"""
Built-in tool implementations: OCR, HTML Reader, PDF Reader.

Each tool function takes an input dict and returns an output dict.
These can be invoked by agents based on DB tool configuration.
"""
from __future__ import annotations

import io
import logging
from typing import Any

logger = logging.getLogger(__name__)

BUILTIN_TOOLS: dict[str, dict[str, Any]] = {
    "pdf_reader": {
        "name": "pdf_reader",
        "description": "Extracts text content from a PDF file.",
        "tool_type": "builtin",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the PDF file"},
                "file_data": {"type": "string", "description": "Base64 encoded PDF data (alternative to file_path)"},
            },
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "page_count": {"type": "integer"},
            },
        },
    },
    "html_reader": {
        "name": "html_reader",
        "description": "Fetches and extracts text content from a web page URL.",
        "tool_type": "builtin",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL of the web page to read"},
            },
            "required": ["url"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "title": {"type": "string"},
            },
        },
    },
    "ocr_reader": {
        "name": "ocr_reader",
        "description": "Extracts text from an image using OCR (Tesseract).",
        "tool_type": "builtin",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the image file"},
                "file_data": {"type": "string", "description": "Base64 encoded image data"},
                "language": {"type": "string", "default": "eng", "description": "Tesseract language code"},
            },
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
        },
    },
}


def execute_pdf_reader(params: dict[str, Any]) -> dict[str, Any]:
    import PyPDF2

    file_path = params.get("file_path")
    file_data = params.get("file_data")

    if file_data:
        import base64
        raw = base64.b64decode(file_data)
        reader = PyPDF2.PdfReader(io.BytesIO(raw))
    elif file_path:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
    else:
        return {"text": "", "page_count": 0, "error": "No file_path or file_data provided"}

    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    return {
        "text": "\n".join(pages_text),
        "page_count": len(reader.pages),
    }


def execute_html_reader(params: dict[str, Any]) -> dict[str, Any]:
    import requests
    from bs4 import BeautifulSoup

    url = params.get("url", "")
    if not url:
        return {"text": "", "title": "", "error": "No URL provided"}

    try:
        response = requests.get(url, timeout=30, headers={"User-Agent": "QurultaiBot/1.0"})
        response.raise_for_status()
    except requests.RequestException as e:
        return {"text": "", "title": "", "error": str(e)}

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    title = soup.title.string if soup.title else ""
    text = soup.get_text(separator="\n", strip=True)

    return {"text": text, "title": title or ""}


def execute_ocr_reader(params: dict[str, Any]) -> dict[str, Any]:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return {"text": "", "error": "pytesseract or Pillow not installed"}

    file_path = params.get("file_path")
    file_data = params.get("file_data")
    language = params.get("language", "eng")

    try:
        if file_data:
            import base64
            raw = base64.b64decode(file_data)
            image = Image.open(io.BytesIO(raw))
        elif file_path:
            image = Image.open(file_path)
        else:
            return {"text": "", "error": "No file_path or file_data provided"}

        text = pytesseract.image_to_string(image, lang=language)
        return {"text": text}
    except Exception as e:
        return {"text": "", "error": str(e)}


_EXECUTORS: dict[str, Any] = {
    "pdf_reader": execute_pdf_reader,
    "html_reader": execute_html_reader,
    "ocr_reader": execute_ocr_reader,
}


def execute_builtin_tool(tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
    executor = _EXECUTORS.get(tool_name)
    if executor is None:
        return {"error": f"Unknown built-in tool: {tool_name}"}
    try:
        return executor(params)
    except Exception as e:
        logger.exception("Error executing tool %s", tool_name)
        return {"error": str(e)}


def get_builtin_tool_definitions() -> list[dict[str, Any]]:
    return list(BUILTIN_TOOLS.values())
