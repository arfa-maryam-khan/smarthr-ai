"""
Resume Parser - Extract structured information from messy PDFs

Resumes come in every format imaginable. This parser handles the chaos by using
a combination of techniques:
- spaCy NER (finds names, organizations, etc.)
- Regex patterns (emails, phones, experience mentions)
- AI/LLM (skill extraction, name detection as fallback)

The goal: Turn a PDF into structured data we can actually work with.
"""

import re
import os
import json
from typing import List, Dict, Optional
from groq import Groq
from dotenv import load_dotenv
from modules.utils import extract_text_from_pdf

load_dotenv()


class ResumeParser:
    """
    Intelligent resume parser that extracts structured information from PDFs.
    
    Resumes are notoriously messy - different formats, layouts, styles. This parser
    uses multiple techniques (NLP, regex, AI) to reliably extract:
    - Name, email, phone
    - Skills (using AI to understand context)
    - Education background
    - Years of experience
    """
    
    def __init__(self):
        """
        Set up the parser with AI models and tools.
        
        We use:
        - spaCy: Fast NLP library for named entity recognition (finds names, etc.)
        - Groq LLM: For intelligent skill extraction (better than keyword matching)
        """
        print("🔄 Initializing Resume Parser...")
        print(f"🔑 Looking for API credentials...")
        
        # Try to find the Groq API key (needed for skill extraction)
        api_key = os.getenv("GROQ_API_KEY")
        
        if api_key:
            print(f"✅ Found API key in environment: {api_key[:10]}...{api_key[-5:]}")
        else:
            # If not in .env, check Streamlit secrets (for cloud deployment)
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
                    api_key = st.secrets['GROQ_API_KEY']
                    print(f"✅ Found API key in Streamlit secrets: {api_key[:10]}...{api_key[-5:]}")
            except:
                pass
        
        # Load spaCy for Named Entity Recognition
        # This helps us find names, dates, organizations, etc.
        print("🔄 Loading spaCy (for finding names and entities)...")
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy ready!")
        except:
            print("⚠️ spaCy not available (name extraction will be less accurate)")
            self.nlp = None
        
        # Set up Groq for AI-powered skill extraction
        if api_key:
            self.client = Groq(api_key=api_key)
            print("✅ Groq AI connected!")
        else:
            print("❌ No API key found - skill extraction will be limited")
            self.client = None
        
        print("✅ Resume Parser ready to process PDFs!")
    
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract raw text from a resume file.
        
        Supports PDF and plain text files. PDFs are the tricky ones - we use
        PyPDF2 to extract the text, though it sometimes struggles with fancy
        formatting or scanned documents.
        
        Args:
            file_path: Path to the resume file
        
        Returns:
            Raw text content of the resume
        """
        if file_path.endswith('.pdf'):
            return extract_text_from_pdf(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        return ""
    
    
    def extract_name(self, text: str) -> str:
        """
        Figure out the candidate's name from their resume.
        
        This is trickier than it sounds! Resumes have names in different places,
        sometimes with titles or credentials. We try multiple strategies:
        
        1. spaCy NER (looks for PERSON entities)
        2. Pattern matching (look for title-case words at the top)
        3. AI as last resort (ask Groq to extract it)
        
        Args:
            text: Full resume text
        
        Returns:
            Candidate's name, or "Unknown Candidate" if we can't figure it out
        """
        
        # Strategy 1: Use spaCy's Named Entity Recognition
        # This is trained to find person names in text
        if self.nlp:
            doc = self.nlp(text[:1500])  # Just check the first part
            for entity in doc.ents:
                if entity.label_ == "PERSON":
                    name = entity.text.strip()
                    # Make sure it's actually a name and not weird text
                    # (no emails, not too long, multiple words)
                    if '@' not in name and len(name.split()) in [2, 3, 4] and len(name) < 50:
                        return name
        
        # Strategy 2: Look for name patterns at the top of the resume
        # Most people put their name in the first few lines
        lines = text.split('\n')
        for line in lines[:15]:  # Check first 15 lines
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines with email addresses (not a name)
            if '@' in line:
                continue
            
            # Skip lines with lots of numbers (probably phone/address)
            if sum(char.isdigit() for char in line) > 3:
                continue
            
            # Skip common resume section headers
            skip_words = ['resume', 'cv', 'curriculum', 'vitae', 'profile', 'objective', 
                         'experience', 'education', 'skills', 'contact', 'summary']
            if any(word in line.lower() for word in skip_words):
                continue
            
            # Look for name patterns: 2-4 words, mostly letters, title case
            words = line.split()
            if 2 <= len(words) <= 4 and 5 < len(line) < 50:
                # Check if it's title case (John Smith, not john smith)
                if all(word[0].isupper() if word else False for word in words if len(word) > 1):
                    return line
        
        # Strategy 3: Ask AI to extract the name (last resort)
        if self.client:
            try:
                prompt = f"""Extract the candidate's full name from this resume text. Return ONLY the name, nothing else.

