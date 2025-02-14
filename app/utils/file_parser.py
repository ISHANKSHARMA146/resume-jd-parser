from io import BytesIO
import logging
from PyPDF2 import PdfReader
from docx import Document
import re

logger = logging.getLogger(__name__)

def parse_pdf_or_docx(file_buffer: BytesIO, filename: str) -> str:
    """
    Determines the file type (PDF or DOCX) and extracts text accordingly.
    :param file_buffer: File buffer of the uploaded file.
    :param filename: Name of the uploaded file.
    :return: Extracted text content as a string, including hyperlinks.
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

def parse_pdf(file_buffer: BytesIO) -> str:
    """
    Extracts text from a PDF file, including hyperlinks.
    :param file_buffer: File buffer of the uploaded PDF file.
    :return: Extracted text content as a string, including hyperlinks.
    """
    try:
        logger.info("Parsing PDF file")
        reader = PdfReader(file_buffer)
        text = ""
        hyperlinks = []

        
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text

            
            if "/Annots" in page:
                annotations = page["/Annots"]
                for annotation in annotations:
                    if "/A" in annotation and "/URI" in annotation["/A"]:
                        hyperlinks.append(annotation["/A"]["/URI"])

        
        hyperlinks_text = '\n'.join(hyperlinks)
        return text.strip() + '\n' + hyperlinks_text

    except Exception as e:
        logger.error(f"Error reading PDF file: {str(e)}", exc_info=True)
        raise

def parse_docx(file_buffer: BytesIO) -> str:
    """
    Extracts text from a DOCX file, including hyperlinks.
    :param file_buffer: File buffer of the uploaded DOCX file.
    :return: Extracted text content as a string, including hyperlinks.
    """
    try:
        logger.info("Parsing DOCX file")
        doc = Document(file_buffer)
        text = ""

        
        for paragraph in doc.paragraphs:
            text += paragraph.text + '\n'

        
        hyperlinks = extract_hyperlinks_from_docx(file_buffer)
        return text.strip() + '\n' + hyperlinks

    except Exception as e:
        logger.error(f"Error reading DOCX file: {str(e)}", exc_info=True)
        raise

def extract_hyperlinks_from_docx(file_buffer: BytesIO) -> str:
    """
    Extracts hyperlinks from a DOCX file by scanning for <a> tags in the document's HTML.
    :param file_buffer: The file buffer of the DOCX file.
    :return: A string containing all hyperlinks found in the document.
    """
    try:
        from zipfile import ZipFile
        import xml.etree.ElementTree as ET

        
        with ZipFile(file_buffer) as docx_zip:
            relationships = docx_zip.read('word/_rels/document.xml.rels')
            tree = ET.ElementTree(ET.fromstring(relationships))
            root = tree.getroot()

            hyperlinks = []
            
            for element in root.iter():
                if element.tag.endswith('Relationship') and 'hyperlink' in element.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}Type', ''):
                    url = element.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}Target')
                    if url:
                        hyperlinks.append(url)

            return '\n'.join(hyperlinks)

    except Exception as e:
        logger.error(f"Error extracting hyperlinks from DOCX file: {str(e)}", exc_info=True)
        raise
