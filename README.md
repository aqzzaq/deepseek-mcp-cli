# Deepseek-CLI-Tool-Framework

## Intro
This is a CLI tool built using MCP (Model Control Protocol) and LangChain with Deepseek LLM integration. It provides a foundation for creating intelligent CLI applications that leverage LLM capabilities to execute commands and process natural language requests.

## Prerequisites
To use this framework, you need to set up your Deepseek API KEY in the configuration files. The main components include:
- **deepseek-mcp-cli-client.py**: The client interface that handles user input and interacts with the LLM
- **deepseek-mcp-cli-server.py**: The MCP server that exposes tools and executes commands

## Key Features
- Natural language processing using Deepseek LLM
- Command execution through MCP (Model Control Protocol)
- LangChain integration for building AI agents
- Modular architecture for easy extension

## Usage
Execute the client using command `python deepseek-mcp-cli-client.py`. You can customize the behavior by modifying the query and tools in the client and server files.

The framework is designed to be easily extended to support custom commands and tools based on your specific requirements.

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Set up your Deepseek API KEY in the configuration
4. Run the client: `python deepseek-mcp-cli-client.py`

## Architecture
The framework follows a client-server architecture:
- **Client**: Handles user interaction and LLM integration
- **Server**: Manages tool execution and command processing
- **MCP Protocol**: Enables communication between client and server

## Customization
You can extend this framework by:
- Adding new tools to the server
- Customizing the LLM prompt in the client
- Implementing additional command handlers
- Integrating with external APIs and services