Resume excerpt:
{text[:800]}

Candidate name:"""
                
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,  # Be precise, not creative
                    max_tokens=50
                )
                
                name = response.choices[0].message.content.strip()
                
                # Validate the AI's answer (make sure it's reasonable)
                if name and '@' not in name and 3 < len(name) < 50 and len(name.split()) <= 4:
                    return name
            except:
                pass  # If AI fails, move to fallback
        
        # Give up and return a placeholder
        return "Unknown Candidate"
    
    
    def extract_email(self, text: str) -> Optional[str]:
        """
        Find the candidate's email address.
        
        Uses regex to match common email patterns. Pretty straightforward!
        
        Args:
            text: Full resume text
        
        Returns:
            Email address if found, None otherwise
        """
        # Standard email regex pattern
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        return emails[0] if emails else None
    
    
    def extract_phone(self, text: str) -> Optional[str]:
        """
        Find the candidate's phone number.
        
        Handles different formats:
        - (123) 456-7890
        - 123-456-7890
        - +1 123 456 7890
        
        Args:
            text: Full resume text
        
        Returns:
            Phone number if found, None otherwise
        """
        # Try multiple phone number patterns
        patterns = [
            r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\+\d{10,15}'  # International format
        ]
        
        for pattern in patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        
        return None
    
    
    def extract_education(self, text: str) -> List[str]:
        """
        Extract education information from the resume.
        
        Looks for sentences that mention degrees, universities, etc.
        Uses spaCy to understand sentence boundaries.
        
        Args:
            text: Full resume text
        
        Returns:
            List of education-related sentences (max 3)
        """
        # Common education keywords
        keywords = ['bachelor', 'master', 'phd', 'degree', 'university']
        
        if self.nlp:
            doc = self.nlp(text)
            education = []
            
            # Find sentences that mention education
            for sentence in doc.sents:
                if any(keyword in sentence.text.lower() for keyword in keywords):
                    education.append(sentence.text.strip())
            
            return education[:3]  # Return top 3 mentions
        
        return []
    
    
    def extract_experience_years(self, text: str) -> int:
        """
        Figure out how many years of experience the candidate has.
        
        Looks for phrases like:
        - "5 years of experience"
        - "3+ years in"
        
        Args:
            text: Full resume text
        
        Returns:
            Number of years (0 if not mentioned)
        """
        # Common patterns for mentioning experience
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+in',
        ]
        
        years_found = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            years_found.extend([int(year) for year in matches])
        
        # Return the highest number mentioned (if any)
        return max(years_found) if years_found else 0
    
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract technical skills from a resume using AI.
        
        This is way better than keyword matching because AI understands context.
        For example, if someone says "built scalable APIs with FastAPI", AI knows
        to extract both "API Development" and "FastAPI" as skills.
        
        Args:
            text: Full resume text
        
        Returns:
            List of technical skills
        """
        if not self.client:
            print("⚠️ Can't extract skills without Groq API")
            return []
        
        print(f"🔍 Using AI to extract skills from resume...")
        
        prompt = f"""Extract ALL technical skills from this resume.

Resume:
{text[:1500]}

Return ONLY a JSON array of skills like: ["Python", "AWS", "Docker"]

JSON Array:"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low creativity - we want accuracy
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up the response (sometimes wrapped in markdown)
            if '```json' in result:
                result = result.split('```json')[1].split('```')[0]
            elif '```' in result:
                result = result.split('```')[1].split('```')[0]
            
            # Make sure we have a proper JSON array
            if '[' in result and ']' in result:
                result = '[' + result.split('[', 1)[1]
                result = result.split(']')[0] + ']'
            
            skills = json.loads(result.strip())
            
            if isinstance(skills, list):
                print(f"✅ Found {len(skills)} skills: {skills}")
                return skills
            
            return []
            
        except Exception as e:
            print(f"⚠️ Skill extraction failed: {e}")
            return []
    
    
    def extract_skills_from_jd(self, jd_text: str) -> List[str]:
        """
        Extract required skills from a job description using AI.
        
        This figures out what technical skills the job actually requires.
        Again, AI is better than keyword matching because it understands
        context and variations in how requirements are written.
        
        Args:
            jd_text: Full job description text
        
        Returns:
            List of required technical skills
        """
        print(f"\n🔍 Using AI to extract required skills from JD ({len(jd_text)} chars)...")
        
        if not self.client:
            print("❌ Can't extract skills without Groq API")
            return []
        
        prompt = f"""Extract ALL technical skills and requirements from this job description.

