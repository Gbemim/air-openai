
"""
Career Agents - Individual agent definitions for AI Refinery
"""

# Standard library imports
import os
import sys

# Add db directory to path
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(backend_dir, 'db'))

# Third-party and local imports
from chunking import search_resume_content
from llm_auth import auth_manager
from openai_call import openai_call

# Track which agents are used
agents_used = set()

# === Agent Definitions ===

async def resume_search_agent(query: str, config: dict = None, **kwargs):
    """Search resume content using semantic vector search"""
    
    print(f"[AGENT] Resume Search Agent invoked")
    agents_used.add("Resume Search Agent")
    
    try:
        # Get configuration values with defaults
        config = config or {}
        vectordb_config = config.get('vectordb_config', {})
        top_k = vectordb_config.get('top_k', 5)
        
        # Include chat history context in search if provided
        enhanced_query = query

        # Extract session_id from query if present
        session_id = None
        if "session_id:" in enhanced_query:
            parts = enhanced_query.split("session_id:")
            session_id = parts[1].strip().split()[0] if len(parts) > 1 else None
            enhanced_query = parts[0].strip()

        # Search in OpenSearch using OpenAI embeddings with config-specified top_k
        results = search_resume_content(enhanced_query, session_id, k=top_k)
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



async def resume_assessment_agent(query: str, config: dict = None, **kwargs):
    """Assess resumes and provide actionable feedback"""
    
    print(f"[AGENT] Resume Assessment Agent invoked")
    agents_used.add("Resume Assessment Agent")

    # Get configuration values with defaults
    config = config or {}
    assessment_criteria = config.get('assessment_criteria', [])
    scoring_weights = config.get('scoring_weights', {})
    feedback_categories = config.get('feedback_categories', {})
    
    # Extract session_id from query if present
    session_id = None
    enhanced_query = query
    if "session_id:" in query:
        parts = query.split("session_id:")
        session_id = parts[1].strip().split()[0] if len(parts) > 1 else None
        enhanced_query = parts[0].strip()
    
    # Get resume content using semantic search
    if session_id:
        try:
            results = search_resume_content(enhanced_query, session_id, k=5)
            if results:
                resume_text = "\n\n".join([r['content'] for r in results])
                enhanced_query = f"{enhanced_query}\n\nHere is the user's resume content:\n{resume_text}"
            else:
                return "I don't see your resume. Please make sure a resume has been uploaded."
        except Exception as e:
            print(f"[ERROR] Failed to fetch resume content: {e}")
            return "I couldn't access your resume. Please make sure a resume has been uploaded and you have the right session ID."
    else:
        return "I don't see your resume. Please provide it to me, and I'll be able to give you a more accurate assessment of your skills and provide recommendations tailored to your experience."
    
    # Build assessment prompt based on config
    criteria_text = "\n".join([f"- {criterion.replace('_', ' ').title()} (Weight: {scoring_weights.get(criterion, 0.0) })" for criterion in assessment_criteria])

    prompt = f"""You are a career counselor analyzing a resume.

Provide:
1. **STRENGTHS** ({feedback_categories.get('strengths', 'Highlight positive aspects and standout elements')})

2. **IMPROVEMENTS** ({feedback_categories.get('improvements', 'Specific actionable recommendations')})

3. **MARKET READINESS** ({feedback_categories.get('market_readiness', 'Overall competitiveness assessment')}) 

4. **NEXT STEPS** ({feedback_categories.get('next_steps', 'Concrete actions to enhance the resume')})

**Assessment Criteria (with weights):**
{criteria_text}
For each criterion, use its scoring weight, for the level of weight each criteria has and apply it to each of the feedback categories.

Be concise, practical, and encouraging.


{enhanced_query}"""
    client = await auth_manager.get_air_client()
    response = await client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="meta-llama/Llama-3.1-70B-Instruct",
    )
    print(f"[DEBUG] Assessment criteria:\n{criteria_text}")
    return response.choices[0].message.content


