"""
Enhanced web interface for Career Agents with AWS OpenSearch integration
"""

import asyncio
import sys
import os
from agents import ask_agents

from db.chunking import search_resume_content

async def handle_chat(user_message: str, user_id: str = "user", session_id: str = None):
    """
    Handle chat with optional session_id for resume-specific queries
    
    The system will:
    1. Search OpenSearch for resume context (if session_id provided)
    2. Add resume context to the message
    3. AI Refinery orchestrator routes to appropriate agent
    4. Agent processes with full context
    """
    try:
        # Pass session_id directly to ask_agents so it can fetch resume context
        response = await ask_agents(user_message, user_id, session_id)
        return {
            'success': True,
            'response': response,
            'service': 'AI Refinery (Orchestrator) + AWS OpenSearch + OpenAI'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def search_resume(query: str, session_id: str = None):
    """
    Direct vector search in resume content
    Uses: OpenAI embeddings + AWS OpenSearch
    """
    try:
        results = search_resume_content(query, session_id, k=5)
        
        if not results:
            return {
                'success': False,
                'message': 'No resume content found. Please upload a resume first.'
            }
        
        return {
            'success': True,
            'results': results,
            'count': len(results),
            'service': 'OpenAI Embeddings + AWS OpenSearch'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
