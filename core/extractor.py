"""
Text Extractor Module
Extract raw text from PDF and DOCX resume files
"""

import io
from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF file using PyPDF2
    
    Args:
        file_bytes (bytes): PDF file content as bytes
        
    Returns:
        str: Extracted text from all pages
    """
    try:
        # BytesIO object banao for PDF reading
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PdfReader(pdf_file)
        
        # Sab pages se text extract karo
        text_parts = []
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        # Sab text ko combine karo with newlines
        full_text = "\n".join(text_parts)
        return full_text
        
    except Exception as e:
        # Agar error aaye to empty string return karo
        print(f"PDF extraction error: {str(e)}")
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text from DOCX file including tables
    
    Args:
        file_bytes (bytes): DOCX file content as bytes
        
    Returns:
        str: Extracted text from paragraphs and tables
    """
    try:
        # BytesIO object banao for DOCX reading
        docx_file = io.BytesIO(file_bytes)
        doc = Document(docx_file)
        
        text_parts = []
        
        # Paragraphs se text extract karo
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        # Tables se bhi text extract karo
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    text_parts.append(" | ".join(row_text))
        
        # Sab text ko combine karo
        full_text = "\n".join(text_parts)
        return full_text
        
    except Exception as e:
        # Agar error aaye to empty string return karo
        print(f"DOCX extraction error: {str(e)}")
        return ""


def extract_text(uploaded_file) -> dict:
    """
    Main extraction function - detects file type and extracts text
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        dict: {
            "filename": str,
            "raw_text": str,
            "char_count": int,
            "word_count": int,
            "extraction_success": bool,
            "error_message": str or None
        }
    """
    result = {
        "filename": uploaded_file.name,
        "raw_text": "",
        "char_count": 0,
        "word_count": 0,
        "extraction_success": False,
        "error_message": None
    }
    
    try:
        # File bytes read karo
        file_bytes = uploaded_file.read()
        
        # File extension se type detect karo
        filename_lower = uploaded_file.name.lower()
        
        if filename_lower.endswith('.pdf'):
            # PDF extraction
            text = extract_text_from_pdf(file_bytes)
        elif filename_lower.endswith('.docx'):
            # DOCX extraction
            text = extract_text_from_docx(file_bytes)
        else:
            # Unsupported file type
            result["error_message"] = f"Unsupported file type: {uploaded_file.name}"
            return result
        
        # Agar text successfully extract hua
        if text and text.strip():
            result["raw_text"] = text
            result["char_count"] = len(text)
            result["word_count"] = len(text.split())
            result["extraction_success"] = True
        else:
            result["error_message"] = "No text could be extracted from file"
            
    except Exception as e:
        # Koi bhi unexpected error handle karo
        result["error_message"] = f"Extraction failed: {str(e)}"
    
    return result


def extract_text_from_file_path(file_path: str) -> str:
    """
    Helper function to extract text from file path (for testing)
    
    Args:
        file_path (str): Path to PDF or DOCX file
        
    Returns:
        str: Extracted text
    """
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        if file_path.lower().endswith('.pdf'):
            return extract_text_from_pdf(file_bytes)
        elif file_path.lower().endswith('.docx'):
            return extract_text_from_docx(file_bytes)
        else:
            return ""
    except Exception as e:
        print(f"File reading error: {str(e)}")
        return ""
