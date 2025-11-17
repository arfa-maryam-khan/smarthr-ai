"""
Recruitment Engine - Optimized for speed
"""
import os
import pickle
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util
from groq import Groq
from dotenv import load_dotenv
from modules.resume_parser import ResumeParser

load_dotenv()

class RecruitmentEngine:
    """Intelligent recruitment engine"""
    
    def __init__(self):
        """Initialize engine with lighter models"""
        print("\n🔄 Initializing Recruitment Engine...")
        
        try:
            # Use LIGHTER model for speed (same as policy chatbot)
            print("   📥 Loading Sentence-BERT (all-MiniLM-L6-v2)...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("   ✅ Sentence-BERT loaded!")
            
            print("   📥 Loading Resume Parser...")
            self.parser = ResumeParser()
            print("   ✅ Parser loaded!")
            
            # Groq for question generation
            print("   📥 Initializing Groq...")
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                self.client = Groq(api_key=api_key)
                print("   ✅ Groq ready!")
            else:
                print("   ⚠️ No Groq API key (questions will use fallback)")
                self.client = None
            
            print("✅ Recruitment Engine ready!\n")
            
        except Exception as e:
            print(f"\n❌ Initialization failed: {str(e)}")
            raise
    
    def calculate_semantic_similarity(self, resume_text: str, jd_text: str) -> float:
        """Calculate similarity using embeddings"""
        try:
            resume_emb = self.embedding_model.encode(resume_text, convert_to_tensor=True)
            jd_emb = self.embedding_model.encode(jd_text, convert_to_tensor=True)
            similarity = util.cos_sim(resume_emb, jd_emb).item()
            return similarity * 100
        except Exception as e:
            print(f"⚠️ Similarity calculation error: {e}")
            return 0.0
    
    def calculate_skill_match(self, resume_skills: List[str], jd_skills: List[str]):
        """Calculate skill overlap"""
        if not jd_skills:
            return 0, []
        
        # Case-insensitive matching
        resume_skills_lower = [s.lower() for s in resume_skills]
        jd_skills_lower = [s.lower() for s in jd_skills]
        
        matched = []
        for jd_skill in jd_skills:
            if jd_skill.lower() in resume_skills_lower:
                matched.append(jd_skill)
        
        match_rate = (len(matched) / len(jd_skills)) * 100
        return match_rate, matched
    
    def screen_candidates(
        self, 
        resume_files: List[str], 
        job_description: str, 
        threshold: float = 50
    ) -> List[Dict]:
        """Screen candidates"""
        print(f"\n🎯 Screening {len(resume_files)} candidates...")
        
        # Extract JD skills
        print("   🧠 Analyzing job requirements...")
        jd_skills = self.parser.extract_skills_from_jd(job_description)
        print(f"   📋 Found {len(jd_skills)} required skills")
        
        results = []
        
        for i, resume_file in enumerate(resume_files, 1):
            print(f"   📄 Processing {i}/{len(resume_files)}: {os.path.basename(resume_file)}")
            
            try:
                # Parse resume
                parsed = self.parser.parse(resume_file)
                
                if not parsed:
                    print(f"      ⚠️ Skipping - parsing failed")
                    continue
                
                # Calculate scores
                similarity_score = self.calculate_semantic_similarity(
                    parsed['raw_text'],
                    job_description
                )
                
                skill_match_rate, matched_skills = self.calculate_skill_match(
                    parsed.get('skills', []),
                    jd_skills
                )
                
                final_score = (similarity_score * 0.6) + (skill_match_rate * 0.4)
                
                results.append({
                    'name': parsed.get('name', 'Unknown'),
                    'filename': parsed['filename'],
                    'email': parsed.get('email'),
                    'phone': parsed.get('phone'),
                    'total_skills': len(parsed.get('skills', [])),
                    'matched_skills': matched_skills,
                    'matched_skills_count': len(matched_skills),
                    'required_skills_count': len(jd_skills),
                    'similarity_score': round(similarity_score, 2),
                    'skill_match_rate': round(skill_match_rate, 2),
                    'final_score': round(final_score, 2),
                    'experience_years': parsed.get('experience_years', 0),
                    'education': parsed.get('education', []),
                    'shortlisted': final_score >= threshold,
                    'resume_text': parsed['raw_text']
                })
                
                print(f"      ✅ Score: {final_score:.1f}")
                
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
                continue
        
        # Sort by score
        results.sort(key=lambda x: x['final_score'], reverse=True)
        
        shortlisted = len([r for r in results if r['shortlisted']])
        print(f"\n✅ Screening complete: {shortlisted}/{len(results)} shortlisted\n")
        
        return results
    
    def generate_interview_questions(
        self, 
        job_description: str, 
        candidate_info: Dict, 
        num_questions: int = 5
    ) -> List[Dict]:
        """
        Generate interview questions WITH evaluation keywords
        
        Returns:
            List of dicts with 'question' and 'keywords' for each question
        """
        
        if not self.client:
            # Fallback without Groq
            skills = candidate_info.get('matched_skills', ['general experience'])[:num_questions]
            return [
                {
                    'question': f"Tell me about your experience with {skill}.",
                    'keywords': [skill, 'project', 'implementation', 'results']
                }
                for skill in skills
            ]
        
        prompt = f"""You are an expert technical interviewer. Generate {num_questions} interview questions with evaluation criteria.

    Job Description:
    {job_description[:500]}

    Candidate Profile:
    - Name: {candidate_info.get('name', 'Unknown')}
    - Key Skills: {', '.join(candidate_info.get('matched_skills', [])[:8])}
    - Experience: {candidate_info.get('experience_years', 0)} years

    For each question, provide:
    1. The interview question
    2. Key concepts/keywords the answer should include (3-5 keywords)

    Format your response EXACTLY like this example:

    Q1: How would you optimize a slow database query?
    KEYWORDS: indexing, query plan, JOIN optimization, caching, EXPLAIN

    Q2: Describe your experience with React hooks.
    KEYWORDS: useState, useEffect, custom hooks, lifecycle, performance

    Generate {num_questions} questions now in this exact format:"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            text = response.choices[0].message.content
            
            # Parse questions and keywords
            import re
            questions_data = []
            
            # Split by Q1:, Q2:, etc.
            sections = re.split(r'Q\d+:', text)
            
            for section in sections[1:]:  # Skip first empty split
                section = section.strip()
                
                if not section:
                    continue
                
                # Try to split by "KEYWORDS:" or "Keywords:" or similar
                parts = re.split(r'KEYWORDS?:', section, flags=re.IGNORECASE)
                
                if len(parts) >= 2:
                    question = parts[0].strip()
                    keywords_text = parts[1].strip()
                    
                    # Extract keywords (split by comma or newline)
                    keywords = [
                        kw.strip() 
                        for kw in re.split(r'[,\n]', keywords_text)
                        if kw.strip() and len(kw.strip()) > 2
                    ]
                    
                    if question and keywords:
                        questions_data.append({
                            'question': question,
                            'keywords': keywords[:6]  # Max 6 keywords
                        })
            
            # If parsing worked, return results
            if questions_data:
                return questions_data[:num_questions]
            
            # Fallback if parsing failed
            print("⚠️ Parsing failed, using fallback")
            skills = candidate_info.get('matched_skills', ['general experience'])[:num_questions]
            return [
                {
                    'question': f"Describe your experience with {skill} in detail.",
                    'keywords': [skill, 'project examples', 'challenges', 'results', 'best practices']
                }
                for skill in skills
            ]
            
        except Exception as e:
            print(f"⚠️ Question generation error: {e}")
            skills = candidate_info.get('matched_skills', ['general experience'])[:num_questions]
            return [
                {
                    'question': f"Tell me about your experience with {skill}.",
                    'keywords': [skill, 'implementation', 'challenges', 'outcomes']
                }
                for skill in skills
            ]