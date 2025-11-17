"""
Utility Functions - The helpful tools everyone needs

This file contains all the general-purpose helper functions that don't belong
to any specific module. Think of it as the toolbox - PDF reading, text chunking,
file handling, etc.

These are the boring-but-essential functions that make everything else work smoothly.
"""

import os
import json
import PyPDF2
from typing import List, Dict, Any


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Pull text content out of a PDF file.
    
    PDFs are tricky - they're designed for viewing, not for extracting text.
    This uses PyPDF2 to read each page and combine all the text. Works well for
    most PDFs, but struggles with:
    - Scanned documents (images, not text)
    - Heavy formatting (tables, columns)
    - Password-protected files
    
    Args:
        pdf_path: Full path to the PDF file
    
    Returns:
        All text from the PDF as one big string, or empty string if it fails
    
    Example:
        text = extract_text_from_pdf("resume.pdf")
        if text:
            print(f"Got {len(text)} characters")
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


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Break long text into smaller, overlapping pieces.
    
    Why? AI models have token limits, and it's easier to search through small chunks
    than entire documents. We use overlapping chunks so we don't lose context when
    we split in the middle of an important section.
    
    For example, if a policy says "Employees with 2+ years tenure get 15 vacation days",
    we don't want "2+ years tenure" in one chunk and "15 vacation days" in another.
    
    Args:
        text: The long text to split up
        chunk_size: How many words per chunk (500 is a good balance)
        overlap: How many words to repeat between chunks (keeps context)
    
    Returns:
        List of text chunks, each roughly `chunk_size` words long
    
    Example:
        chunks = chunk_text("very long policy document...", chunk_size=500)
        print(f"Split into {len(chunks)} chunks")
    """
    words = text.split()
    chunks = []
    
    # Slide through the text with overlapping windows
    # If chunk_size=500 and overlap=50, we move 450 words each time
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        
        if chunk.strip():  # Don't add empty chunks
            chunks.append(chunk)
    
    return chunks


def load_skills_database(json_path: str = 'config/skills_database.json') -> List[str]:
    """
    Load a predefined list of technical skills from a JSON file.
    
    Note: We don't actually use this much anymore since we switched to AI-based
    skill extraction (which is smarter). But keeping it here in case we need
    a fallback or want to validate AI results.
    
    Args:
        json_path: Path to the skills JSON file
    
    Returns:
        Flat list of all skills from all categories
    
    Example JSON structure:
        {
            "programming": ["Python", "Java", "JavaScript"],
            "cloud": ["AWS", "Azure", "GCP"]
        }
    """
    try:
        if not os.path.exists(json_path):
            print(f"⚠️ Skills database not found at {json_path}")
            print(f"   (This is OK - we use AI for skill extraction now)")
            return []
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten all categories into one big list
        # So {"programming": ["Python"], "cloud": ["AWS"]} becomes ["Python", "AWS"]
        all_skills = []
        for category in data.values():
            if isinstance(category, list):
                all_skills.extend(category)
        
        # Remove duplicates (same skill might be in multiple categories)
        return list(set(all_skills))
    
    except Exception as e:
        print(f"❌ Error loading skills database: {e}")
        return []


def save_to_json(data: Any, filepath: str) -> bool:
    """
    Save Python data structures to a JSON file.
    
    Handles directory creation automatically and formats the JSON nicely
    (indented, human-readable). Useful for saving screening results, configs, etc.
    
    Args:
        data: Any JSON-serializable Python data (dict, list, etc.)
        filepath: Where to save the file
    
    Returns:
        True if save succeeded, False if it failed
    
    Example:
        results = {"candidates": [...]}
        save_to_json(results, "output/screening_results.json")
    """
    try:
        # Make sure the directory exists (e.g., if filepath is "output/results.json")
        directory = os.path.dirname(filepath)
        if directory:  # Only if there's actually a directory part
            os.makedirs(directory, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(
                data, 
                f, 
                indent=2,  # Pretty print with 2-space indentation
                ensure_ascii=False  # Allow unicode characters (names with accents, etc.)
            )
        
        return True
        
    except Exception as e:
        print(f"❌ Couldn't save to {filepath}: {e}")
        return False


def load_from_json(filepath: str) -> Any:
    """
    Load Python data from a JSON file.
    
    Safe wrapper around json.load() that handles missing files gracefully.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        The loaded data (dict, list, etc.) or None if file doesn't exist or fails
    
    Example:
        config = load_from_json("config/settings.json")
        if config:
            print(f"Loaded settings: {config}")
        else:
            print("No config found, using defaults")
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️ File not found: {filepath}")
            return None
            
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        print(f"   (File might be corrupted or not valid JSON)")
        return None


def ensure_directory(directory: str) -> None:
    """
    Make sure a directory exists, creating it if necessary.
    
    Convenience function so you don't have to remember the os.makedirs() syntax
    every time. Safe to call even if the directory already exists.
    
    Args:
        directory: Path to directory (e.g., "data/policies" or "output/reports")
    
    Example:
        ensure_directory("temp/resumes")
        # Now you can safely save files to temp/resumes/
    """
    os.makedirs(directory, exist_ok=True)


def format_phone_number(phone: str) -> str:
    """
    Clean up and format phone numbers consistently.
    
    Takes messy phone numbers and makes them readable. Optional function -
    not currently used, but handy to have.
    
    Args:
        phone: Raw phone number (e.g., "+1-234-567-8900" or "2345678900")
    
    Returns:
        Formatted phone number (e.g., "(234) 567-8900")
    
    Example:
        clean_phone = format_phone_number("+12345678900")
        # Returns: "(234) 567-8900"
    """
    # Remove all non-digit characters
    digits = ''.join(char for char in phone if char.isdigit())
    
    # Handle US numbers (10 digits)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    # Handle US numbers with country code (11 digits, starts with 1)
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    # Return as-is if we don't recognize the format
    else:
        return phone


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Shorten text to a maximum length, adding ellipsis.
    
    Useful for displaying long text in UI without overwhelming the user.
    Tries to break at word boundaries so we don't cut words in half.
    
    Args:
        text: The text to truncate
        max_length: Maximum characters to keep
        suffix: What to add at the end (default: "...")
    
    Returns:
        Truncated text with suffix
    
    Example:
        short = truncate_text("This is a very long resume description...", 20)
        # Returns: "This is a very lo..."
    """
    if len(text) <= max_length:
        return text
    
    # Try to break at a space to avoid cutting words
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + suffix


def validate_email(email: str) -> bool:
    """
    Quick sanity check if a string looks like a valid email.
    
    This is a simple check (has @ and a dot after it). For production,
    you'd want a more robust regex or validation library.
    
    Args:
        email: Email string to validate
    
    Returns:
        True if it looks like an email, False otherwise
    
    Example:
        if validate_email("john@example.com"):
            print("Looks good!")
    """
    if not email or '@' not in email:
        return False
    
    # Basic check: has @ and a domain with a dot
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    domain = parts[1]
    return '.' in domain and len(domain) > 3