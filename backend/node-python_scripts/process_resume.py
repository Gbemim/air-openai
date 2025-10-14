#!/usr/bin/env python3
"""
Script to process resume PDF through the chunking and embedding pipeline
Called from Node.js upload route
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add the db directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / 'db'))

try:
    from chunk import process_resume_pipeline
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print("Usage: python process_resume.py <file_path> <filename> [session_id]", file=sys.stderr)
        sys.exit(1)
    
    file_path = sys.argv[1]
    filename = sys.argv[2]
    session_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Process the resume through the pipeline
        success = process_resume_pipeline(file_path, filename, session_id)
        
        result = {
            "success": success,
            "file_path": file_path,
            "filename": filename,
            "session_id": session_id,
            "processed_at": datetime.now().isoformat(),
            "pipeline_steps": [
                "PDF text extraction",
                "Section chunking", 
                "Metadata building",
                "Embedding generation",
                "OpenSearch storage"
            ]
        }
        
        print(json.dumps(result))
        
        if success:
            sys.exit(0)
        else:
            print("Processing failed", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error processing resume: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()