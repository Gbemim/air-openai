"""
Career Agents using AI Refinery SDK + AWS OpenSearch
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
backend_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(backend_dir, '.env'))

# Add db directory to path for OpenSearch client
sys.path.append(os.path.join(backend_dir, 'db'))
from chunking import search_resume_content

# Import centralized authentication
from auth import auth_manager

# Module configuration (moved from __init__.py)
from pathlib import Path
CONFIG_PATH = Path(__file__).parent / 'config.yaml'
PROJECT_NAME = 'career_agents'

# Import OpenAI agent for general career guidance
from openai_agent import simple_agent

# Resume Search Agent (uses OpenAI + AWS OpenSearch)
async def resume_search_agent(query: str):
    """Search resume content using semantic vector search"""
    try:
        # Extract session_id from query if present
        session_id = None
        if "session_id:" in query:
            parts = query.split("session_id:")
            session_id = parts[1].strip().split()[0] if len(parts) > 1 else None
            query = parts[0].strip()
        
        # Search in OpenSearch using OpenAI embeddings
        results = search_resume_content(query, session_id, k=5)
        
        if not results:
            return "No resume content found. Please make sure a resume has been uploaded."
        
        # Format results
        context = "\n\n".join([
            f"**Section {i+1}:**\n{result['content']}\n(Score: {result.get('score', 'N/A')})"
            for i, result in enumerate(results)
        ])
        
        return f"Found relevant resume content:\n\n{context}"
        
    except Exception as e:
        return f"Error searching resume: {str(e)}"


# Resume Assessment Agent
async def resume_assessment_agent(query: str):
    """Assess resumes and provide actionable feedback"""
    prompt = f"""You are a career counselor. Analyze the resume and provide:

1. **STRENGTHS** (2-3 key strengths)
2. **IMPROVEMENTS** (2-3 specific areas to improve)
3. **MARKET READINESS** (score 1-10 with brief explanation)
4. **NEXT STEPS** (3 actionable recommendations)

Be concise, practical, and encouraging.

{query}"""
    
    client = await auth_manager.get_air_client()
    response = await client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="meta-llama/Llama-3.1-70B-Instruct",
    )
    return response.choices[0].message.content


# Job Search Agent
async def job_search_agent(query: str):
    """Help users find jobs online"""
    prompt = f"""You are a job search expert. Based on the user's background, tell them:

1. **SPECIFIC JOB SITES** (which platforms work best for their profile)
2. **SEARCH KEYWORDS** (exact terms to use)
3. **JOB TITLES** (5-7 titles they should search for)
4. **COMPANY TYPES** (what kinds of companies hire people like them)
5. **APPLICATION TIPS** (how to stand out)

Be specific and actionable.

{query}"""
    
    client = await auth_manager.get_air_client()
    response = await client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="meta-llama/Llama-3.1-70B-Instruct",
    )
    return response.choices[0].message.content


# Interview Prep Agent
async def interview_prep_agent(query: str):
    """Help users prepare for interviews"""
    prompt = f"""You are an interview coach. Help this person prepare:

1. **LIKELY QUESTIONS** (5-7 questions they'll probably be asked)
2. **HOW TO ANSWER** (structure for good responses)
3. **QUESTIONS TO ASK** (5 good questions to ask the interviewer)
4. **KEY POINTS** (what to highlight from their background)
5. **COMMON MISTAKES** (what to avoid)

Be practical and specific.

{query}"""
    
    client = await auth_manager.get_air_client()
    response = await client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="meta-llama/Llama-3.1-70B-Instruct",
    )
    return response.choices[0].message.content


# General Career Agent (uses OpenAI GPT-4)
async def general_career_agent(query: str):
    """General career guidance using OpenAI"""
    return await simple_agent(query)


class CareerAgents:
    """Career agents using AI Refinery orchestrator"""
    def __init__(self):
        self.project_name = PROJECT_NAME
        self.config_path = CONFIG_PATH
        self.distiller_client = None
    
    async def initialize(self):
        """Initialize the AI Refinery project"""
        # Get distiller client from auth manager
        self.distiller_client = auth_manager.get_distiller_client()
        
        # Create or update project
        try:
            self.distiller_client.create_project(
                config_path=str(self.config_path),
                project=self.project_name
            )
            print(f"✅ Project '{self.project_name}' initialized")
        except Exception as e:
            # Project might already exist, that's OK
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
                # Search for relevant resume content based on the message
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
        
        # Create wrapper functions that include resume context
        async def resume_search_with_context(query: str):
            return await resume_search_agent(query)
        
        async def resume_assessment_with_context(query: str):
            if resume_sections_data:
                # Add resume data to the query
                resume_text = "\n\n".join([r['content'] for r in resume_sections_data])
                enhanced_query = f"{query}\n\nHere is the user's resume content:\n{resume_text}"
                return await resume_assessment_agent(enhanced_query)
            else:
                return "I don't see your resume. Please provide it to me, and I'll be able to give you a more accurate assessment of your skills and provide recommendations tailored to your experience."
        
        async def job_search_with_context(query: str):
            if resume_sections_data:
                # Add resume data to the query
                resume_text = "\n\n".join([r['content'] for r in resume_sections_data])
                enhanced_query = f"{query}\n\nHere is the user's background from their resume:\n{resume_text}"
                return await job_search_agent(enhanced_query)
            else:
                return await job_search_agent(query)
        
        async def interview_prep_with_context(query: str):
            if resume_sections_data:
                # Add resume data to the query
                resume_text = "\n\n".join([r['content'] for r in resume_sections_data])
                enhanced_query = f"{query}\n\nHere is the user's background from their resume:\n{resume_text}"
                return await interview_prep_agent(enhanced_query)
            else:
                return await interview_prep_agent(query)
        
        async def general_career_with_context(query: str):
            if resume_sections_data:
                # Add resume data to the query
                resume_text = "\n\n".join([r['content'] for r in resume_sections_data])
                enhanced_query = f"{query}\n\nHere is the user's background from their resume:\n{resume_text}"
                return await general_career_agent(enhanced_query)
            else:
                return await general_career_agent(query)
        
        # Define executor dictionary mapping agent names to functions
        executor_dict = {
            "Resume Search Agent": resume_search_with_context,
            "Resume Assessment Agent": resume_assessment_with_context,
            "Job Search Agent": job_search_with_context,
            "Interview Prep Agent": interview_prep_with_context,
            "General Career Agent": general_career_with_context,
        }
        
        # Connect and query
        async with self.distiller_client(
            project=self.project_name,
            uuid=user_id,
            executor_dict=executor_dict
        ) as dc:
            responses = await dc.query(query=enhanced_message)
            
            # Collect all response chunks
            full_response = ""
            async for response in responses:
                full_response += response.get('content', '')
            
            return full_response


# Simple function for easy use
async def ask_agents(message: str, user_id: str = "user", session_id: str = None) -> str:
    """Simple function to ask the career agents"""
    agents = CareerAgents()
    return await agents.chat(message, user_id, session_id)
