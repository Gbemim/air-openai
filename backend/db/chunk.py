from pdfminer.high_level import extract_text
import re
import os
from datetime import datetime
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from aws_opensearch import AWSOpenSearchClient

# Initialize clients when needed, not at module import
client = None
opensearch_client = None

def get_openai_client():
    global client
    if client is None:
        client = OpenAI()
    return client

def get_opensearch_client():
    global opensearch_client
    if opensearch_client is None:
        opensearch_client = AWSOpenSearchClient()
    return opensearch_client

def extract_resume_sections(pdf_file_path: str) -> List[str]:
    """Extract text from PDF and split into sections"""
    text = extract_text(pdf_file_path)
    # Split by the most common resume headers
    sections = re.split(
        r'\n(?=(?:Education|Experience|Work History|Skills|Projects|Certifications|Summary|Profile|Awards|Publications|Objective|Contact)\b)', 
        text, 
        flags=re.I
    )
    return [s.strip() for s in sections if len(s.strip()) > 50]

def chunk_resume_for_embed(sections: List[str]) -> List[str]:
    """Split resume sections into smaller chunks for embedding"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,   # ~700–800 tokens per chunk
        chunk_overlap=100, # small overlap for context continuity
        separators=["\n\n", "\n", ".", " "]
    )

    chunks = []
    for sec in sections:
        for chunk in splitter.split_text(sec):
            chunks.append(chunk)
    return chunks

def build_chunk_metadata(chunks: List[str], filename: str, session_id: str = None) -> List[Dict[str, Any]]:
    """Build metadata for each chunk"""
    return [
        {
            "id": f"resume_chunk_{session_id}_{i}" if session_id else f"resume_chunk_{i}",
            "content": chunk,
            "metadata": {
                "type": "resume", 
                "section": "auto", 
                "source": "pdf",
                "filename": filename,
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        }
        for i, chunk in enumerate(chunks)
    ]

def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """Generate embeddings for text chunks using OpenAI"""
    client = get_openai_client()
    embeddings = []
    for chunk in chunks:
        emb = client.embeddings.create(
            model="text-embedding-3-large",
            input=chunk
        )
        embeddings.append(emb.data[0].embedding)
    return embeddings

def process_resume_pipeline(pdf_file_path: str, filename: str, session_id: str = None) -> bool:
    """
    Complete pipeline to process resume PDF and store in OpenSearch
    Returns True if successful, False otherwise
    """
    try:
        # Step 1: Extract sections from PDF
        print(f"Extracting sections from {filename}...")
        sections = extract_resume_sections(pdf_file_path)
        
        # Step 2: Chunk the sections
        print("Chunking resume sections...")
        chunks = chunk_resume_for_embed(sections)
        
        # Step 3: Build metadata
        print("Building chunk metadata...")
        chunks_with_metadata = build_chunk_metadata(chunks, filename, session_id)
        
        # Step 4: Generate embeddings
        print("Generating embeddings...")
        embeddings = embed_chunks(chunks)
        
        # Step 5: Combine chunks with embeddings
        chunks_with_embeddings = []
        for i, chunk_data in enumerate(chunks_with_metadata):
            chunk_data["embedding"] = embeddings[i]
            chunks_with_embeddings.append(chunk_data)
        
        # Step 6: Store in OpenSearch
        print("Storing in OpenSearch...")
        opensearch_client = get_opensearch_client()
        success = opensearch_client.store_resume_chunks(chunks_with_embeddings, session_id)
        
        if success:
            print(f"Successfully processed resume: {filename}")
            return True
        else:
            print(f"Failed to store chunks for: {filename}")
            return False
            
    except Exception as e:
        print(f"Error processing resume {filename}: {str(e)}")
        return False

def search_resume_content(query: str, session_id: str = None, k: int = 5) -> List[Dict[str, Any]]:
    """
    Search resume content using semantic similarity
    """
    try:
        # Generate embedding for the query
        client = get_openai_client()
        query_embedding = client.embeddings.create(
            model="text-embedding-3-large",
            input=query
        ).data[0].embedding
        
        # Search in OpenSearch
        opensearch_client = get_opensearch_client()
        results = opensearch_client.search_resume_chunks(query_embedding, session_id, k)
        
        return results
        
    except Exception as e:
        print(f"Error searching resume content: {str(e)}")
        return []