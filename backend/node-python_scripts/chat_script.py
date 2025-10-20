#!/usr/bin/env python3
"""
Script to handle chat messages through AI Refinery
Called from Node.js conversations route
Includes web interface functionality
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# pretty markdown rendering
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Add air_llm directory to path
sys.path.append(str(Path(__file__).parent.parent / 'air_llm'))

# Add db directory to path
backend_dir = str(Path(__file__).parent.parent)
sys.path.append(os.path.join(backend_dir, 'db'))

try:
    from orchestrator import ask_agents
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)

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
        response, agents_used = await ask_agents(user_message, user_id, session_id)
        return {
            'success': True,
            'response': response,
            'agents_used': list(agents_used),
            'service': 'AI Refinery (Orchestrator) + AWS OpenSearch + OpenAI'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python chat.py <message> <user_id> [session_id] [--json|--pretty]"
        }))
        sys.exit(1)
    
    message = sys.argv[1]
    user_id = sys.argv[2]
    session_id = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else None
    
    # output format
    output_format = 'json' 
    if '--pretty' in sys.argv:
        output_format = 'pretty'
    elif '--json' in sys.argv:
        output_format = 'json'
    
    try:
        # Run async chat handler
        result = asyncio.run(handle_chat(message, user_id, session_id))
        
        # Terminal output based on format
        if output_format == 'pretty' and RICH_AVAILABLE:
            # Pretty markdown rendering for terminal viewing
            console = Console()
            
            if result.get('success'):
                console.print("\n")
                console.print(Panel.fit("Success", style="bold green"))
                
                # Render the LLM response as markdown
                console.print("\n[bold cyan]Response:[/bold cyan]")
                md = Markdown(result['response'])
                console.print(md)
                
                console.print(f"\n[bold blue]Agents Used:[/bold blue] [yellow]{', '.join(result['agents_used'])}[/yellow]")
                console.print(f"[bold blue]Service:[/bold blue] {result['service']}\n")
            else:
                console.print("\n")
                console.print(Panel.fit("Error", style="bold red"))
                console.print(f"[red]{result.get('error', 'Unknown error')}[/red]\n")
        else:
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
