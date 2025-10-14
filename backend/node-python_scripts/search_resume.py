#!/usr/bin/env python3
"""
Script to search resume content using semantic similarity
Called from Node.js upload route
"""

import sys
import json
from pathlib import Path

# Add the db directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / 'db'))

try:
    from chunk import search_resume_content
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_resume.py <query> [k] [session_id]", file=sys.stderr)
        sys.exit(1)
    
    query = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    session_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        results = search_resume_content(query, session_id, k)
        print(json.dumps(results, indent=2))
        sys.exit(0)
        
    except Exception as e:
        print(f"Error searching resume content: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()