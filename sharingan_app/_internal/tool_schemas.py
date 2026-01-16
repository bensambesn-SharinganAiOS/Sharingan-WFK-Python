#!/usr/bin/env python3
"""
Tool Schemas - Detailed tool descriptions for LLM agents
Inspired by OpenCode's tool schema system
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class ToolCategory(Enum):
    FILE_IO = "file_io"
    SEARCH = "search"
    EXECUTION = "execution"
    NETWORK = "network"
    AI = "ai"
    SYSTEM = "system"
    DEBUG = "debug"

@dataclass
class ToolParameter:
    name: str
    type: str
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum_values: Optional[List[str]] = None

@dataclass
class ToolSchema:
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    returns: str
    examples: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)

# Tool definitions with detailed descriptions
TOOL_SCHEMAS = {
    "read": ToolSchema(
        name="read",
        description="Read a file from the local filesystem. You can access any file directly by using this tool. "
                    "If the User provides a path to a file assume that path is valid. "
                    "It is okay to read a file that does not exist; an error will be returned.",
        category=ToolCategory.FILE_IO,
        parameters=[
            ToolParameter("filePath", "string", "The path to the file to read (absolute path required)", required=True),
            ToolParameter("offset", "number", "The line number to start reading from (0-based)", required=False, default=0),
            ToolParameter("limit", "number", "The number of lines to read (defaults to 2000)", required=False, default=2000),
        ],
        returns="File contents with line numbers, or error message",
        examples=["read /etc/hosts", "read /path/to/file.py offset=100 limit=50"],
        permissions=["read"]
    ),
    
    "write": ToolSchema(
        name="write",
        description="Write content to a file on the local filesystem. "
                    "If the file already exists, it will be overwritten. "
                    "Directories will be created if they don't exist.",
        category=ToolCategory.FILE_IO,
        parameters=[
            ToolParameter("filePath", "string", "The path to the file to write (absolute path required)", required=True),
            ToolParameter("content", "string", "The content to write to the file", required=True),
        ],
        returns="Success message or error",
        examples=["write /tmp/test.txt content='Hello World'", "write /path/to/new_file.py content='# New file'"],
        permissions=["write"]
    ),
    
    "edit": ToolSchema(
        name="edit",
        description="Edit a specific portion of an existing file. "
                    "Uses exact string matching to replace oldString with newString in the file.",
        category=ToolCategory.FILE_IO,
        parameters=[
            ToolParameter("filePath", "string", "The path to the file to edit (absolute path required)", required=True),
            ToolParameter("oldString", "string", "The exact text to replace (must match exactly including indentation)", required=True),
            ToolParameter("newString", "string", "The text to replace it with (must be different from oldString)", required=True),
            ToolParameter("replaceAll", "boolean", "Replace all occurrences of oldString (default false)", required=False, default=False),
        ],
        returns="Success message or error if oldString not found",
        examples=["edit /path/to/file.py oldString='old text' newString='new text'"],
        permissions=["edit", "write"]
    ),
    
    "glob": ToolSchema(
        name="glob",
        description="Find files by pattern matching in a directory. "
                    "Supports glob patterns like '**/*.js' or 'src/**/*.ts'. "
                    "Returns matching file paths sorted by modification time.",
        category=ToolCategory.SEARCH,
        parameters=[
            ToolParameter("pattern", "string", "The glob pattern to match files against", required=True),
            ToolParameter("path", "string", "The directory to search in (defaults to current directory)", required=False),
            ToolParameter("ignore", "array", "List of glob patterns to ignore", required=False, default=[]),
        ],
        returns="List of matching file paths",
        examples=["pattern '**/*.py'", "pattern 'src/**/*.ts' path=/project/src"],
        permissions=["read"]
    ),
    
    "grep": ToolSchema(
        name="grep",
        description="Search file contents using regular expressions. "
                    "Supports full regex syntax. Filter files by pattern with the include parameter.",
        category=ToolCategory.SEARCH,
        parameters=[
            ToolParameter("pattern", "string", "The regex pattern to search for in file contents", required=True),
            ToolParameter("path", "string", "The directory to search in (defaults to current directory)", required=False),
            ToolParameter("include", "string", "File pattern to include (e.g., '*.js', '*.{ts,tsx}')", required=False),
            ToolParameter("literal_text", "boolean", "Treat pattern as literal string (not regex)", required=False, default=False),
        ],
        returns="File paths and line numbers with matches, sorted by modification time",
        examples=["pattern 'log.*Error' include='*.log'", "pattern 'function\\s+\\w+'"],
        permissions=["read"]
    ),
    
    "list": ToolSchema(
        name="list",
        description="List files and directories in a given path. "
                    "The path parameter must be absolute. "
                    "Can optionally provide an array of glob patterns to ignore.",
        category=ToolCategory.FILE_IO,
        parameters=[
            ToolParameter("path", "string", "The absolute path to the directory to list", required=True),
            ToolParameter("ignore", "array", "List of glob patterns to ignore", required=False, default=[]),
        ],
        returns="List of files and directories",
        examples=["path '/etc'", "path '/project' ignore=['*.pyc', '__pycache__']"],
        permissions=["read"]
    ),
    
    "bash": ToolSchema(
        name="bash",
        description="Executes a given bash command in a persistent shell session with optional timeout. "
                    "All commands run in /root/Projets/Sharingan-WFK-Python by default. "
                    "Use the 'workdir' parameter to run commands in a different directory.",
        category=ToolCategory.EXECUTION,
        parameters=[
            ToolParameter("command", "string", "The command to execute", required=True),
            ToolParameter("description", "string", "Clear, concise description of what this command does in 5-10 words", required=True),
            ToolParameter("timeout", "number", "Optional timeout in milliseconds (max 600000ms / 10 minutes)", required=False, default=120000),
            ToolParameter("workdir", "string", "The working directory to run the command in", required=False),
        ],
        returns="Command output (stdout/stderr) or error",
        examples=["command='ls -la' description='List files in directory'", 
                  "command='pytest tests' description='Run tests' timeout=300000"],
        permissions=["bash"]
    ),
    
    "todowrite": ToolSchema(
        name="todowrite",
        description="Create and manage a structured task list for your current coding session. "
                    "This helps track progress, organize complex tasks, and demonstrate thoroughness.",
        category=ToolCategory.SYSTEM,
        parameters=[
            ToolParameter("todos", "array", "The updated todo list (array of task objects)", required=True),
        ],
        returns="Success message with task count",
        examples=["todos=[{'content': 'Fix bug', 'status': 'in_progress', 'priority': 'high', 'id': '1'}]"],
        permissions=["write"]
    ),
    
    "todoread": ToolSchema(
        name="todoread",
        description="Read your current todo list to see pending, in-progress, and completed tasks.",
        category=ToolCategory.SYSTEM,
        parameters=[],
        returns="Current todo list",
        examples=[],
        permissions=["read"]
    ),
    
    "webfetch": ToolSchema(
        name="webfetch",
        description="Fetch content from a specified URL. "
                    "Takes a URL and a prompt as input. "
                    "Fetches the URL content, converts HTML to markdown.",
        category=ToolCategory.NETWORK,
        parameters=[
            ToolParameter("url", "string", "The URL to fetch content from", required=True),
            ToolParameter("format", "string", "The format to return content in (text, markdown, or html)", required=True, 
                         enum_values=["text", "markdown", "html"]),
            ToolParameter("timeout", "number", "Optional timeout in seconds (max 120)", required=False, default=30),
        ],
        returns="Content in requested format or error",
        examples=["url='https://example.com' format='text'", "url='https://api.github.com' format='json'"],
        permissions=["webfetch"]
    ),
    
    "codesearch": ToolSchema(
        name="codesearch",
        description="Search and get relevant context for any programming task using Exa Code API. "
                    "Provides comprehensive code examples, documentation, and API references.",
        category=ToolCategory.SEARCH,
        parameters=[
            ToolParameter("query", "string", "Search query to find relevant context for APIs, Libraries, and SDKs", required=True),
            ToolParameter("tokensNum", "number", "Number of tokens to return (1000-50000, default 5000)", required=False, default=5000),
        ],
        returns="Relevant code examples and documentation",
        examples=["query='React useState hook examples'", "query='Python pandas dataframe filtering'"],
        permissions=["codesearch"]
    ),
    
    "task": ToolSchema(
        name="task",
        description="Launch a new agent to handle complex, multi-step tasks autonomously. "
                    "Use this for research, exploration, or tasks requiring multiple iterations.",
        category=ToolCategory.AI,
        parameters=[
            ToolParameter("command", "string", "The command that triggered this task", required=True),
            ToolParameter("description", "string", "A short (3-5 words) description of the task", required=True),
            ToolParameter("prompt", "string", "The task for the agent to perform", required=True),
            ToolParameter("subagent_type", "string", "The type of specialized agent to use", required=True,
                         enum_values=["general", "explore"]),
            ToolParameter("session_id", "string", "Existing Task session to continue", required=False),
        ],
        returns="Agent's final response",
        examples=["command='/analyze path/to/file.py' description='Analyze file' prompt='Check for bugs' subagent_type='explore'"],
        permissions=["task"]
    ),
}

def get_tool_schema(tool_name: str) -> Optional[ToolSchema]:
    """Get schema for a specific tool"""
    return TOOL_SCHEMAS.get(tool_name)

def get_all_tool_schemas() -> Dict[str, ToolSchema]:
    """Get all tool schemas"""
    return TOOL_SCHEMAS

def format_tool_for_llm(tool_name: str) -> str:
    """Format tool schema for LLM system prompt"""
    schema = get_tool_schema(tool_name)
    if not schema:
        return f"Unknown tool: {tool_name}"
    
    params = []
    for p in schema.parameters:
        param_str = f"{p.name}: {p.type}"
        if p.required:
            param_str += " (required)"
        if p.default is not None:
            param_str += f" (default: {p.default})"
        if p.enum_values:
            param_str += f" ({p.enum_values})"
        param_str += f" - {p.description}"
        params.append(f"  - {param_str}")
    
    return f"""