async def job_search_agent(query: str, config: dict = None, **kwargs):
    """Help users find jobs online"""
    
    print(f"[AGENT] Job Search Agent invoked")
    agents_used.add("Job Search Agent")

    # Get configuration values with defaults
    config = config or {}
    search_platforms = config.get('search_platforms', [])
    search_strategies = config.get('search_strategies', {})
    job_categories = config.get('job_categories', [])
    
    # Extract session_id from query if present
    session_id = None
    enhanced_query = query
    if "session_id:" in query:
        parts = query.split("session_id:")
        session_id = parts[1].strip().split()[0] if len(parts) > 1 else None
        enhanced_query = parts[0].strip()
    
    # Get resume content using semantic search if session_id available
    if session_id:
        try:
            results = search_resume_content(enhanced_query, session_id, k=5)
            if results:
                resume_text = "\n\n".join([r['content'] for r in results])
                enhanced_query = f"{enhanced_query}\n\nHere is the user's background from their resume:\n{resume_text}"
        except Exception as e:
            print(f"[ERROR] Failed to fetch resume content: {e}")
    
    # Build platform and category lists for the prompt
    platforms_text = "\n".join([f"- {platform}" for platform in search_platforms])
    categories_text = "\n".join([f"- {category}" for category in job_categories])
    strategies_text = "\n".join([f"- {key.replace('_', ' ').title()}: {value}" for key, value in search_strategies.items()])
    
    prompt = f"""You are a job search expert. 

Based on the user's background, recommend from these platforms:
{platforms_text}

Consider these job categories:
{categories_text}

Apply these strategies:
{strategies_text}

Provide:
1. **SPECIFIC JOB SITES** (which platforms work best for their profile)
2. **SEARCH KEYWORDS** (exact terms to use)
3. **JOB TITLES** (5-7 titles they should search for)
4. **COMPANY TYPES** (what kinds of companies hire people like them)
5. **APPLICATION TIPS** (how to stand out)

Be specific and actionable.

{enhanced_query}"""

    client = await auth_manager.get_air_client()
    response = await client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="meta-llama/Llama-3.1-70B-Instruct",
    )
    return response.choices[0].message.content



async def interview_prep_agent(query: str, config: dict = None, **kwargs):
    """Help users prepare for interviews"""
    
    print(f"[AGENT] Interview Prep Agent invoked")
    agents_used.add("Interview Prep Agent")

    # Get configuration values with defaults
    config = config or {}
    interview_types = config.get('interview_types', ['Technical Interviews', 'Behavioral Interviews'])
    question_categories = config.get('question_categories', {})
    answer_frameworks = config.get('answer_frameworks', {})
    
    # Extract session_id from query if present
    session_id = None
    enhanced_query = query
    if "session_id:" in query:
        parts = query.split("session_id:")
        session_id = parts[1].strip().split()[0] if len(parts) > 1 else None
        enhanced_query = parts[0].strip()
    
    # Get resume content using semantic search if session_id available
    if session_id:
        try:
            results = search_resume_content(enhanced_query, session_id, k=5)
            if results:
                resume_text = "\n\n".join([r['content'] for r in results])
                enhanced_query = f"{enhanced_query}\n\nHere is the user's background from their resume:\n{resume_text}"
        except Exception as e:
            print(f"[ERROR] Failed to fetch resume content: {e}")
    
    # Build framework text for the prompt
    frameworks_text = "\n".join([f"- {name}: {description}" for name, description in answer_frameworks.items()])
    
    prompt = f"""You are an interview coach. 

Focus on these interview types: {', '.join(interview_types)}. You can exclude any of them if not relevant.

Use these answer frameworks:
{frameworks_text}

Help this person prepare:
1. **LIKELY QUESTIONS** (5-7 questions they'll probably be asked)
2. **HOW TO ANSWER** (structure for good responses using the frameworks above)
3. **QUESTIONS TO ASK** (5 good questions to ask the interviewer)
4. **KEY POINTS** (what to highlight from their background)
5. **COMMON MISTAKES** (what to avoid)

Be practical and specific.

{enhanced_query}"""

    client = await auth_manager.get_air_client()
    response = await client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="meta-llama/Llama-3.1-70B-Instruct",
    )
    return response.choices[0].message.content



async def general_career_agent(query: str, config: dict = None, **kwargs):
    """General career guidance using OpenAI"""
    
    print(f"[AGENT] General Career Agent invoked")
    agents_used.add("General Career Agent")

    # Get configuration values with defaults
    config = config or {}
    response_style = config.get('response_style', 'conversational')
    expertise_areas = config.get('expertise_areas', ['Career transitions', 'Skill development'])
    max_response_length = config.get('max_response_length', 500)
    
    # Extract session_id from query if present
    session_id = None
    enhanced_query = query
    if "session_id:" in query:
        parts = query.split("session_id:")
        session_id = parts[1].strip().split()[0] if len(parts) > 1 else None
        enhanced_query = parts[0].strip()
    
    # Get resume content using semantic search if session_id available
    if session_id:
        try:
            results = search_resume_content(enhanced_query, session_id, k=5)
            if results:
                resume_text = "\n\n".join([r['content'] for r in results])
                enhanced_query = f"{enhanced_query}\n\nHere is the user's background from their resume:\n{resume_text}"
        except Exception as e:
            print(f"[ERROR] Failed to fetch resume content: {e}")
    
    # Enhance query with config
    final_query = f"""
    Response Style: {response_style}
    Expertise Areas: {', '.join(expertise_areas)}
    Max Response Length: {max_response_length} words
        
    Current query: {enhanced_query}
    """

    return await openai_call(final_query)