Job Description:
{jd_text[:1500]}

Return ONLY a JSON array of technical skills: ["Python", "AWS", "Docker", "Machine Learning"]
Include programming languages, frameworks, tools, technologies, and methodologies.

JSON Array:"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            print(f"✅ AI responded: {result[:100]}...")
            
            # Clean up markdown wrapping
            if '```json' in result:
                result = result.split('```json')[1].split('```')[0]
            elif '```' in result:
                result = result.split('```')[1].split('```')[0]
            
            # Extract just the JSON array part
            if '[' in result and ']' in result:
                result = '[' + result.split('[', 1)[1]
                result = result.split(']')[0] + ']'
            
            skills = json.loads(result.strip())
            
            if isinstance(skills, list) and skills:
                # Remove duplicates and clean up
                skills = list(set([skill.strip() for skill in skills if skill.strip()]))
                print(f"✅ Found {len(skills)} required skills: {skills}")
                return skills
            
            print("⚠️ AI returned empty or invalid skills list")
            return []
            
        except json.JSONDecodeError as e:
            print(f"❌ Couldn't parse AI response as JSON: {e}")
            return []
        except Exception as e:
            print(f"❌ Skill extraction error: {e}")
            return []
    
    
    def parse(self, file_path: str) -> Optional[Dict]:
        """
        Main parsing function - extract all info from a resume file.
        
        This orchestrates all the extraction methods to turn a messy PDF
        into structured, usable data.
        
        Args:
            file_path: Path to the resume PDF
        
        Returns:
            Dictionary with extracted information:
                - filename: Original filename
                - name: Candidate's name
                - email: Contact email
                - phone: Phone number
                - skills: List of technical skills
                - education: Education background
                - experience_years: Years of experience
                - raw_text: Full extracted text
            
            Returns None if parsing fails
        """
        try:
            # First, get the text out of the PDF
            text = self.extract_text(file_path)
            
            if not text.strip():
                print(f"⚠️ No text found in {file_path} (might be a scanned image?)")
                return None
            
            # Extract skills using AI
            skills = self.extract_skills_from_text(text)
            
            # Package everything up
            return {
                'filename': os.path.basename(file_path),
                'name': self.extract_name(text),
                'email': self.extract_email(text),
                'phone': self.extract_phone(text),
                'skills': skills,
                'education': self.extract_education(text),
                'experience_years': self.extract_experience_years(text),
                'raw_text': text  # Keep the full text for semantic analysis
            }
            
        except Exception as e:
            print(f"❌ Failed to parse {file_path}: {e}")
            return None