### {tool_name}

{schema.description}

**Category:** {schema.category.value}

**Parameters:**
{chr(10).join(params)}

**Returns:** {schema.returns}

**Examples:**
{chr(10).join(f'  - {e}' for e in schema.examples)}

**Required Permissions:** {', '.join(schema.permissions) if schema.permissions else 'none'}
"""

def get_tools_for_agent(agent_type: str) -> List[str]:
    """Get list of tools available to a specific agent type"""
    if agent_type == "plan":
        # Plan agent - read only with ask for bash
        return ["read", "glob", "grep", "list", "webfetch", "codesearch", "todoread"]
    elif agent_type == "build":
        # Build agent - all tools
        return list(TOOL_SCHEMAS.keys())
    else:
        # Default - basic tools
        return ["read", "glob", "grep", "list", "todoread", "todoread"]

def get_system_prompt_for_agent(agent_type: str) -> str:
    """Generate system prompt for a specific agent type"""
    tools = get_tools_for_agent(agent_type)
    
    prompt = f"""You are Sharingan OS, an autonomous AI coding agent.

## Your Role
- You are helping with software engineering tasks
- Be concise and direct in your responses
- Focus on the user's query without unnecessary preamble

## Available Tools
"""
    
    for tool_name in tools:
        prompt += format_tool_for_llm(tool_name) + "\n"
    
    if agent_type == "plan":
        prompt += """
## Plan Mode
- You are in READ-ONLY mode
- Do NOT make file changes or execute shell commands without explicit permission
- Focus on analysis, planning, and providing recommendations
- When you need to make changes, explain what you would do and ask for confirmation
"""
    else:
        prompt += """
## Build Mode
- You can read and write files
- You can execute shell commands
- Always explain what you're doing before making changes
- Follow the code style and conventions of the existing codebase
"""
    
    return prompt

if __name__ == "__main__":
    print("=== TOOL SCHEMAS ===\n")
    
    print("Available tools:")
    for name, schema in TOOL_SCHEMAS.items():
        print(f"  - {name} ({schema.category.value})")
    
    print("\n" + "="*50)
    print("Example: read tool schema")
    print("="*50)
    print(format_tool_for_llm("read"))
    
    print("\n" + "="*50)
    print("System prompt for PLAN agent")
    print("="*50)
    print(get_system_prompt_for_agent("plan")[:500] + "...")
