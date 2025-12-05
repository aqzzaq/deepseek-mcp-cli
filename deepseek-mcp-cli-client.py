import os
import asyncio
import sys
from langchain_deepseek import ChatDeepSeek
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent


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


async def run(query):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            print("\nAvailable tools:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            agent = create_react_agent(llm, tools)
            result = await agent.ainvoke({"messages": [("human", query)]})
            print("\n=== Result ===")
            print(result["messages"][-1].content)

if __name__ == "__main__":
    print("=== Deepseek MCP CLI Client ===")
    print("Type 'exit' to quit.")
    print("\nEnter your command or query:")
    
    # If command line argument is provided, use it as the query
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        asyncio.run(run(query))
    else:
        # Interactive mode
        while True:
            try:
                query = input(">>> ")
                if query.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break
                if query.strip():
                    asyncio.run(run(query))
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break