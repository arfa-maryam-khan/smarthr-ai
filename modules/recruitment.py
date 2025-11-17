"""
Recruitment Engine - AI-powered candidate screening and interview prep

This module handles two main jobs:
1. Screen resumes against job descriptions (find the best matches)
2. Generate personalized interview questions for shortlisted candidates

Think of it as your AI recruiting assistant that never gets tired of reading resumes!
"""

import os
import json
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util
from groq import Groq
from dotenv import load_dotenv
from modules.resume_parser import ResumeParser

load_dotenv()


class RecruitmentEngine:
    """
    AI-powered recruitment assistant for screening candidates and preparing interviews.
    
    This engine combines multiple AI techniques:
    - Semantic understanding (Sentence-BERT) to see if resumes match the role
    - Skill extraction (LLM) to check if candidates have required skills
    - Intelligent scoring (weighted formula) that balances experience and skills
    """
    
    def __init__(self):
        """
        Fire up all the AI models we need for recruitment.
        
        This loads:
        1. Resume parser (extracts info from PDFs)
        2. Sentence-BERT (understands semantic similarity)
        3. Groq LLM (generates interview questions)
        """
        print("🔄 Initializing Recruitment Engine...")
        
        # Load the resume parser (handles PDF reading and info extraction)
        print("📖 Loading Resume Parser...")
        self.parser = ResumeParser()
        
        # Load Sentence-BERT for semantic matching
        # This lets us compare "how similar" a resume is to a JD, not just keyword matching
        print("🧠 Loading Sentence-BERT (the brain that compares resumes to job descriptions)...")
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Sentence-BERT ready!")
        except Exception as e:
            print(f"❌ Couldn't load Sentence-BERT: {e}")
            raise
        
        # Set up Groq for generating interview questions
        print("🤖 Connecting to Groq AI...")
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ Can't find GROQ_API_KEY in environment!")
            raise ValueError("Missing GROQ_API_KEY - add it to your .env file")
        
        self.client = Groq(api_key=api_key)
        print("✅ Groq AI connected!")
        
        print("✅ Recruitment Engine ready to screen candidates!\n")
    
    
    def screen_candidates(self, resume_paths: List[str], job_description: str, threshold: float = 50.0):
        """
        Screen a batch of candidates against a job description and rank them.
        
        This is the core screening logic. For each resume, we:
        1. Extract skills using AI (not just keyword matching)
        2. Calculate semantic similarity (does their experience fit?)
        3. Check skill matches (do they have what we need?)
        4. Combine scores with a weighted formula (60% experience, 40% skills)
        5. Decide if they're shortlisted based on threshold
        
        Why 60/40 weighting? Overall experience and fit matters more than just
        having every checkbox skill. Someone with 5/7 skills but great experience
        often beats someone with 7/7 skills but poor fit.
        
        Args:
            resume_paths: List of paths to resume PDF files
            job_description: The full JD text
            threshold: Minimum score to be shortlisted (default 50%)
        
        Returns:
            List of candidate results, sorted by score (highest first)
        """
        
        def log(msg):
            """Helper to print screening progress"""
            print(msg)
        
        log(f"\n{'='*60}")
        log(f"🎯 SCREENING {len(resume_paths)} CANDIDATES")
        log(f"{'='*60}")
        
        results = []
        
        # STEP 1: Figure out what skills the job actually requires
        # We use AI to extract these, not a hardcoded list
        log(f"\n📋 STEP 1: Extracting required skills from job description...")
        required_skills = self.parser.extract_skills_from_jd(job_description)
        log(f"✅ Found {len(required_skills)} required skills: {required_skills}")
        
        if not required_skills:
            log("⚠️ WARNING: Couldn't find any skills in the JD!")
            log("   (This might mean the JD is too vague, or AI extraction failed)")
        
        # STEP 2: Convert the JD into a semantic embedding
        # This captures the "meaning" of the role in a 384-dimensional vector
        log(f"\n🧠 STEP 2: Creating semantic profile of the job...")
        jd_embedding = self.model.encode(job_description, convert_to_tensor=True)
        log(f"✅ Job profile created (vector dimension: {jd_embedding.shape})")
        
        # STEP 3: Process each resume
        for i, resume_path in enumerate(resume_paths, 1):
            log(f"\n{'='*60}")
            log(f"📄 PROCESSING RESUME {i}/{len(resume_paths)}: {os.path.basename(resume_path)}")
            log(f"{'='*60}")
            
            try:
                # Parse the resume PDF and extract information
                log(f"📖 Reading and parsing resume...")
                candidate_data = self.parser.parse(resume_path)
                
                if not candidate_data:
                    log(f"❌ Couldn't extract info from this resume - skipping")
                    continue
                
                log(f"✅ Candidate: {candidate_data['name']}")
                log(f"✅ Contact: {candidate_data['email']}")
                log(f"✅ Their skills: {candidate_data['skills']}")
                
                # Convert resume into semantic embedding (same format as JD)
                log(f"\n🧠 Creating semantic profile of candidate...")
                # Use first 2000 chars to avoid token limits
                resume_text = candidate_data['raw_text'][:2000]
                resume_embedding = self.model.encode(resume_text, convert_to_tensor=True)
                log(f"✅ Candidate profile created")
                
                # Calculate how similar the resume is to the JD (semantic match)
                # This captures overall fit: does their experience align with the role?
                log(f"\n📊 Measuring how well they match the role overall...")
                similarity = util.cos_sim(resume_embedding, jd_embedding).item()
                similarity_score = round(similarity * 100, 2)
                log(f"✅ Semantic similarity: {similarity_score}%")
                log(f"   (This measures overall experience fit, not just keywords)")
                
                # Check which specific skills they have
                # This is more black-and-white: do they have the tech stack we need?
                log(f"\n🔍 Checking specific skill matches...")
                matched_skills = [
                    skill for skill in required_skills 
                    if skill in candidate_data['skills']
                ]
                matched_count = len(matched_skills)
                required_count = len(required_skills)
                
                log(f"   Required skills: {required_skills}")
                log(f"   Candidate has: {candidate_data['skills']}")
                log(f"   Matched: {matched_skills}")
                
                # Calculate skill match percentage
                if required_count > 0:
                    skill_match_rate = round((matched_count / required_count) * 100, 2)
                else:
                    skill_match_rate = 0  # No required skills = can't calculate
                
                log(f"✅ Skill match rate: {matched_count}/{required_count} = {skill_match_rate}%")
                
                # Calculate final score using weighted formula
                # 60% semantic (overall fit) + 40% skills (specific requirements)
                log(f"\n🎯 Calculating final score...")
                final_score = round((similarity_score * 0.6) + (skill_match_rate * 0.4), 2)
                log(f"   Formula: (semantic × 0.6) + (skills × 0.4)")
                log(f"   Result: ({similarity_score} × 0.6) + ({skill_match_rate} × 0.4) = {final_score}")
                
                # Decide if they're shortlisted
                shortlisted = final_score >= threshold
                status = '✅ SHORTLISTED' if shortlisted else '❌ NOT SHORTLISTED'
                log(f"   {status} (threshold: {threshold}%)")
                
                # Package up all the info for this candidate
                result = {
                    'name': candidate_data['name'],
                    'email': candidate_data['email'],
                    'phone': candidate_data['phone'],
                    'experience_years': candidate_data['experience_years'],
                    'similarity_score': similarity_score,
                    'skill_match_rate': skill_match_rate,
                    'matched_skills': matched_skills,
                    'matched_skills_count': matched_count,
                    'required_skills_count': required_count,
                    'final_score': final_score,
                    'shortlisted': shortlisted,
                    'raw_text': candidate_data['raw_text']
                }
                
                results.append(result)
                
            except Exception as e:
                log(f"\n❌ ERROR processing this resume: {str(e)}")
                import traceback
                log(traceback.format_exc())
                continue
        
        # Sort candidates by score (best first)
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        log(f"\n{'='*60}")
        log(f"✅ SCREENING COMPLETE!")
        log(f"   📊 Total processed: {len(results)}")
        log(f"   🎯 Shortlisted: {sum(1 for r in results if r['shortlisted'])}")
        log(f"{'='*60}\n")
        
        return results
    
    
    def generate_interview_questions(
        self, 
        job_description: str, 
        candidate_info: Dict, 
        num_questions: int = 5
    ) -> List[Dict]:
        """
        Generate personalized interview questions for a specific candidate.
        
        This creates technical questions tailored to:
        - The job requirements
        - The candidate's specific skills
        - Their experience level
        
        Each question comes with "evaluation keywords" - concepts you should listen
        for in their answer to know if they really understand the topic.
        
        Args:
            job_description: The full JD text
            candidate_info: Dict with candidate's skills, experience, etc.
            num_questions: How many questions to generate (default 5)
        
        Returns:
            List of question objects, each with:
                - question: The actual question text
                - keywords: Key concepts to listen for in the answer
        
        Example:
            [
                {
                    "question": "How would you optimize a slow PostgreSQL query?",
                    "keywords": ["indexing", "EXPLAIN", "query plan", "vacuuming"]
                }
            ]
        """
        
        # Extract candidate details
        matched_skills = candidate_info.get('matched_skills', [])
        experience_years = candidate_info.get('experience_years', 0)
        
        # Build a prompt for the AI to generate relevant questions
        prompt = f"""You are an expert technical interviewer. Generate {num_questions} interview questions for this candidate.

JOB DESCRIPTION (what we're hiring for):
{job_description[:1000]}

CANDIDATE PROFILE (who we're interviewing):
- Technical skills they have: {', '.join(matched_skills[:10])}
- Years of experience: {experience_years}

YOUR TASK:
Create questions that are:
1. Specific to the technologies mentioned in the JD
2. Appropriate for their experience level ({experience_years} years)
3. Mix technical depth with practical application
4. Actually answerable (not trick questions)

For each question, also provide "evaluation keywords" - the key concepts or techniques
you'd expect in a good answer.

OUTPUT FORMAT (return ONLY valid JSON, no markdown, no explanation):
[
  {{
    "question": "How would you handle database connection pooling in a high-traffic application?",
    "keywords": ["connection pool", "resource management", "concurrent connections", "timeouts"]
  }},
  {{
    "question": "Describe your approach to debugging a memory leak in production.",
    "keywords": ["profiling", "heap dump", "monitoring", "gradual degradation", "logs"]
  }}
]

Now generate {num_questions} questions in this exact JSON format:"""
        
        try:
            # Call Groq's LLM to generate the questions
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,  # Some creativity, but not too wild
                max_tokens=1500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up the response (sometimes AI wraps JSON in markdown)
            if '```json' in result:
                result = result.split('```json')[1].split('```')[0]
            elif '```' in result:
                result = result.split('```')[1].split('```')[0]
            
            result = result.strip()
            
            # Parse the JSON
            questions = json.loads(result)
            
            # Validate that we got a proper list
            if isinstance(questions, list):
                return questions
            else:
                print(f"⚠️ AI returned unexpected format: {type(questions)}")
                return []
            
        except json.JSONDecodeError as e:
            print(f"❌ Couldn't parse AI response as JSON: {e}")
            print(f"   Raw response: {result if 'result' in locals() else 'no response'}")
            return []
        except Exception as e:
            print(f"❌ Error generating questions: {e}")
            return []