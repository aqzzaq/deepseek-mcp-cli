# Deepseek-CLI-Tool-Framework

## Intro
This is a CLI tool framework built using MCP (Model Control Protocol) and LangChain with Deepseek LLM integration. It provides a foundation for creating intelligent CLI applications that leverage LLM capabilities to execute commands and process natural language requests with context memory and customizable presets.

## Prerequisites
To use this framework, you need to set up your Deepseek API KEY in the environment variable `DEEPSEEK_API_KEY` or directly in the client file. The main components include:
- **deepseek-mcp-cli-client.py**: The client interface that handles user input, context memory, and interacts with the LLM
- **deepseek-mcp-cli-server.py**: The MCP server that exposes tools and executes commands

## Key Features
- Natural language processing using Deepseek LLM
- Command execution through MCP (Model Control Protocol)
- LangChain integration for building AI agents
- Context memory for maintaining conversation history
- Customizable presets for defining LLM roles and instructions
- Interactive mode with user-friendly interface
- Command-line argument support
- Modular architecture for easy extension

## Usage

### Interactive Mode
Execute the client in interactive mode:
```bash
python deepseek-mcp-cli-client.py
```

In interactive mode, you can:
- Enter natural language queries
- The LLM remembers previous interactions (context memory)
- Type `exit`, `quit`, or `q` to exit

### Command Line Arguments
Execute a single query directly:
```bash
python deepseek-mcp-cli-client.py "What's in my current directory?"
```

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your Deepseek API KEY:
   ```bash
   export DEEPSEEK_API_KEY="your-api-key"
   ```
   Or edit `deepseek-mcp-cli-client.py` and add your API key directly.

3. Run the client (the server starts automatically):
   ```bash
   python deepseek-mcp-cli-client.py
   ```

## Architecture
The framework follows a client-server architecture:
- **Client**: Handles user interaction, LLM integration, and context memory
- **Server**: Manages tool execution and command processing
- **MCP Protocol**: Enables communication between client and server
- **LangChain**: Provides agent framework and tool integration

## Customization

### Preset Customization
You can customize the LLM's role and behavior by modifying the preset in `deepseek-mcp-cli-client.py`:

```python
# Default preset example
DEFAULT_PRESET = {
    "role": "Helpful CLI Assistant",
    "instructions": [
        "You are a helpful CLI assistant that can execute commands and perform file operations.",
        "Always be clear and concise in your responses.",
        "Use the available tools to accomplish tasks when needed."
    ]
}
```

### Adding New Tools
Extend the server by adding new tools in `deepseek-mcp-cli-server.py`:

```python
@tool
async def new_tool(param: str) -> str:
    """Description of what the tool does."""
    # Implementation here
    return "Result"
```

### Context Memory
The framework automatically maintains conversation history. You can modify this behavior in the `run()` function in the client file.

## Available Tools
By default, the server provides these tools:
- `list_files`: List files in a directory
- `current_directory`: Get current working directory
- `create_file`: Create a new file with content
- `read_file`: Read the content of a file
- `execute_command`: Execute a shell command

## License
MIT License
