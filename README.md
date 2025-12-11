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
- The LLM remembers previous interactions using worklog-based context
- Type `exit`, `quit`, or `q` to exit

### Command Line Arguments

#### Execute a single query directly:
```bash
python deepseek-mcp-cli-client.py "What's in my current directory?"
```

#### Continue from an existing worklog:
```bash
python deepseek-mcp-cli-client.py -l worklog_xxxx.log
```

#### Execute a query and continue from a worklog:
```bash
python deepseek-mcp-cli-client.py -l worklog_xxxx.log "Show me the current directory content"
```

#### View help information:
```bash
python deepseek-mcp-cli-client.py --help
```

### Available Options
- `-l, --log`: Path to existing worklog file to continue conversation from
- `query`: Optional initial query to execute

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


### Context Memory
The framework uses a worklog-based context memory system:

1. **Worklog as Context**: All user interactions and AI responses are logged to a worklog file
2. **Automatic Context Loading**: When continuing from an existing worklog, the entire conversation history is loaded as context
3. **Minimal Memory Usage**: Only the current system configuration and worklog content are maintained in memory
4. **Session Persistence**: Conversations can be resumed at any time by specifying the worklog file

This approach reduces token usage while maintaining comprehensive context memory across sessions.

## Available Tools
By default, the server provides these tools:
- `list_files`: List files in a directory
- `current_directory`: Get current working directory
- `create_file`: Create a new file with content
- `read_file`: Read the content of a file
- `execute_command`: Execute a shell command

### Mandatory Worklog Feature

The default preset includes a mandatory worklog requirement: all user requests and AI responses are automatically logged to a session log file with timestamps. This ensures a complete audit trail of all interactions and operations performed through the CLI.

#### Worklog Features:
- Each new dialogue session generates a unique log file with timestamp-based naming
- Custom filenames are supported when continuing from existing sessions
- All user requests are automatically logged with timestamps
- All AI responses are automatically logged with timestamps
- Timestamp format: `YYYY-MM-DD HH:MM:SS`
- Serves as the context memory for continuing conversations
- Can be used to resume conversations at any time

#### Example Log Entries:
```
[2023-11-01 14:30:25] USER REQUEST: List files in my current directory
[2023-11-01 14:30:27] AI RESPONSE: I'll list the files in your current directory...
[2023-11-01 14:30:28] Executing command: ls -la
[2023-11-01 14:30:28] Command result - Exit code: 0
```

#### Continuing Conversations:
To continue a conversation from an existing worklog:
```bash
python deepseek-mcp-cli-client.py -l worklog_xxxxx.log
```

The entire conversation history from the worklog will be used as context for the new session.

## License
MIT License
