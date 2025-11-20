"""
Generate all sample data for SmartHR AI
"""
from fpdf import FPDF
import os

def create_policy_pdf(filename, title, content):
    """Create a policy PDF"""
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)
    
    # Content
    pdf.set_font("Arial", size=11)
    for line in content.split('\n'):
        if line.strip():
            pdf.multi_cell(0, 6, line)
            pdf.ln(2)
    
    os.makedirs('data/policies', exist_ok=True)
    pdf.output(f"data/policies/{filename}")
    print(f"✅ Created: data/policies/{filename}")

def create_resume_pdf(filename, data):
    """Create a resume PDF"""
    pdf = FPDF()
    pdf.add_page()
    
    # Name
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, data['name'], ln=True, align='C')
    
    # Contact
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, f"{data['email']} | {data['phone']}", ln=True, align='C')
    pdf.ln(5)
    
    # Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "PROFESSIONAL SUMMARY", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 5, data['summary'])
    pdf.ln(3)
    
    # Skills
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "TECHNICAL SKILLS", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 5, data['skills'])
    pdf.ln(3)
    
    # Experience
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "WORK EXPERIENCE", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 5, data['experience'])
    pdf.ln(3)
    
    # Education
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "EDUCATION", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 5, data['education'])
    
    os.makedirs('data/resumes', exist_ok=True)
    pdf.output(f"data/resumes/{filename}")
    print(f"✅ Created: data/resumes/{filename}")

