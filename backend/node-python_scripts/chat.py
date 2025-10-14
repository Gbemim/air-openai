#!/usr/bin/env python3
"""
Script to handle chat messages through AI Refinery
Called from Node.js conversations route
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add air_llm directory to path
sys.path.append(str(Path(__file__).parent.parent / 'air_llm'))

try:
    from web_enhanced import handle_chat
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)

async def process_chat(message, user_id, session_id=None):
    """Process chat message through AI Refinery"""
    try:
        result = await handle_chat(message, user_id, session_id)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python chat.py <message> <user_id> [session_id]"
        }))
        sys.exit(1)
    
    message = sys.argv[1]
    user_id = sys.argv[2]
    session_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        # Run async chat handler
        result = asyncio.run(process_chat(message, user_id, session_id))
        
        # Output result as JSON
        print(json.dumps(result))
        
        if result.get('success'):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Error processing chat: {str(e)}"
        }), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
