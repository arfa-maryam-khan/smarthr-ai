def __init__(self):
    """Initialize recruitment engine"""
    print("🔄 Initializing Recruitment Engine...")
    
    # Initialize parser
    print("📖 Loading Resume Parser...")
    self.parser = ResumeParser()
    
    # Load Sentence-BERT model
    print("🧠 Loading Sentence-BERT model...")
    try:
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence-BERT loaded!")
    except Exception as e:
        print(f"❌ Failed to load Sentence-BERT: {e}")
        raise
    
    # Initialize Groq for question generation
    print("🤖 Initializing Groq client...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found!")
        raise ValueError("GROQ_API_KEY not set")
    
    from groq import Groq
    self.client = Groq(api_key=api_key)
    print("✅ Groq client ready!")
    
    print("✅ Recruitment Engine initialized!\n")