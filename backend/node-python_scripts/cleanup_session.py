#!/usr/bin/env python3
"""
Script to clean up session data from OpenSearch and file system
Called from Node.js when a session is deleted or expires
"""

import sys
import json
import os
import glob
from pathlib import Path

# Add the db directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / 'db'))

try:
    from aws_opensearch import AWSOpenSearchClient
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)

def cleanup_session_files(session_id: str, uploads_dir: str, client: AWSOpenSearchClient):
    """Delete all files associated with a session using existing OpenSearch methods"""
    deleted_files = []
    
    try:
        # Use existing method to get session chunks
        chunks = client.get_session_chunks(session_id)
        
        # Extract unique original filenames from chunks
        original_filenames = []
        for chunk in chunks:
            filename = chunk.get('metadata', {}).get('filename', '')
            if filename and filename not in original_filenames:
                original_filenames.append(filename)
        
        # Find and delete files that end with the original filename
        for original_filename in original_filenames:
            # Look for files that end with the original filename
            for actual_filename in os.listdir(uploads_dir):
                if actual_filename.endswith(original_filename):
                    file_path = os.path.join(uploads_dir, actual_filename)
                    try:
                        os.remove(file_path)
                        deleted_files.append(actual_filename)  # Store the actual filename that was deleted
                        break  # Only delete the first match
                    except Exception as e:
                        # Don't print error, just continue
                        pass
        
        return deleted_files
    except Exception as e:
        return deleted_files

def main():
    if len(sys.argv) < 2:
        print("Usage: python cleanup_session.py <session_id> [uploads_dir]", file=sys.stderr)
        sys.exit(1)
    
    session_id = sys.argv[1]
    uploads_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    cleanup_result = {
        "session_id": session_id,
        "opensearch_deleted": 0,
        "files_deleted": [],
        "success": True,
        "errors": []
    }
    
    try:
        # Initialize OpenSearch client
        client = AWSOpenSearchClient()
        
        # Delete associated files first (get filenames from OpenSearch before deleting)
        if uploads_dir:
            deleted_files = cleanup_session_files(session_id, uploads_dir, client)
            cleanup_result["files_deleted"] = deleted_files
        
        # Delete from OpenSearch using existing method
        deleted_count = client.delete_session_data(session_id)
        cleanup_result["opensearch_deleted"] = deleted_count
        
        # Only output JSON for Node.js parsing
        print(json.dumps(cleanup_result, indent=2))
        sys.exit(0)
        
    except Exception as e:
        cleanup_result["success"] = False
        cleanup_result["errors"].append(str(e))
        print(f"Error during cleanup: {str(e)}", file=sys.stderr)
        print(json.dumps(cleanup_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()