"""
Document Parsing: PDF, DOCX, and OCR support
"""
import os
from typing import Tuple

import PyPDF2


def parse_pdf(file_path: str) -> str:
    """Extract text from PDF"""
    try:
        text = []
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return "\n".join(text)
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"


def parse_docx(file_path: str) -> str:
    """Extract text from DOCX"""
    try:
        from docx import Document

        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"Error parsing DOCX: {str(e)}"


def parse_text(file_path: str) -> str:
    """Extract text from plain text file"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error parsing text: {str(e)}"


def auto_parse_document(file_path: str) -> Tuple[str, str]:
    """
    Automatically parse document based on extension
    Returns: (text_content, file_type)
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return parse_pdf(file_path), "pdf"
    elif ext in [".docx", ".doc"]:
        return parse_docx(file_path), "docx"
    elif ext in [".txt", ".md"]:
        return parse_text(file_path), "text"
    else:
        return f"Unsupported file type: {ext}", "unknown"


# For future OCR support
def parse_image_ocr(file_path: str) -> str:
    """Extract text from image using OCR (Tesseract)"""
    try:
        # import pytesseract
        # from PIL import Image
        # image = Image.open(file_path)
        # return pytesseract.image_to_string(image)
        return "OCR not configured yet"
    except Exception as e:
        return f"Error with OCR: {str(e)}"
