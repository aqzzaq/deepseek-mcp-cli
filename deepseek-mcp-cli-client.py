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
        "When executing commands, always confirm with the user before running them.",
        "MANDATORY: Document every step you were asked to do and have executed with a datetimestamp. Append the content into worklog.log file before execution."
    ]
}


async def run(query, message_history=None, preset=None):
    # Use default preset if none provided
    if preset is None:
        preset = DEFAULT_PRESET
        
    # Initialize message history if not provided
    if message_history is None:
        message_history = []
        
        # Add preset to message history as system prompt
        system_message = f"ROLE: {preset['role']}\n"
        system_message += "INSTRUCTIONS:\n"
        for instruction in preset['instructions']:
            system_message += f"- {instruction}\n"
        message_history.append(("system", system_message.strip()))
        
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
