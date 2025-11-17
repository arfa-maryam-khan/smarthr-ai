"""
Utility functions for SmartHR AI
"""
import os
import json
import PyPDF2
from typing import List, Dict, Any

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Input text
        chunk_size: Number of words per chunk
        overlap: Number of overlapping words
        
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks

def load_skills_database(json_path: str = 'config/skills_database.json') -> List[str]:
    """
    Load skills database from JSON
    
    Args:
        json_path: Path to skills JSON file
        
    Returns:
        List of all skills
    """
    try:
        if not os.path.exists(json_path):
            print(f"⚠️ Skills database not found at {json_path}")
            return []
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten all skills into one list
        all_skills = []
        for category in data.values():
            if isinstance(category, list):
                all_skills.extend(category)
        
        return list(set(all_skills))  # Remove duplicates
        
    except Exception as e:
        print(f"❌ Error loading skills database: {e}")
        return []

def save_to_json(data: Any, filepath: str) -> bool:
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        filepath: Output file path
        
    Returns:
        True if successful
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error saving to {filepath}: {e}")
        return False

def load_from_json(filepath: str) -> Any:
    """
    Load data from JSON file
    
    Args:
        filepath: Input file path
        
    Returns:
        Loaded data or None
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"❌ Error loading from {filepath}: {e}")
        return None

def ensure_directory(directory: str) -> None:
    """Create directory if it doesn't exist"""
    os.makedirs(directory, exist_ok=True)