#!/bin/bash
# Sharingan OS - Llama.cpp Setup Script
# Installs llama.cpp and Gemma 3 1B for local inference

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Sharingan OS - Llama.cpp Setup ===${NC}"
echo ""

# Configuration
LLAMA_DIR="$HOME/.local/share/sharingan/llama.cpp"
MODEL_DIR="$HOME/.local/share/sharingan/models"
MODEL_URL="https://huggingface.co/google/gemma-3-1b-it-gguf/resolve/main/gemma-3-1b-it.gguf"
MODEL_NAME="gemma3-1b-it.gguf"

# Create directories
mkdir -p "$LLAMA_DIR"
mkdir -p "$MODEL_DIR"

# Check prerequisites
echo -e "${YELLOW}[1/5] Checking prerequisites...${NC}"
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed${NC}"
    exit 1
fi
if ! command -v make &> /dev/null; then
    echo -e "${RED}Error: make is not installed${NC}"
    exit 1
fi
if ! command -v g++ &> /dev/null; then
    echo -e "${RED}Error: g++ is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}Prerequisites OK${NC}"

# Clone and build llama.cpp
echo ""
echo -e "${YELLOW}[2/5] Building llama.cpp...${NC}"
if [ -f "$LLAMA_DIR/llama-server" ]; then
    echo -e "${GREEN}llama.cpp already built${NC}"
else
    cd "$LLAMA_DIR"
    if [ ! -d ".git" ]; then
        git clone https://github.com/ggerganov/llama.cpp.git .
    fi
    make LLAMA_BUILD_METAL=0 -j$(nproc)
    echo -e "${GREEN}llama.cpp built successfully${NC}"
fi

# Download Gemma 3 1B model
echo ""
echo -e "${YELLOW}[3/5] Downloading Gemma 3 1B model (~4GB)...${NC}"
MODEL_PATH="$MODEL_DIR/$MODEL_NAME"
if [ -f "$MODEL_PATH" ]; then
    echo -e "${GREEN}Model already exists${NC}"
else
    cd "$MODEL_DIR"
    echo "Downloading from HuggingFace..."
    # Try with wget first, fallback to curl
    if command -v wget &> /dev/null; then
        wget -c --progress=bar:force "$MODEL_URL" -O "$MODEL_NAME"
    else
        curl -L -C - -o "$MODEL_NAME" "$MODEL_URL"
    fi
    echo -e "${GREEN}Model downloaded${NC}"
fi

# Create startup script
echo ""
echo -e "${YELLOW}[4/5] Creating startup script...${NC}"
cat > "$HOME/.local/bin/sharingan-llama-server" << 'SCRIPT'
#!/bin/bash
# Start llama.cpp server for Sharingan OS

MODEL_DIR="$HOME/.local/share/sharling/models"
MODEL="gemma3-1b-it.gguf"
PORT=8080
CONTEXT=2048

cd "$HOME/.local/share/sharing/llama.cpp"
./llama-server \
    -m "$MODEL_DIR/$MODEL" \
    -c $CONTEXT \
    --port $PORT \
    --host 127.0.0.1 \
    --temp 0.7 \
    --top-k 40 \
    --top-p 0.95 \
    --log-disable
SCRIPT
chmod +x "$HOME/.local/bin/sharingan-llama-server"
echo -e "${GREEN}Startup script created: ~/.local/bin/sharingan-llama-server${NC}"

# Create systemd service (optional)
echo ""
echo -e "${YELLOW}[5/5] Creating systemd service...${NC}"
cat > "$HOME/.config/systemd/user/sharingan-llama.service" << 'SERVICE'
[Unit]
Description=Sharingan OS - Llama.cpp Server (Gemma 3 1B)
After=network.target

[Service]
Type=simple
ExecStart=%h/.local/bin/sharingan-llama-server
Restart=on-failure
RestartSec=10
Environment=HOME=%h

[Install]
WantedBy=default.target
SERVICE

mkdir -p "$HOME/.config/systemd/user"
systemctl --user daemon-reload 2>/dev/null || true
echo -e "${GREEN}Systemd service created${NC}"

echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "To start the server:"
echo -e "${YELLOW}  ~/.local/bin/sharingan-llama-server${NC}"
echo ""
echo "Or as a service:"
echo -e "${YELLOW}  systemctl --user start sharingan-llama${NC}"
echo ""
echo "To enable auto-start on boot:"
echo -e "${YELLOW}  systemctl --user enable sharingan-llama${NC}"
echo ""
echo "Once started, test with:"
echo -e "${YELLOW}  python -m sharingan_app._internal.ai_providers_llama${NC}"
