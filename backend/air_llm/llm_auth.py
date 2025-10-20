"""
Authentication and client management for AI Refinery and OpenAI
"""

import os
from air import AsyncAIRefinery, DistillerClient
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIAuthManager:
    """Centralized authentication and client management"""
    
    def __init__(self):
        self.air_api_key = os.getenv('AIR_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self._air_client = None
        self._openai_client = None
        self._distiller_client = None
        
        # Validate API keys
        if not self.air_api_key:
            raise ValueError("AIR_API_KEY not found in environment variables")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    async def get_air_client(self) -> AsyncAIRefinery:
        """Get AI Refinery async client"""
        if self._air_client is None:
            self._air_client = AsyncAIRefinery(api_key=self.air_api_key)
        return self._air_client
    
    def get_openai_client(self) -> OpenAI:
        """Get OpenAI client"""
        if self._openai_client is None:
            self._openai_client = OpenAI(api_key=self.openai_api_key)
        return self._openai_client

    def get_distiller_client(self) -> DistillerClient:
        """Get AI Refinery Distiller client for orchestration"""
        if self._distiller_client is None:
            self._distiller_client = DistillerClient(api_key=self.air_api_key)
        return self._distiller_client
    

# Global auth manager instance
auth_manager = AIAuthManager()