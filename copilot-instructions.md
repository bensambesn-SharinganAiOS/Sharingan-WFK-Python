# Copilot Instructions for Sharingan OS

## How to Interact with Sharingan OS

Sharingan OS is an AI-powered cybersecurity toolkit with a natural language command interface. You can interact with it in multiple ways.

### 1. Natural Language Shell (Interactive)

Start an interactive shell where you can type commands in natural language (French or English):

```bash
python3 -m sharingan_app._internal.main shell
```

**Example session:**
```
🌐_sharingan> scan les ports de example.com
🌐_sharingan> qui est le propriétaire de google.com
🌐_sharingan> trouve l'IP de yahoo.com
🌐_sharingan> /status
🌐_sharingan> /exit
```

### 2. Demo Mode

Run demo commands to see the NLP system in action:

```bash
python3 -m sharingan_app._internal.main shell --demo
```

### 3. Direct AI Chat

Chat with the AI system directly:

```bash
python3 -m sharingan_app._internal.main ai "comment faire un scan de ports"
```

### 4. System Commands

```bash
# Show system status
python3 -m sharingan_app._internal.main status

# List all capabilities
python3 -m sharingan_app._internal.main capabilities

# List available tools
python3 -m sharingan_app._internal.main tools

# System consciousness overview
python3 -m sharingan_app._internal.main consciousness overview

# Genome memory statistics
python3 -m sharingan_app._internal.main genome show

# Memory management
python3 -m sharingan_app._internal.main memory show
```

## Natural Language Commands Supported

### Network Scanning
| Command | Executed |
|---------|----------|
| `scan les ports de example.com` | `nmap -sV example.com` |
| `scan les ports de localhost` | `nmap -sV localhost` |
| `scan ports of 192.168.1.1` | `nmap -sV 192.168.1.1` |
| `scan rapide de example.com` | `nmap -F example.com` |

### Reconnaissance
| Command | Executed |
|---------|----------|
| `whois example.com` | `whois example.com` |
| `qui est le propriétaire de google.com` | `whois google.com` |
| `trouve l'IP de yahoo.com` | `dig yahoo.com` |
| `quelle est l'IP de 192.168.1.1` | `dig 192.168.1.1` |
| `dig google.com` | `dig google.com` |

### Web Testing
| Command | Executed |
|---------|----------|
| `affiche les headers de site.com` | `curl -sI site.com` |
| `teste le site de example.com` | `curl -sI example.com` |
| `vérifie le serveur de google.com` | `curl -sI google.com` |

### Shell Special Commands
- `/explain <query>` - Explain what a command would do without executing
- `/history` - Show command history
- `/status` - Show system status
- `/exit` - Quit the shell

## Risk Levels

Commands are classified by risk level:
- **SAFE** - Read-only operations (whois, dig)
- **LOW** - Information discovery
- **MEDIUM** - Active scanning (nmap)
- **HIGH** - Security testing (nikto)
- **CRITICAL** - Requires explicit confirmation

## AI Providers

Sharingan supports multiple AI providers:
- **tgpt** - Primary provider (Phind/Grok)
- **grok-code-fast** - Coding specialist
- **minimax** - API backup
- **ollama** - Local models (tinyllama, gemma:2b)
- **llama_local** - llama.cpp server (optional)

## Development

### Running Tests
```bash
pytest
```

### Linting
```bash
flake8 . --max-line-length=100
```

### Type Checking
```bash
python -m mypy --strict
```

## Architecture

```
sharingan_app/_internal/
├── main.py              # Entry point, CLI parser
├── sharingan_os.py      # Core OS class
├── nl_command_processor.py  # NLP to command parsing
├── ai_providers.py      # Multi-provider AI routing
├── system_consciousness.py  # Permissions, clarifier
├── enhanced_system_consciousness.py  # Capabilities
├── action_executor.py   # Command execution
├── ai_memory_manager.py # Persistent memory
├── genome_memory.py     # ADN-based learning
├── ml_sklearn_detector.py  # ML intent classification
├── ml_pytorch_models.py    # PyTorch models
├── ml_onnx_detector.py     # ONNX detection
└── ...
```

## Logging

All modules use `logging.getLogger("sharingan.*")`:
- `INFO` - Normal operations
- `WARNING` - Non-critical issues
- `ERROR` - Failures (logged, not printed to user)
