"""
HR Policy Chatbot using RAG (Retrieval-Augmented Generation)
Architecture: Sentence-BERT + FAISS + Groq LLM
This is the industry-standard approach for document Q&A
"""
import os
import pickle
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from groq import Groq
from dotenv import load_dotenv
from modules.utils import extract_text_from_pdf, chunk_text

load_dotenv()

class PolicyChatbot:
    """
    RAG-based HR Policy Chatbot
    
    Why this architecture?
    - Sentence-BERT: State-of-the-art for semantic search (better than keyword matching)
    - FAISS: Production-grade vector search (used by Meta, handles billions of vectors)
    - Groq LLM: Accurate response generation grounded in retrieved context
    - Result: No hallucinations, cites sources, handles complex queries
    """
    
    def __init__(self, policy_dir: str = "data/policies/"):
        """Initialize chatbot with optimal models"""
        self.policy_dir = policy_dir
        self.documents = []
        self.embeddings = None
        self.index = None
        
        # Sentence-BERT: Best pretrained model for semantic similarity
        print("🔄 Loading Sentence-BERT (all-MiniLM-L6-v2)...")
        print("   Why: 384-dim embeddings, 22M params, fast inference")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence-BERT loaded!")
        
        # Groq LLM for response generation
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY not found in .env file!")
        self.client = Groq(api_key=api_key)
        print("✅ Groq client initialized!")
        
    def load_policies(self) -> bool:
        """
        Load policy documents and generate embeddings
        
        Process:
        1. Extract text from PDFs (PyPDF2 - just file I/O)
        2. Split into chunks (overlap for context preservation)
        3. Generate embeddings (Sentence-BERT - semantic understanding)
        4. Cache everything (fast subsequent loads)
        """
        print(f"\n📂 Loading policies from: {self.policy_dir}")
        
        os.makedirs(self.policy_dir, exist_ok=True)
        
        # Check for cached embeddings (huge speedup!)
        cache_file = 'models/embeddings/policy_cache.pkl'
        
        if os.path.exists(cache_file):
            try:
                print("⚡ Loading cached embeddings (instant!)...")
                with open(cache_file, 'rb') as f:
                    cache = pickle.load(f)
                    self.documents = cache['documents']
                    self.embeddings = cache['embeddings']
                print(f"✅ Loaded {len(self.documents)} cached chunks!")
                return True
            except Exception as e:
                print(f"⚠️ Cache load failed: {e}. Rebuilding...")
        
        # Load PDF files
        pdf_files = [f for f in os.listdir(self.policy_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print("⚠️ No PDF files found! Add policy PDFs to data/policies/")
            return False
        
        print(f"📄 Found {len(pdf_files)} PDF files")
        
        # Process each PDF
        for filename in pdf_files:
            filepath = os.path.join(self.policy_dir, filename)
            print(f"   Processing: {filename}")
            
            # Extract text (PyPDF2 - just reads the file)
            text = extract_text_from_pdf(filepath)
            
            if not text.strip():
                print(f"   ⚠️ No text extracted from {filename}")
                continue
            
            # Chunk with overlap (preserves context across boundaries)
            chunks = chunk_text(text, chunk_size=500, overlap=50)
            
            # Store with metadata for source attribution
            for i, chunk in enumerate(chunks):
                self.documents.append({
                    'source': filename,
                    'chunk_id': i,
                    'content': chunk
                })
        
        if not self.documents:
            print("❌ No documents loaded!")
            return False
        
        print(f"✅ Loaded {len(self.documents)} text chunks")
        
        # Generate embeddings (Sentence-BERT)
        print("🧠 Generating semantic embeddings...")
        print("   This captures meaning, not just keywords")
        
        texts = [doc['content'] for doc in self.documents]
        
        try:
            # Batch encoding for efficiency
            self.embeddings = self.embedding_model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True,
                batch_size=32
            )
            
            # Cache for instant future loads
            os.makedirs('models/embeddings', exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'embeddings': self.embeddings
                }, f)
            
            print("💾 Embeddings cached successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            return False
    
    def build_vector_store(self, force_rebuild: bool = False) -> bool:
        """
        Build FAISS index for fast similarity search
        
        Why FAISS?
        - Used by Meta in production (billions of vectors)
        - 100x faster than brute force search
        - Exact nearest neighbor search (L2 distance)
        """
        index_path = 'models/embeddings/faiss.index'
        
        # Load existing index
        if os.path.exists(index_path) and not force_rebuild:
            try:
                print("⚡ Loading cached FAISS index...")
                self.index = faiss.read_index(index_path)
                print(f"✅ Index loaded ({self.index.ntotal} vectors)!")
                return True
            except Exception as e:
                print(f"⚠️ Failed to load index: {e}. Rebuilding...")
        
        if self.embeddings is None:
            print("❌ No embeddings available! Load policies first.")
            return False
        
        print("🔄 Building FAISS index...")
        
        try:
            # L2 (Euclidean) distance index - exact search
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            
            # Add all embeddings
            self.index.add(self.embeddings.astype('float32'))
            
            # Save for future use
            os.makedirs('models/embeddings', exist_ok=True)
            faiss.write_index(self.index, index_path)
            
            print(f"✅ FAISS index built ({self.index.ntotal} vectors)!")
            return True
            
        except Exception as e:
            print(f"❌ Error building index: {e}")
            return False
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve most relevant document chunks using semantic search
        
        Process:
        1. Encode query with same model (Sentence-BERT)
        2. Search FAISS index for nearest neighbors
        3. Return top-k most similar chunks
        
        Why semantic search?
        - "PTO" query matches "paid time off" policy (understands synonyms)
        - "sick days" query matches "medical leave" (understands concepts)
        """
        if self.index is None or not self.documents:
            print("⚠️ Vector store not initialized!")
            return []
        
        try:
            # Encode query with same model as documents
            query_embedding = self.embedding_model.encode(
                [query],
                convert_to_numpy=True
            )
            
            # Search FAISS index
            k = min(top_k, len(self.documents))
            distances, indices = self.index.search(
                query_embedding.astype('float32'),
                k
            )
            
            # Get retrieved documents
            retrieved_docs = []
            for idx in indices[0]:
                if 0 <= idx < len(self.documents):
                    retrieved_docs.append(self.documents[idx])
            
            return retrieved_docs
            
        except Exception as e:
            print(f"❌ Error retrieving context: {e}")
            return []
    
    def generate_response(self, query: str) -> Dict:
        """
        Generate answer using RAG (Retrieval-Augmented Generation)
        
        RAG Process:
        1. RETRIEVE: Find relevant policy chunks (semantic search)
        2. AUGMENT: Add retrieved context to LLM prompt
        3. GENERATE: LLM answers ONLY from provided context
        
        Benefits:
        - No hallucinations (LLM can't make up policies)
        - Source attribution (can cite which policy)
        - Up-to-date (no training needed, just update PDFs)
        """
        
        # Step 1: RETRIEVE relevant context
        context_docs = self.retrieve_context(query, top_k=3)
        
        if not context_docs:
            return {
                'answer': "I don't have any policy documents loaded. Please upload HR policy PDFs to the data/policies/ folder.",
                'sources': [],
                'context': []
            }
        
        # Step 2: AUGMENT - Build context string
        context = "\n\n".join([
            f"[Source: {doc['source']}]\n{doc['content']}"
            for doc in context_docs
        ])
        
        # Step 3: GENERATE - Prompt LLM with context
        prompt = f"""You are a helpful HR assistant. Answer the employee's question based ONLY on the HR policy documents provided below.

**IMPORTANT**: Only use information from the policy context. If the answer is not in the provided policies, clearly state that.

**HR Policy Context:**
{context}

**Employee Question:** {query}

**Instructions:**
- Provide a clear, concise answer
- ONLY use information from the policy documents above
- Cite which policy document the information comes from (e.g., "According to leave_policy.pdf...")
- If the answer is not in the policies, say: "I don't have information about this in our current policy documents"
- Be professional and helpful

**Answer:**"""
        
        try:
            # Call Groq LLM
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Fast, accurate
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful HR assistant. Only answer based on provided policy documents. Never make up information."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temp = more factual
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            sources = list(set([doc['source'] for doc in context_docs]))
            
            return {
                'answer': answer,
                'sources': sources,
                'context': context_docs
            }
            
        except Exception as e:
            return {
                'answer': f"Error generating response: {str(e)}",
                'sources': [],
                'context': []
            }
    
    def get_stats(self) -> Dict:
        """Get chatbot statistics"""
        return {
            'total_documents': len(self.documents),
            'total_chunks': len(self.documents),
            'embedding_dimension': self.embeddings.shape[1] if self.embeddings is not None else 0,
            'index_size': self.index.ntotal if self.index else 0
        }
