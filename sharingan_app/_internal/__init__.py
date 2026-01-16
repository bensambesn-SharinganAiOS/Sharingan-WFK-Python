"""
Sharingan OS - Python Core Library
Complete ethical hacking and system administration toolkit
"""

from .sharingan_os import SharinganOS, sharingan
from .main import SharinganCore, get_core, sharingan as core

# AI & Providers
from .ai_providers import (
    get_provider_manager, 
    ai_chat,
    AIProvider,
    TgptProvider,
    MiniMaxProvider,
    GrokCodeFastProvider,
    HybridProviderManager
)

# Consciousness & Clarification
from .system_consciousness import (
    SystemConsciousness,
    PermissionConfig
)

from .clarification_layer import (
    ProactiveClarifier,
    get_clarifier,
    QueryType
)

# Neutral AI
from .neutral_ai import (
    NeutralMode,
    get_neutral_mode,
    NeutralSystemPrompt,
    Warning
)

# Tools & Schemas
from .tool_schemas import (
    ToolSchema,
    ToolParameter,
    ToolCategory,
    get_tool_schema,
    get_all_tool_schemas,
    get_system_prompt_for_agent,
    get_tools_for_agent
)

# Diagnostics & Context
from .lsp_diagnostics import (
    DiagnosticManager,
    LSPServer,
    SimpleDiagnostics,
    get_diagnostic_manager,
    Diagnostic
)

from .context_manager import (
    ContextManager,
    ContextSummary,
    get_context_manager
)

# Memory
from .ai_memory_manager import (
    IntelligentMemoryManager,
    SharedMemory,
    get_memory_manager,
    get_shared_memory,
    MemoryPriority,
    MemoryCategory
)

# Tool Registry
from .tool_registry import (
    ToolRegistry,
    get_tool_registry
)

__version__ = "3.0.0"
__author__ = "Ben Sambe"

__all__ = [
    # Core
    "SharinganOS",
    "sharingan",
    "SharinganCore",
    "get_core",
    "core",
    
    # AI Providers
    "get_provider_manager",
    "ai_chat",
    "TgptProvider",
    "MiniMaxProvider",
    "GrokCodeFastProvider",
    "HybridProviderManager",
    
    # Consciousness
    "SystemConsciousness",
    "PermissionConfig",
    
    # Clarification
    "ProactiveClarifier",
    "get_clarifier",
    "QueryType",
    
    # Neutral AI
    "NeutralMode",
    "get_neutral_mode",
    "NeutralSystemPrompt",
    "Warning",
    
    # Tools
    "ToolSchema",
    "ToolParameter",
    "ToolCategory",
    "get_tool_schema",
    "get_all_tool_schemas",
    "get_system_prompt_for_agent",
    "get_tools_for_agent",
    
    # Diagnostics
    "DiagnosticManager",
    "LSPServer",
    "SimpleDiagnostics",
    "get_diagnostic_manager",
    "Diagnostic",
    
    # Context
    "ContextManager",
    "ContextSummary",
    "get_context_manager",
    
    # Memory
    "IntelligentMemoryManager",
    "SharedMemory",
    "get_memory_manager",
    "get_shared_memory",
    "MemoryPriority",
    "MemoryCategory",
    
    # Registry
    "ToolRegistry",
    "get_tool_registry",
]
