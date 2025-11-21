# 🤖 SmartHR AI

An AI-powered HR assistant that actually works. Upload your policies, ask questions, screen candidates, and get interview questions — all in one place.

**[🚀 Try it live here](https://ai-smart-hr.streamlit.app/)**

---

## 🎯 What Does This Thing Do?

### Policy Chatbot 💬
Remember when employees would email HR with the same questions over and over? Yeah, that's over.

- Drop in your HR policy PDFs
- Employees ask questions like they're texting a friend
- Get instant answers with "this is from the Leave Policy"
- No more digging through 50-page documents

**Real example:**
```
Employee: "Can I work remotely on Fridays?"
AI: "Yes! According to the Remote Work Policy, hybrid employees 
     can work remotely 2-3 days per week, including Fridays."
```

### Recruitment Assistant 📄
Screening resumes is soul-crushing. Let AI do it.

- Upload a bunch of resumes (PDFs)
- Paste your job description
- AI ranks everyone and tells you who's a good fit
- Get personalized interview questions for candidate
- Includes "what to listen for" keywords

**Real example:**
```
Candidate: Sarah Chen
Score: 87/100
Matched Skills: Python, Machine Learning, AWS (5/7 required)
Top Questions:
1. How would you optimize a slow PostgreSQL query?
   🔑 Listen for: indexing, EXPLAIN, query optimization
```

---

## 🤷 Why Did I Build This?

**The Problem:**
- HR spends most of their time answering repetitive policy questions
- Screening resumes manually takes forever and is super biased
- Interview questions are usually generic and unhelpful

**The Solution:**
- AI reads your policies and answers questions
- AI screens resumes way faster than humans and focuses on actual skills
- AI generates specific interview questions

---

## 🛠️ Tech Stack

**What's under the hood:**

- **Frontend:** Streamlit
- **Brain:** Groq's Llama 3.3 70B (super fast, free API)
- **Embeddings:** Sentence-BERT (turns text into math)
- **Search:** FAISS (Facebook's vector database thing)
- **PDF Reading:** PyPDF2

**Why these choices?**
- Everything is pretrained (zero training time)
- Free APIs

---

## 🚀 Want to Run It Yourself?

### You'll Need:
- Python 3.11 or newer
- A Groq API key (free at [console.groq.com](https://console.groq.com))

### Setup:
```bash
# Clone it
git clone https://github.com/arfa-maryam-khan/smarthr-ai.git
cd smarthr-ai

# Make a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Add your API key
echo "GROQ_API_KEY=your_key_here" > .env

# Generate fake data to play with
python create_sample_data.py

# Run it!
streamlit run app.py
```

Open **http://localhost:8501** and you're good to go.

---

## 📖 How to Use It

### Policy Assistant

**First time setup:**
1. Click "Policy Assistant" in the sidebar
2. Upload your HR policy PDF
3. Hit "Process Documents" and wait for AI to process your policies
4. Done! Now you can ask questions

**Asking questions:**
- Type naturally: "How much maternity leave do I get?"
- The AI understands normal human speech

### Recruitment Hub

**Screening candidates:**
1. Go to "Recruitment Hub" → "Screen Candidates" tab
2. Upload resume PDFs (as many as you want)
3. Paste your job description
4. Adjust the threshold slider (50% is usually good)
5. Click "Screen Candidates"
6. Let AI screen the candidates

**Reading the results:**
- Green bars = shortlisted
- Red bars = not shortlisted
- Final score = 60% how well they match overall + 40% specific skills
- Download CSV to share with your team

**Interview questions:**
1. Go to "Interview Questions" tab
2. Pick a candidate from the dropdown
3. Click "Generate Questions"
4. Get 5-10 tailored questions with keywords

**Example output:**
```
1. How would you optimize a slow database query in PostgreSQL?
   🔑 Listen for: indexing, EXPLAIN, query plans, caching, JOIN optimization

2. Tell me about a time you had to debug a production issue under pressure.
   🔑 Listen for: monitoring tools, root cause analysis, communication, prevention
```

---

## 🧮 How Does the Scoring Work?

**Candidate Score = (Semantic Match × 60%) + (Skill Match × 40%)**

**Semantic Match:**
- AI reads the whole resume and JD
- Figures out if the person's experience actually fits
- Not just keyword matching — understands context

**Skill Match:**
- Counts how many required skills they have
- "Python, Machine Learning, AWS" vs "Required: Python, ML, AWS, Docker"
- 3 out of 4 = 75% skill match

**Example:**
```
Resume: Senior Python Developer, 5 years ML experience
JD: Looking for Python + ML + AWS expert
Semantic Match: 92% (experience fits great)
Skill Match: 67% (has Python & ML, missing AWS)
Final Score: (92 × 0.6) + (67 × 0.4) = 82/100
```

---

## 🎯 Project Layout
```
smarthr-ai/
├── app.py                    # The main app (start here)
├── modules/
│   ├── policy_chatbot.py    # RAG magic happens here
│   ├── resume_parser.py     # Resume → structured data
│   └── recruitment.py       # Screening & questions
├── data/
│   ├── policies/            # Drop your PDFs here
│   ├── resumes/             # Sample resumes
│   └── job_descriptions/    # Sample JDs
├── config/
│   └── skills_database.json # List of tech skills
├── create_sample_data.py    # Generates fake data
└── README.md                # You are here
```
---
