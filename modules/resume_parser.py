"""
AI-Powered Resume Parser using Groq LLM
Most accurate approach - understands context, handles any format
"""
import os
import json
import re
from typing import Dict, List, Optional
from groq import Groq
from dotenv import load_dotenv
from modules.utils import extract_text_from_pdf

load_dotenv()

class ResumeParser:
    """LLM-powered resume parser for maximum accuracy"""
    
    def __init__(self):
        """Initialize with Groq"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY not found!")
        
        self.client = Groq(api_key=api_key)
        print("✅ AI Resume Parser initialized!")
    
    def extract_text(self, file_path: str) -> str:
        """Extract raw text from file"""
        if file_path.endswith('.pdf'):
            return extract_text_from_pdf(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        return ""
    
    def parse_with_llm(self, text: str) -> Dict:
        """
        Use LLM to intelligently parse resume
        Most accurate method - understands context and variations
        """
        prompt = f"""You are an expert resume parser. Extract structured information from this resume.

Resume Text:
{text[:3000]}

Extract the following in valid JSON format:
{{
  "name": "candidate's full name",
  "email": "email address",
  "phone": "phone number",
  "skills": ["list", "of", "technical", "skills"],
  "experience_years": number_of_years,
  "education": ["degree and institution"]
}}

Rules:
- Only extract information that's explicitly in the resume
- For skills: include programming languages, frameworks, tools, technologies
- For experience_years: estimate from work history
- Return ONLY the JSON object, no other text

JSON:"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            # Sometimes LLM wraps in ```json
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            parsed = json.loads(result_text)
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            # Fallback to basic extraction
            return self._fallback_parse(text)
        except Exception as e:
            print(f"⚠️ LLM parsing error: {e}")
            return self._fallback_parse(text)
    
    def _fallback_parse(self, text: str) -> Dict:
        """Fallback regex-based parsing if LLM fails"""
        return {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'skills': [],
            'experience_years': self._extract_experience(text),
            'education': []
        }
    
    def _extract_name(self, text: str) -> str:
        """Simple name extraction"""
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) <= 4 and len(line) > 5:
                return line
        return "Unknown"
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email with regex"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        return emails[0] if emails else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone with regex"""
        pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(pattern, text)
        return phones[0] if phones else None
    
    def _extract_experience(self, text: str) -> int:
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+in'
        ]
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([int(m) for m in matches])
        return max(years) if years else 0
    
    def parse(self, file_path: str) -> Optional[Dict]:
        """
        Main parsing method - uses LLM for accuracy
        
        Returns:
            Dictionary with parsed resume data
        """
        try:
            # Step 1: Extract raw text (PyPDF2 - just file I/O)
            text = self.extract_text(file_path)
            
            if not text.strip():
                print(f"⚠️ No text extracted from {file_path}")
                return None
            
            # Step 2: LLM parses and structures (AI-powered!)
            parsed = self.parse_with_llm(text)
            
            # Add metadata
            parsed['filename'] = os.path.basename(file_path)
            parsed['raw_text'] = text
            
            print(f"✅ Parsed: {parsed.get('name', 'Unknown')} - {len(parsed.get('skills', []))} skills")
            
            return parsed
            
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return None
    
    def extract_skills_from_jd(self, jd_text: str) -> List[str]:
        """
        Extract required skills from job description using LLM
        More accurate than keyword matching
        """
        prompt = f"""Extract the required technical skills from this job description.

Job Description:
{jd_text}

Return ONLY a JSON array of skills (programming languages, frameworks, tools, technologies).
Example: ["Python", "Machine Learning", "AWS", "Docker"]

JSON Array:"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean response
            if '```json' in result:
                result = result.split('```json')[1].split('```')[0]
            elif '```' in result:
                result = result.split('```')[1].split('```')[0]
            
            skills = json.loads(result)
            return skills if isinstance(skills, list) else []
            
        except Exception as e:
            print(f"⚠️ Skill extraction error: {e}")
            return []