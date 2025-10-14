"""
Simple AI agent using OpenAI GPT models
"""

from auth import auth_manager

# Simple function for general career guidance using OpenAI
async def simple_agent(query: str):
    """
    Simple agent function using OpenAI GPT-4
    """
    try:
        openai_client = auth_manager.get_openai_client()
        
        # Enhanced career guidance prompt
        system_prompt = """You are a professional career counselor and advisor. Provide helpful, practical, and actionable career guidance. 

Guidelines:
- Be encouraging but realistic
- Provide specific, actionable advice
- Consider current job market trends
- Focus on practical next steps
- Be concise but thorough

Respond in a friendly, professional tone."""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in simple agent: {e}")
        return f"Error processing query: {str(e)}"
