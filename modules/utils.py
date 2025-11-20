"""
This file contains all the general-purpose helper functions that don't belong
to any specific module such as PDF reading, text chunking,
file handling, etc.
"""

import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Pull text content out of a PDF file. This uses PyPDF2 to read each page and combine all the text.
    
    Args:
        pdf_path: Full path to the PDF file
    
    Returns:
        All text from the PDF as one big string, or empty string if it fails
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Go through each page and extract text
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:  # Some pages might be blank
                    text += page_text + "\n"
            
            return text.strip()
            
    except Exception as e:
        print(f"❌ Couldn't read {pdf_path}: {e}")
        print(f"   (This might be a scanned PDF or corrupted file)")
        return ""
