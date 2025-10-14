#!/usr/bin/env python3
"""
Script to get all resume data for a specific session
Called from Node.js upload route
"""

import sys
import json
from pathlib import Path

# Add the db directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / 'db'))

try:
    from aws_opensearch import AWSOpenSearchClient
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python get_session_data.py <session_id>", file=sys.stderr)
        sys.exit(1)
    
    session_id = sys.argv[1]
    
    try:
        client = AWSOpenSearchClient()
        chunks = client.get_session_chunks(session_id)
        
        result = {
            "session_id": session_id,
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
        
        print(json.dumps(result, indent=2))
        sys.exit(0)
        
    except Exception as e:
        print(f"Error getting session data: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()