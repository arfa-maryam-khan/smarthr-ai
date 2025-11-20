"""
HR Policy Chatbot

This chatbot uses RAG (Retrieval-Augmented Generation) to answer questions about
HR policies. 

How it works:
1. We break policy documents into small chunks
2. Convert each chunk into a "meaning vector" (semantic embedding)
3. When you ask a question, we find the most relevant chunks
4. An AI reads those chunks and gives you a natural answer

Tech stack: Sentence-BERT for understanding, FAISS for fast search, Groq for answers
"""

import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from groq import Groq
from dotenv import load_dotenv
from modules.utils import extract_text_from_pdf

load_dotenv()


class PolicyChatbot:
    """
    An AI assistant that answers questions about your company's HR policies.
    """
    
    def __init__(self, data_dir: str = "data/policies/"):
        """
        Set up the chatbot with AI models and get ready to load policies.
        
        Args:
            data_dir: Folder where your policy PDF files are stored
        """
        self.data_dir = data_dir
        
        # Storage for our policy documents and their chunks
        self.documents = []  # Original docs: [{source, content, chunks}]
        self.chunks = []  # All text chunks combined from all documents
        self.chunk_sources = []  # Keeps track of which chunk came from which file
        self.index = None  # FAISS search index
        
        # Load the AI model
        print("🔄 Loading Sentence-BERT (the brain that understands your questions)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Ready to understand your questions!")
        
        # Set up the AI that generates natural language answers
        api_key = os.getenv("GROQ_API_KEY")
        
        # If not in environment, check Streamlit secrets
        if not api_key:
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
                    api_key = st.secrets['GROQ_API_KEY']
            except:
                pass
        
        if not api_key:
            raise ValueError("Oops! Can't find GROQ_API_KEY. Add it to your .env file or Streamlit secrets.")
        
        self.client = Groq(api_key=api_key)
        print("✅ AI assistant ready to answer questions!")
    
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Break long documents into chunks that the AI can work with.

        Args:
            text: The full document text
            chunk_size: How many words per chunk
            overlap: How many words to repeat between chunks
        
        Returns:
            List of text chunks, like pages in a book
        """
        words = text.split()
        chunks = []
        
        # Slide through the text with overlapping windows
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():  # Don't keep empty chunks
                chunks.append(chunk)
        
        # If document is tiny, just return it as-is
        return chunks if chunks else [text]
    
    
    def load_policies(self) -> bool:
        """
        Read all PDF policy documents from the policies folder.
        
        Returns:
            True if we found and loaded at least one document, False otherwise
        """
        print("📂 Looking for policy documents...")
        
        # Make sure the folder exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Find all PDF files in the folder
        policy_files = [f for f in os.listdir(self.data_dir) if f.endswith('.pdf')]
        
        print(f"📄 Found {len(policy_files)} PDF files: {policy_files}")
        
        if not policy_files:
            print("❌ No policy files found! Add some PDFs to the policies folder.")
            return False
        
        # Read each PDF and extract the text
        for filename in policy_files:
            filepath = os.path.join(self.data_dir, filename)
            print(f"📖 Reading {filename}...")
            
            # PyPDF2 extracts the actual text from the PDF
            text = extract_text_from_pdf(filepath)
            
            if text.strip():
                print(f"✅ Got {len(text)} characters from {filename}")
                self.documents.append({
                    'content': text,
                    'source': filename,  # Keep track of where this came from
                    'chunks': []
                })
            else:
                print(f"⚠️ Couldn't extract text from {filename} (might be scanned image?)")
        
        print(f"✅ Successfully loaded {len(self.documents)} policy documents")
        return len(self.documents) > 0
    
    
    def build_vector_store(self) -> bool:
        """
        Process all documents into a searchable format that AI can understand.
        
        This is where the magic happens:
        1. Break documents into chunks (small pieces)
        2. Convert each chunk into a "meaning vector" using AI
        3. Build a FAISS index for lightning-fast search
        
        Returns:
            True if everything worked, False if something went wrong
        """
        print("🧠 Building the search engine for your policies...")
        
        all_chunks = []
        chunk_metadata = []
        
        # Break each document into chunks
        for doc in self.documents:
            print(f"📝 Breaking {doc['source']} into chunks...")
            
            chunks = self.chunk_text(doc['content'])
            doc['chunks'] = chunks
            
            print(f"   Created {len(chunks)} chunks")
            
            # Keep track of which chunk came from which document
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                chunk_metadata.append({
                    'source': doc['source'],
                    'chunk_id': i
                })
        
        print(f"📊 Total: {len(all_chunks)} chunks across all documents")
        
        if not all_chunks:
            print("❌ No content to process!")
            return False
        
        # "semantic embedding" - similar meanings = similar numbers
        print(f"🧠 Converting {len(all_chunks)} chunks into AI-understandable format...")
        embeddings = self.model.encode(
            all_chunks, 
            convert_to_tensor=False, 
            show_progress_bar=True
        )
        
        # Build a FAISS index for super-fast similarity search
        print("🔍 Creating search index...")
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)  # L2 = Euclidean distance
        self.index.add(embeddings)
        
        # Store everything we need for later searches
        self.chunks = all_chunks
        self.chunk_sources = chunk_metadata
        
        print(f"✅ Search engine ready!")
        print(f"   📚 {len(self.documents)} documents indexed")
        print(f"   📄 {len(self.chunks)} total chunks")
        print(f"   🔍 Index size: {self.index.ntotal} vectors")
        
        return True
    
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Find the most relevant policy sections for a given question.
        
        This is the "retrieval" part of RAG. We convert the question into the same
        format as our chunks, then use FAISS to find the closest matches.
        
        Args:
            query: The employee's question
            top_k: How many relevant chunks to return (5 is usually enough)
        
        Returns:
            List of the most relevant chunks with their source documents
        """
        print(f"\n🔍 Searching for: '{query}'")
        print(f"🔍 Looking for top {top_k} most relevant sections...")
        
        if self.index is None:
            print("❌ Search index not ready! Run build_vector_store() first.")
            return []
        
        # Convert the question into the same format as our document chunks
        query_embedding = self.model.encode([query], convert_to_tensor=False)
        
        # Find the closest matching chunks using FAISS
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Gather the results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            chunk_info = {
                'content': self.chunks[idx],
                'source': self.chunk_sources[idx]['source'],
                'distance': float(distance),  # Lower = more similar
                'rank': i + 1
            }
            results.append(chunk_info)
            
            print(f"   {i+1}. {chunk_info['source']} (similarity score: {distance:.2f})")
        
        print(f"✅ Found {len(results)} relevant sections")
        
        # Show which documents were helpful
        unique_sources = list(set(r['source'] for r in results))
        print(f"📚 Information from: {', '.join(unique_sources)}")
        
        return results
    
    
    def generate_response(self, query: str) -> Dict:
        """
        Answer an employee's question about HR policies.
        
        This is the full RAG pipeline:
        1. RETRIEVE: Find relevant policy chunks using semantic search
        2. AUGMENT: Give those chunks to the AI as context
        3. GENERATE: AI writes a natural answer based only on the policies
        
        Args:
            query: The employee's question (e.g., "How many vacation days do I get?")
        
        Returns:
            Dictionary with:
                - answer: The AI's response
                - sources: Which policy files were used
        """
        
        # Step 1: Find the most relevant policy sections
        retrieved_chunks = self.retrieve_relevant_chunks(query, top_k=5)
        
        if not retrieved_chunks:
            return {
                'answer': "I don't have any policy documents loaded yet. Upload some PDFs first!",
                'sources': []
            }
        
        # Step 2: Combine the relevant chunks into context for the AI
        context = "\n\n".join([
            f"[From {chunk['source']}]\n{chunk['content']}"
            for chunk in retrieved_chunks
        ])
        
        # Keep track of which files we're citing
        sources = list(set(chunk['source'] for chunk in retrieved_chunks))
        
        # Step 3: Ask the AI to answer based on the context
        prompt = f"""You are a helpful HR assistant. Answer the employee's question using ONLY the policy documents provided below.

HR Policy Context:
{context}

Employee Question: {query}

Instructions:
- Give a clear, helpful answer
- ONLY use information from the policy documents above
- Mention which policy document the info comes from (e.g., "According to leave_policy.pdf...")
- If the answer isn't in the policies, say so honestly

Answer:"""
        
        try:
            # Call Groq's LLM (Llama 3.3) to generate the answer
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful HR assistant. Only answer based on the provided policy documents. Never make up information."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            print(f"✅ Generated answer using: {', '.join(sources)}")
            
            return {
                'answer': answer,
                'sources': sources
            }
            
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return {
                'answer': f"Sorry, something went wrong: {str(e)}",
                'sources': []
            }