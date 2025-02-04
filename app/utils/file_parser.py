import logging
import re
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO

logger = logging.getLogger(__name__)

def parse_pdf_or_docx(file_buffer: BytesIO, filename: str):
    """
    Determines the file type (PDF or DOCX) and extracts text accordingly.
    :param file_buffer: File buffer of the uploaded file.
    :param filename: Name of the uploaded file.
    :return: Extracted text content as a string.
    """
    try:
        if filename.lower().endswith(".pdf"):
            return parse_pdf(file_buffer)
        elif filename.lower().endswith(".docx"):
            return parse_docx(file_buffer)
        else:
            raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
    except Exception as e:
        logger.error(f"Error parsing file '{filename}': {str(e)}", exc_info=True)
        raise

def parse_pdf(file_buffer: BytesIO):
    """
    Extracts text from a PDF file.
    :param file_buffer: File buffer of the uploaded PDF file.
    :return: Extracted text content as a string.
    """
    try:
        logger.info("Parsing PDF file")
        reader = PdfReader(file_buffer)

        # Combine text from all pages
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

        # Clean and normalize the text
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error reading PDF file: {str(e)}", exc_info=True)
        raise

def parse_docx(file_buffer: BytesIO):
    """
    Extracts text from a DOCX file.
    :param file_buffer: File buffer of the uploaded DOCX file.
    :return: Extracted text content as a string.
    """
    try:
        logger.info("Parsing DOCX file")
        doc = Document(file_buffer)

        # Combine text from all paragraphs
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)

        # Clean and normalize the text
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error reading DOCX file: {str(e)}", exc_info=True)
        raise

def clean_text(text: str) -> str:
    """
    Cleans and normalizes text to improve parsing results.
    :param text: Raw extracted text.
    :return: Cleaned and normalized text.
    """
    # Remove excessive whitespace and normalize spaces
    text = re.sub(r'\s+', ' ', text)

    # Normalize line breaks for better readability
    return text.strip()
