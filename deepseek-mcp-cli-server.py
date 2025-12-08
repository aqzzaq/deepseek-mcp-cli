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
def write_file(filename, content, append=False):
    """Write content to a file. Set append=True to append to existing file."""
    try:
        mode = "a" if append else "w"
        with open(filename, mode) as f:
            f.write(content)
        action = "appended to" if append else "written to"
        return f"Content successfully {action} '{filename}'"
    except Exception as e:
        return f"Error writing to file: {str(e)}"


@mcp.tool()
def append_to_worklog(content, log_filename="worklog.log"):
    """Append content to the specified log file with timestamp."""
    import datetime
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {content}\n"
        with open(log_filename, "a") as f:
            f.write(log_entry)
        return f"Worklog entry added successfully to '{log_filename}'"
    except Exception as e:
        return f"Error writing to worklog: {str(e)}"


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
def execute_command(command, log_filename="worklog.log"):
    """Execute a shell command and return the output."""
    import subprocess
    import datetime
    
    # Log the command to worklog before execution
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Executing command: {command}\n"
        with open(log_filename, "a") as f:
            f.write(log_entry)
    except Exception as log_error:
        return f"Error writing to worklog: {str(log_error)}"
    
    # Execute the command
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Log the result to worklog
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Command result - Exit code: {result.returncode}\n"
            with open(log_filename, "a") as f:
                f.write(log_entry)
        except:
            # Ignore logging errors for the result
            pass
            
        return f"Command output: {result.stdout}\nError: {result.stderr}\nReturn code: {result.returncode}"
    except Exception as e:
        return f"Error executing command: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
