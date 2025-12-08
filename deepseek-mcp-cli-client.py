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
        "MANDATORY: When executing commands, always confirm with the user before running them.",
        "MANDATORY: Avoid interactive sessions or commands that require user input during execution as they will cause the CLI to get stuck.",
        "MANDATORY: Document every step you execute with a datetimestamp. Note: All user requests are automatically logged to the worklog file.",
        "MANDATORY: Use the unique log filename provided in the system message for all worklog entries.",
        "MANDATORY: When using tools that support it, always pass the correct log_filename parameter.",
        "MANDATORY: All worklog entries must be appended to the specified log file before execution."
    ]
}


async def run(query, message_history=None, preset=None):
    import datetime
    import re
    
    # Use default preset if none provided
    if preset is None:
        preset = DEFAULT_PRESET
        
    # Initialize message history if not provided or extract log filename if it exists
    log_filename = None
    if message_history is None:
        message_history = []
        
        # Generate unique log filename for this session
        session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"worklog_{session_id}.log"
        
        # Add preset to message history as system prompt
        system_message = f"ROLE: {preset['role']}\n"
        system_message += "INSTRUCTIONS:\n"
        for instruction in preset['instructions']:
            system_message += f"- {instruction}\n"
        # Add log filename requirement to system message
        system_message += f"\nMANDATORY: All worklog entries must use this filename: {log_filename}"
        message_history.append(("system", system_message.strip()))
        
        print(f"\n=== Session Started ===")
        print(f"Log file: {log_filename}")
    else:
        # Extract log filename from existing system message
        for role, content in message_history:
            if role == "system":
                match = re.search(r"MANDATORY: All worklog entries must use this filename: (worklog_\d{8}_\d{6}\.log)", content)
                if match:
                    log_filename = match.group(1)
                    break
        
        # Generate a new log filename if none found (should rarely happen)
        if not log_filename:
            session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"worklog_{session_id}.log"
    
    # Log every user request, not just the first one
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_filename, "a") as f:
            f.write(f"[{timestamp}] USER REQUEST: {query}\n")
    except Exception as e:
        print(f"Warning: Failed to log user request: {e}")
    
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
            
            # Create agent and invoke with message history
            agent = create_agent(llm, tools)
            
            # Add current user query to message history
            message_history.append(("human", query))
            result = await agent.ainvoke({"messages": message_history.copy()})
            
            # Extract the final AI response
            ai_response = result["messages"][-1]
            
            # Add AI response to message history
            message_history.append((ai_response.type, ai_response.content))
            
            print("\n=== Result ===")
            print(ai_response.content)
            
            return message_history

if __name__ == "__main__":
    print("=== Deepseek MCP CLI Client ===")
    print("Type 'exit' to quit.")
    print("\nEnter your command or query:")
    
    # If command line argument is provided, use it as the query (no history)
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        asyncio.run(run(query))
    else:
        # Interactive mode with context memory
        message_history = None
        
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
