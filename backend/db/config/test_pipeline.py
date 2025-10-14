#!/usr/bin/env python3
"""
Test script to validate the resume processing pipeline
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)
print(f"Loading environment from: {env_path}")

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from chunk import (
            extract_resume_sections, 
            chunk_resume_for_embed, 
            build_chunk_metadata,
            embed_chunks,
            process_resume_pipeline,
            search_resume_content
        )
        print("✓ chunk.py imports successful")
    except ImportError as e:
        print(f"✗ chunk.py import failed: {e}")
        return False
    
    try:
        from aws_opensearch import AWSOpenSearchClient
        print("✓ aws_opensearch.py imports successful")
    except ImportError as e:
        print(f"✗ aws_opensearch.py import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test that required environment variables are set"""
    print("\nTesting environment variables...")
    
    required_vars = [
        'AWS_REGION',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'OPENSEARCH_ENDPOINT', 
        'OPENAI_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            # Show partial value for verification
            if 'KEY' in var or 'SECRET' in var:
                print(f"  {var}: {value[:10]}...{value[-4:] if len(value) > 14 else ''}")
            else:
                print(f"  {var}: {value}")
    
    if missing:
        print(f"✗ Missing environment variables: {', '.join(missing)}")
        print("Please set these in your .env file")
        return False
    else:
        print("✓ All required environment variables are set")
        return True

def test_opensearch_connection():
    """Test OpenSearch connection"""
    print("\nTesting OpenSearch connection...")
    
    try:
        from aws_opensearch import AWSOpenSearchClient
        client = AWSOpenSearchClient()
        
        # Try to get cluster info
        info = client.client.info()
        print(f"✓ Connected to OpenSearch cluster: {info.get('cluster_name', 'Unknown')}")
        return True
        
    except Exception as e:
        print(f"✗ OpenSearch connection failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI API connection...")
    
    try:
        from openai import OpenAI
        client = OpenAI()
        
        # Test embedding generation
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input="test text"
        )
        
        if response.data[0].embedding:
            print(f"✓ OpenAI API working - embedding dimension: {len(response.data[0].embedding)}")
            return True
        else:
            print("✗ OpenAI API returned empty embedding")
            return False
            
    except Exception as e:
        print(f"✗ OpenAI API connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Resume Processing Pipeline Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_environment,
        test_opensearch_connection,
        test_openai_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Pipeline is ready to use.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Please check the configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()