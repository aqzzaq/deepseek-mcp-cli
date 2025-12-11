import os
import asyncio
import sys
from langchain_deepseek import ChatDeepSeek
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate


server_params = StdioServerParameters(command="python", args=["deepseek-mcp-cli-server.py"])

if not os.getenv("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = "" # Input Deepseek api key.

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Default preset - can be customized by user
DEFAULT_PRESET = {
    "role": "Helpful CLI Assistant",
    "instructions": [
        "You are a helpful CLI assistant that can execute commands and perform file operations.",
        "Always be clear and concise in your responses.",
        "Use the available tools to accomplish tasks when needed.",
        "If you don't know how to answer or complete a task, be honest about it.",
        "When executing commands, ensure they are safe and appropriate.",
        "Provide clear explanations of what you're doing and why.",
        "MANDATORY: Avoid interactive sessions or commands that require user input during execution as they will cause the CLI to get stuck.",
        "MANDATORY: Document every step you execute and its corresponding result with a datetimestamp.",
        "MANDATORY: For every response, document concised summary of the result in log file",
        "MANDATORY: Use the unique log filename provided in the system message for all worklog entries.",
        "MANDATORY: When using tools that support it, always pass the correct log_filename parameter."
    ]
}


async def run(query, message_history=None, preset=None, log_filename=None):
    import datetime
    import re
    import os
    
    # Use default preset if none provided
    if preset is None:
        preset = DEFAULT_PRESET
        
    # Initialize session parameters
    system_message = None
    
    if message_history is None:
        # Check if log_filename is provided and exists
        if log_filename and os.path.exists(log_filename):
            print(f"\n=== Session Continued ===")
            print(f"Loading from log file: {log_filename}")
        
        # Generate new log filename if not provided
        if not log_filename:
            session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"worklog_{session_id}.log"
            print(f"\n=== Session Started ===")
            print(f"Log file: {log_filename}")
        
        # Create system message with preset instructions and log filename
        system_message = f"ROLE: {preset['role']}\n"
        system_message += "INSTRUCTIONS:\n"
        for instruction in preset['instructions']:
            system_message += f"- {instruction}\n"
        system_message += f"\nMANDATORY: All worklog entries must use this filename: {log_filename}"
        
        # Initialize message history with just the system message
        message_history = [("system", system_message.strip())]
    else:
        # Extract system message and log filename
        for role, content in message_history:
            if role == "system":
                system_message = content
                match = re.search(r"MANDATORY: All worklog entries must use this filename: (.+)", content)
                if match:
                    log_filename = match.group(1)
                    break
        
        # Generate a new log filename if none found (should rarely happen)
        if not log_filename:
            session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"worklog_{session_id}.log"
    
    # Log current user request
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_filename, "a") as f:
            f.write(f"[{timestamp}] USER REQUEST: {query}\n")
    except Exception as e:
        print(f"Warning: Failed to log user request: {e}")
    
    # Read worklog content to use as context
    worklog_context = ""
    try:
        with open(log_filename, "r") as f:
            worklog_content = f.read()
        if worklog_content:
            worklog_context = "\n\n--- PREVIOUS INTERACTIONS (FROM WORKLOG) ---\n" + worklog_content + "\n--- END OF PREVIOUS INTERACTIONS ---"
    except FileNotFoundError:
        # Worklog might not exist yet for first interaction
        pass
    except Exception as e:
        print(f"Warning: Failed to read worklog context: {e}")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            
            # Only show tools on first run
            if len(message_history) == 1:  # Only system message
                print("\nAvailable tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
                print()
            
            # Create a minimal message history with just the system message and current query
            # The worklog_context provides the previous interactions as context
            minimal_history = [("system", system_message.strip() + worklog_context)]
            minimal_history.append(("human", query))
            
            # Create agent and invoke with minimal history + worklog context
            agent = create_agent(llm, tools)
            result = await agent.ainvoke({"messages": minimal_history.copy()})
            
            # Extract the final AI response
            ai_response = result["messages"][-1]
            
            # Add AI response to message history
            message_history.append((ai_response.type, ai_response.content))
            
            print("\n=== Result ===")
            print(ai_response.content)
            
            # Return only the system message (not the full history) to reduce memory usage
            return [("system", system_message.strip())]

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Deepseek MCP CLI Client")
    parser.add_argument("-l", "--log", help="Path to existing worklog file to continue conversation from")
    parser.add_argument("query", nargs="*", help="Initial query (optional)")
    args = parser.parse_args()
    
    print("=== Deepseek MCP CLI Client ===")
    print("Type 'exit' to quit.")
    print("\nEnter your command or query:")
    
    # Initialize message_history
    message_history = None
    
    # If an initial query is provided, run it first
    if args.query:
        query = " ".join(args.query)
        message_history = asyncio.run(run(query, message_history, log_filename=args.log))
    
    # Start interactive mode
    # If we already processed a query, we'll continue from there
    # Otherwise, we'll start fresh with the provided log file (if any)
    while True:
        try:
            query = input(">>> ")
            if query.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            if query.strip():
                # Update message history with each interaction
                message_history = asyncio.run(run(query, message_history))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
