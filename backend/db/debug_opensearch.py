#!/usr/bin/env python3
"""Debug script to check what's in OpenSearch"""

import sys
import os
from pathlib import Path

# Setup environment
sys.path.append(str(Path(__file__).parent))

from aws_opensearch import AWSOpenSearchClient

def main():
    try:
        client = AWSOpenSearchClient()
        
        # Get all documents
        query = {
            'query': {'match_all': {}},
            'size': 100,
            '_source': ['metadata']
        }
        
        response = client.client.search(index=client.index_name, body=query)
        
        total = response['hits']['total']['value']
        print(f"\n📊 Total documents in OpenSearch: {total}\n")
        
        if total == 0:
            print("❌ No documents found in OpenSearch!")
            print("   The resume may not have been processed correctly.")
            return
        
        # Group by session_id
        sessions = {}
        for hit in response['hits']['hits']:
            session_id = hit['_source']['metadata'].get('session_id', 'unknown')
            filename = hit['_source']['metadata'].get('filename', 'unknown')
            
            if session_id not in sessions:
                sessions[session_id] = {
                    'count': 0,
                    'filename': filename
                }
            sessions[session_id]['count'] += 1
        
        print("📁 Documents grouped by session_id:\n")
        for session_id, info in sessions.items():
            print(f"   Session: {session_id}")
            print(f"   File: {info['filename']}")
            print(f"   Chunks: {info['count']}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