def main():
    print("🚀 Creating sample data for SmartHR AI...\n")
    
    # ========== POLICY DOCUMENTS ==========
    
    print("📄 Creating policy documents...")
    
    # Leave Policy
    leave_policy = """
ANNUAL LEAVE POLICY

1. ELIGIBILITY
All full-time employees are entitled to paid annual leave after completing 3 months of probation period.

2. LEAVE ENTITLEMENT
- Full-time employees: 15 days per year
- Part-time employees: Pro-rated based on working hours
- Leave accrues monthly at 1.25 days per month
- Maximum carry-forward: 5 days to next year

3. REQUESTING LEAVE
- Submit leave request at least 2 weeks in advance through HR portal
- Manager approval required
- Maximum 10 consecutive days without special approval from HR Director

4. SICK LEAVE
- 10 days paid sick leave per year
- Medical certificate required for absences exceeding 3 consecutive days
- Unused sick leave does not carry forward to next year

5. MATERNITY AND PATERNITY LEAVE
- Maternity leave: 12 weeks paid leave
- Paternity leave: 2 weeks paid leave
- Must notify HR at least 1 month before expected date
- Job protection guaranteed during leave period

6. PUBLIC HOLIDAYS
- Company observes 10 public holidays annually
- Holiday list published at start of each fiscal year
- Work on public holidays compensated with overtime pay or lieu days

7. EMERGENCY LEAVE
- Up to 3 days per year for family emergencies
- Requires manager approval and documentation
- Can be taken at short notice
"""
    
    create_policy_pdf("leave_policy.pdf", "ANNUAL LEAVE POLICY", leave_policy)
    
    # Remote Work Policy
    remote_policy = """
REMOTE WORK POLICY

1. ELIGIBILITY
- Must complete 6 months probation period
- Performance rating: Meets Expectations or higher
- Manager approval required
- Role must be suitable for remote work

2. WORK ARRANGEMENTS
Hybrid Model:
- 2-3 days in office per week
- 2-3 days remote work
- Core team days: Tuesdays and Thursdays in office

Full Remote:
- Available for specific roles with director approval
- Quarterly in-person meetings required

3. WORKING HOURS
- Core hours: 10 AM - 4 PM in company timezone (must be available)
- Flexible start and end times allowed
- Total: 8 hours per day, 40 hours per week
- Overtime requires prior approval

4. EQUIPMENT AND EXPENSES
Company Provides:
- Laptop and required software licenses
- VPN access and security tools
- Ergonomic equipment on request

Employee Provides:
- Stable internet connection (minimum 25 Mbps)
- Dedicated workspace
- Appropriate work environment

Monthly Stipend:
- $50 for internet and utilities
- Reimbursement requires receipts

5. COMMUNICATION REQUIREMENTS
- Daily standup: 9:30 AM via video call
- Available on Slack during core hours
- Respond within 2 hours during work hours
- Weekly 1:1 with direct manager
- Camera on for team meetings

6. PERFORMANCE AND MONITORING
- Same performance standards as office work
- Output-based evaluation
- Regular check-ins with manager
- Quarterly performance reviews

7. DATA SECURITY
- Use company VPN for all work
- No public WiFi for sensitive work
- Lock computer when stepping away
- Report security incidents immediately to IT
- Do not share credentials or access with family members
"""
    
    create_policy_pdf("remote_work_policy.pdf", "REMOTE WORK POLICY", remote_policy)
    
    # Code of Conduct
    conduct_policy = """
CODE OF CONDUCT

1. WORKPLACE BEHAVIOR
- Treat all colleagues with respect and dignity
- Zero tolerance for harassment, discrimination, or bullying
- Professional communication in all settings (office, remote, social)
- Report violations to HR immediately
- Maintain confidentiality of sensitive discussions

2. DRESS CODE
- Business casual for office days
- Professional attire for client meetings and presentations
- Casual Fridays allowed (no offensive graphics)
- Use good judgment and represent company professionally

3. CONFIDENTIALITY AND DATA PROTECTION
- Protect company confidential information
- Do not share client data externally
- Sign NDA on first day of employment
- Return all documents and equipment on exit
- Do not discuss confidential matters in public spaces

4. CONFLICT OF INTEREST
- Disclose any potential conflicts to manager and HR
- No competing business activities during employment
- Outside work or consulting requires written approval
- Family member employment requires disclosure and HR approval

5. SOCIAL MEDIA POLICY
- Do not speak on behalf of company without authorization
- Respect confidentiality in all online forums
- Maintain professional conduct on public platforms
- Do not post sensitive company information
- Personal opinions should be clearly marked as such

6. SUBSTANCE ABUSE
- Workplace must be free from drugs and alcohol
- Being under influence during work hours is prohibited
- Alcohol at company events must be consumed responsibly
- Violations will result in disciplinary action

7. REPORTING VIOLATIONS
- Report concerns to direct manager or HR
- Anonymous hotline available: 1-800-XXX-XXXX
- No retaliation for good faith reports
- All reports investigated promptly and confidentially
- Whistleblower protections in place
"""
    
    create_policy_pdf("code_of_conduct.pdf", "CODE OF CONDUCT", conduct_policy)
    
    # ========== RESUMES ==========
    
    print("\n📄 Creating sample resumes...")
    
    resume1 = {
        'name': 'Sarah Chen',
        'email': 'sarah.chen@email.com',
        'phone': '+1-555-0101',
        'summary': 'Senior Software Engineer with 6 years of experience in Python, Machine Learning, and cloud technologies. Proven track record of building scalable ML systems, leading technical teams, and delivering production-ready AI solutions. Passionate about NLP and building intelligent applications.',
        'skills': 'Python, Machine Learning, Deep Learning, NLP, TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy, AWS, Docker, Kubernetes, SQL, PostgreSQL, MongoDB, REST API, FastAPI, Flask, Git, CI/CD, Agile, Linux',
        'experience': '''Senior Software Engineer - TechCorp Inc (2020 - Present)
- Led development of ML-powered recommendation system serving 100K+ daily users
- Built RAG-based chatbot using LangChain and OpenAI APIs, improving customer satisfaction by 40%
- Managed team of 4 engineers, conducted code reviews and mentored junior developers
- Implemented CI/CD pipelines reducing deployment time by 60%
- Technologies: Python, TensorFlow, AWS, Docker, PostgreSQL

Software Engineer - DataSystems LLC (2018 - 2020)
- Developed data pipelines processing 1M+ records daily using Apache Spark
- Built REST APIs for internal analytics platform using FastAPI
- Implemented automated testing increasing code coverage to 85%
- Technologies: Python, Spark, Redis, MySQL

Junior Developer - StartupXYZ (2017 - 2018)
- Contributed to backend development of e-commerce platform
- Fixed bugs and improved application performance by 30%
- Technologies: Python, Django, PostgreSQL''',
        'education': '''Master of Science in Computer Science
Stanford University, CA (2017)
GPA: 3.8/4.0
Thesis: Neural Networks for Natural Language Understanding

Bachelor of Engineering in Computer Science
UC Berkeley, CA (2015)
GPA: 3.7/4.0
Honors: Dean's List, Summa Cum Laude'''
    }
    
    resume2 = {
        'name': 'Michael Rodriguez',
        'email': 'michael.rodriguez@email.com',
        'phone': '+1-555-0102',
        'summary': 'Full-stack developer with 4 years of experience building scalable web applications. Proficient in React, Node.js, and cloud infrastructure. Strong focus on user experience and clean code.',
        'skills': 'JavaScript, TypeScript, React, Node.js, Express, Python, SQL, PostgreSQL, MongoDB, AWS, Docker, Git, REST API, GraphQL, HTML, CSS, Tailwind, Jest, CI/CD',
        'experience': '''Full Stack Developer - WebSolutions Inc (2021 - Present)
- Built customer portal using React and Node.js, handling 50K+ monthly users
- Implemented JWT authentication and role-based authorization
- Optimized database queries reducing load time by 50%
- Technologies: React, Node.js, PostgreSQL, AWS, Docker

Junior Developer - StartupABC (2019 - 2021)
- Developed features for e-commerce platform using React and Express
- Fixed bugs and improved application performance
- Wrote unit tests using Jest, achieving 80% code coverage
- Technologies: React, Express, MongoDB

Intern - TechHub (Summer 2019)
- Assisted in frontend development using React
- Participated in code reviews and agile ceremonies
- Technologies: React, JavaScript, HTML, CSS''',
        'education': '''Bachelor of Science in Computer Science
MIT, MA (2019)
GPA: 3.6/4.0
Relevant coursework: Web Development, Databases, Algorithms'''
    }
    
    resume3 = {
        'name': 'Emily Watson',
        'email': 'emily.watson@email.com',
        'phone': '+1-555-0103',
        'summary': 'Data Analyst with 3 years of experience turning data into actionable insights. Skilled in SQL, Python, and data visualization. Strong analytical mindset with business acumen.',
        'skills': 'SQL, Python, Pandas, NumPy, Matplotlib, Seaborn, Tableau, Power BI, Excel, Statistical Analysis, Data Visualization, A/B Testing, Google Analytics',
        'experience': '''Data Analyst - Analytics Corp (2021 - Present)
- Created executive dashboards in Tableau tracking KPIs for C-suite
- Analyzed customer behavior data identifying 20% revenue opportunity
- Conducted A/B tests improving conversion rates by 15%
- Generated weekly reports automating 10 hours of manual work
- Technologies: SQL, Python, Tableau, Excel

Junior Analyst - Finance Inc (2020 - 2021)
- Cleaned and processed financial data using SQL and Python
- Built Excel models for forecasting and budgeting
- Supported reporting team with ad-hoc analysis
- Technologies: SQL, Excel, Python''',
        'education': '''Bachelor of Science in Statistics
Columbia University, NY (2020)
GPA: 3.7/4.0
Relevant coursework: Statistical Analysis, Data Mining, Machine Learning'''
    }
    
    resume4 = {
        'name': 'David Kim',
        'email': 'david.kim@email.com',
        'phone': '+1-555-0104',
        'summary': 'Junior software engineer with 2 years of experience. Strong foundation in Python and web development. Eager to learn and contribute to ML/AI projects.',
        'skills': 'Python, JavaScript, HTML, CSS, Flask, SQL, Git, Linux, REST API',
        'experience': '''Junior Software Engineer - CodeLab (2022 - Present)
- Developed backend APIs using Flask and Python
- Maintained MySQL database and wrote optimized queries
- Fixed bugs and added new features based on user feedback
- Technologies: Python, Flask, MySQL, Git

Intern - TechStartup (Summer 2022)
- Assisted in web development projects
- Learned agile methodologies and participated in sprints
- Technologies: Python, JavaScript, HTML, CSS''',
        'education': '''Bachelor of Science in Computer Science
University of Washington (2022)
GPA: 3.5/4.0'''
    }
    
    resume5 = {
        'name': 'Priya Sharma',
        'email': 'priya.sharma@email.com',
        'phone': '+1-555-0105',
        'summary': 'Machine Learning Engineer with 5 years of experience in building and deploying ML models. Expert in Python, deep learning, and MLOps. Published researcher with 3 peer-reviewed papers.',
        'skills': 'Python, Machine Learning, Deep Learning, NLP, Computer Vision, TensorFlow, PyTorch, Keras, Scikit-learn, MLflow, Kubeflow, AWS SageMaker, Docker, Kubernetes, Git, SQL, Spark',
        'experience': '''Machine Learning Engineer - AI Labs (2020 - Present)
- Developed and deployed 10+ ML models in production using AWS SageMaker
- Built NLP models for sentiment analysis with 92% accuracy
- Implemented MLOps pipelines using MLflow and Kubeflow
- Published 2 papers in top-tier conferences (NeurIPS, ACL)
- Technologies: PyTorch, TensorFlow, AWS, Docker, Kubernetes

ML Research Intern - Google Research (Summer 2019)
- Researched transformer architectures for machine translation
- Published paper at ACL conference
- Technologies: TensorFlow, Python

Research Assistant - Stanford AI Lab (2018 - 2019)
- Assisted professors with deep learning research
- Collected and annotated datasets
- Technologies: PyTorch, Python''',
        'education': '''Master of Science in Artificial Intelligence
Stanford University (2020)
GPA: 3.9/4.0
Thesis: Attention Mechanisms in Neural Machine Translation

Bachelor of Technology in Computer Science
IIT Delhi, India (2018)
GPA: 9.2/10.0'''
    }
    
    create_resume_pdf("resume_1_sarah_chen.pdf", resume1)
    create_resume_pdf("resume_2_michael_rodriguez.pdf", resume2)
    create_resume_pdf("resume_3_emily_watson.pdf", resume3)
    create_resume_pdf("resume_4_david_kim.pdf", resume4)
    create_resume_pdf("resume_5_priya_sharma.pdf", resume5)
    
    # ========== JOB DESCRIPTIONS ==========
    
    print("\n📄 Creating job descriptions...")
    
    jd_ml = """SENIOR SOFTWARE ENGINEER - MACHINE LEARNING

We are seeking an experienced ML Engineer to join our AI team.

REQUIRED SKILLS:
- 5+ years of Python development experience
- Strong experience with Machine Learning frameworks (TensorFlow, PyTorch, Scikit-learn)
- Experience with NLP and text processing
- Proficiency in SQL and NoSQL databases
- Cloud platforms (AWS, GCP, or Azure)
- Docker and Kubernetes
- REST API development
- Git version control

PREFERRED SKILLS:
- Experience with LLMs and RAG systems
- FastAPI or Flask framework
- CI/CD pipelines
- Agile/Scrum methodologies
- Published research papers

RESPONSIBILITIES:
- Design and implement ML pipelines
- Develop scalable backend services
- Collaborate with data scientists and product teams
- Code review and mentoring junior engineers
- Write technical documentation
- Stay current with latest ML research

EDUCATION:
- Bachelor's or Master's in Computer Science or related field

EXPERIENCE:
- 5+ years in software development
- 2+ years in ML/AI projects
"""
    
    jd_fullstack = """FULL STACK DEVELOPER

REQUIRED SKILLS:
- 3+ years of JavaScript/TypeScript experience
- React or Angular frontend development
- Node.js backend development
- SQL databases (PostgreSQL, MySQL)
- RESTful API design
- Git version control

PREFERRED:
- AWS or cloud experience
- Docker
- GraphQL
- CI/CD

RESPONSIBILITIES:
- Build web applications
- Develop REST APIs
- Write tests
- Collaborate with designers

EDUCATION: Bachelor's in CS or related field
EXPERIENCE: 3+ years
"""
    
    jd_data = """DATA ANALYST

REQUIRED SKILLS:
- 2+ years SQL experience
- Python (Pandas, NumPy)
- Data visualization (Tableau, Power BI, or Plotly)
- Excel advanced functions
- Statistical analysis

RESPONSIBILITIES:
- Create dashboards and reports
- Analyze business metrics
- Support data-driven decision making
- Conduct A/B tests

EDUCATION: Bachelor's in Statistics, Math, or related
EXPERIENCE: 2+ years
"""
    
    os.makedirs('data/job_descriptions', exist_ok=True)
    
    with open('data/job_descriptions/ml_engineer_jd.txt', 'w') as f:
        f.write(jd_ml)
    print("✅ Created: data/job_descriptions/ml_engineer_jd.txt")
    
    with open('data/job_descriptions/fullstack_dev_jd.txt', 'w') as f:
        f.write(jd_fullstack)
    print("✅ Created: data/job_descriptions/fullstack_dev_jd.txt")
    
    with open('data/job_descriptions/data_analyst_jd.txt', 'w') as f:
        f.write(jd_data)
    print("✅ Created: data/job_descriptions/data_analyst_jd.txt")
    
    print("\n" + "="*50)
    print("✅ ALL SAMPLE DATA CREATED SUCCESSFULLY!")
    print("="*50)
    print("\nGenerated:")
    print("  📁 3 Policy PDFs in data/policies/")
    print("  📁 5 Resume PDFs in data/resumes/")
    print("  📁 3 Job Descriptions in data/job_descriptions/")
    print("  📁 1 Skills database in config/")
    print("\n🚀 Ready to run the application!")

if __name__ == "__main__":
    main()