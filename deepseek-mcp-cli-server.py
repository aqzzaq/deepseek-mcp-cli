# basic import 
from mcp.server.fastmcp import FastMCP
import os
import yaml

# instantiate an MCP server client
mcp = FastMCP("Deepseek MCP CLI Server")


@mcp.tool()
def list_files(directory="."):
    """List files in the specified directory."""
    import os
    try:
        files = os.listdir(directory)
        return f"Files in {directory}:\n" + "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"


@mcp.tool()
def current_directory():
    """Get the current working directory."""
    import os
    return f"Current directory: {os.getcwd()}"


@mcp.tool()
def create_file(filename, content=""):
    """Create a new file with optional content."""
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"File '{filename}' created successfully."
    except Exception as e:
        return f"Error creating file: {str(e)}"


@mcp.tool()
def read_file(filename):
    """Read the content of a file."""
    try:
        with open(filename, "r") as f:
            content = f.read()
        return f"Content of '{filename}':\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def execute_command(command):
    """Execute a shell command and return the output."""
    import subprocess
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"Command output: {result.stdout}\nError: {result.stderr}\nReturn code: {result.returncode}"
    except Exception as e:
        return f"Error executing command: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
