"""
Test if models load correctly
"""
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Prevent warnings

print("🔄 Testing model loading...")

try:
    print("\n1. Testing Sentence-BERT...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Sentence-BERT loaded!")
    
    print("\n2. Testing embedding generation...")
    embedding = model.encode("test")
    print(f"✅ Embedding generated! Shape: {embedding.shape}")
    
    print("\n3. Testing Groq...")
    from groq import Groq
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        client = Groq(api_key=api_key)
        print("✅ Groq client initialized!")
    else:
        print("⚠️ GROQ_API_KEY not found in .env")
    
    print("\n✅ ALL TESTS PASSED!")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()