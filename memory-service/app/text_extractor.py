"""
Text Extractor - Extract text from PDF, DOCX, TXT files
Centralized in memory-service for unified context management.
"""

from loguru import logger


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file content"""
    try:
        from docx import Document
        import io
        doc = Document(io.BytesIO(file_content))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting DOCX text: {e}")
        return ""


def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file content"""
    try:
        # Try UTF-8 first, then fallback to latin-1
        try:
            return file_content.decode('utf-8').strip()
        except UnicodeDecodeError:
            return file_content.decode('latin-1').strip()
    except Exception as e:
        logger.error(f"Error extracting TXT text: {e}")
        return ""


def extract_text_from_file(file_content: bytes, file_type: str) -> str:
    """
    Extract text from file based on type.

    Args:
        file_content: Raw file bytes
        file_type: File extension (pdf, docx, txt)

    Returns:
        Extracted text or empty string on error
    """
    file_type = file_type.lower().strip('.')

    if file_type == "pdf":
        return extract_text_from_pdf(file_content)
    elif file_type == "docx":
        return extract_text_from_docx(file_content)
    elif file_type == "txt":
        return extract_text_from_txt(file_content)
    else:
        logger.warning(f"Unsupported file type: {file_type}")
        return ""
