#!/usr/bin/env python3
"""
Script to list all uploaded files and their session associations
Useful for debugging and manual cleanup
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

def list_all_files_and_sessions():
    """List all files and their associated sessions from OpenSearch"""
    try:
        client = AWSOpenSearchClient()
        
        query = {
            "query": {"match_all": {}},
            "_source": ["metadata.filename", "metadata.session_id", "metadata.created_at"],
            "size": 1000,
            "sort": [{"metadata.created_at": {"order": "desc"}}]
        }
        
        response = client.client.search(index=client.index_name, body=query)
        
        files_by_session = {}
        
        for hit in response['hits']['hits']:
            metadata = hit['_source'].get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            session_id = metadata.get('session_id', 'Unknown')
            created_at = metadata.get('created_at', 'Unknown')
            
            if session_id not in files_by_session:
                files_by_session[session_id] = []
            
            files_by_session[session_id].append({
                'filename': filename,
                'created_at': created_at,
                'document_id': hit['_id']
            })
        
        return {
            'total_sessions': len(files_by_session),
            'total_documents': response['hits']['total']['value'],
            'sessions': files_by_session
        }
        
    except Exception as e:
        print(f"Error listing files: {e}", file=sys.stderr)
        return {'error': str(e)}

def main():
    try:
        result = list_all_files_and_sessions()
        print(json.dumps(result, indent=2))
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()