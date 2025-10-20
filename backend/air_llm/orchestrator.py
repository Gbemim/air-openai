"""
Career Agents Orchestrator using AI Refinery SDK
"""

# Standard library imports
import os
import sys
import yaml
from pathlib import Path

# Add db directory to path
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(backend_dir, 'db'))

# Third-party and local imports
from chunking import search_resume_content
from llm_auth import auth_manager
from agents import (
    resume_search_agent,
    resume_assessment_agent,
    job_search_agent,
    interview_prep_agent,
    general_career_agent,
    agents_used
)

# Module configuration
CONFIG_PATH = Path(__file__).parent / 'config.yaml'
PROJECT_NAME = 'career_agents'


class CareerAgents:
    """Career agents using AI Refinery orchestrator"""
    def __init__(self):
        self.project_name = PROJECT_NAME
        self.config_path = CONFIG_PATH
        self.distiller_client = None

    async def initialize(self):
        """Initialize the AI Refinery project"""
        self.distiller_client = auth_manager.get_distiller_client()
        
        try:
            self.distiller_client.create_project(
                config_path=str(self.config_path),
                project=self.project_name
            )
            print(f"✅ Project '{self.project_name}' initialized")
        except Exception as e:
            print(f"Note: {e}")

    async def chat(self, message: str, user_id: str = "user", session_id: str = None):
        """Chat with the career agents - orchestrator handles routing"""
        if not self.distiller_client:
            await self.initialize()

        # Get resume context from OpenSearch if session_id provided
        resume_context = ""
        resume_sections_data = []
        print(f"[DEBUG] Chat called with session_id: {session_id}")

        if session_id:
            try:
                print(f"[DEBUG] Searching for resume content with session_id: {session_id}")
                results = search_resume_content(message, session_id, k=3)
                print(f"[DEBUG] Search results: {len(results)} chunks found")
                if results:
                    resume_sections_data = results
                    resume_sections = "\n\n".join([
                        f"Resume Section:\n{result['content']}"
                        for result in results[:3]
                    ])
                    resume_context = f"\n\nUser's Resume Context:\n{resume_sections}\n"
                    print(f"[DEBUG] Resume context found and added to message")
                else:
                    print(f"[DEBUG] No resume content found for session_id: {session_id}")
            except Exception as e:
                print(f"[ERROR] Could not fetch resume context: {e}")
                import traceback
                traceback.print_exc()

        # Prepend resume context to the message if available
        enhanced_message = message
        if resume_context:
            enhanced_message = f"{message}{resume_context}"

        # Append session_id to message so agents can extract it
        if session_id:
            enhanced_message = f"{enhanced_message} session_id:{session_id}"

        # Executor dictionary
        executor_dict = {
            "Resume Assessment Agent": resume_assessment_agent,
            "Job Search Agent": job_search_agent,
            "Interview Prep Agent": interview_prep_agent,
            "General Career Agent": general_career_agent,
        }

        # Connect and query
        async with self.distiller_client(
            project=self.project_name,
            uuid=user_id,
            executor_dict=executor_dict
        ) as dc:
            # Add orchestrator to agents used
            agents_used.add("Orchestrator")

            responses = await dc.query(query=enhanced_message)
            full_response = ""
            async for response in responses:
                full_response += response.get('content', '')
            
            return full_response, agents_used


# === Public/terminal tester call ===

async def ask_agents(message: str, user_id: str = "user", session_id: str = None):
    """Simple function to ask the career agents"""
    agents = CareerAgents()
    return await agents.chat(message, user_id, session_id)
