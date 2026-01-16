#!/bin/bash
# Sharingan OS - ML Dependencies Installation
# Installs scikit-learn, onnxruntime, PyTorch and other ML dependencies

set -e

echo "=========================================="
echo "Sharingan OS - ML Dependencies Installer"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Python version
echo -e "${YELLOW}[1/5] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
    echo -e "${GREEN}Python $PYTHON_VERSION OK${NC}"
else
    echo -e "${RED}Error: Python 3.8+ required (found: $PYTHON_VERSION)${NC}"
    exit 1
fi

# Check available RAM
echo ""
echo -e "${YELLOW}[2/5] Checking system resources...${NC}"
TOTAL_RAM=$(free -m | awk '/^Mem:/{print $2}')
echo -e "  Total RAM: ${TOTAL_RAM}MB"
if [ "$TOTAL_RAM" -lt 2048 ]; then
    echo -e "${YELLOW}Warning: Less than 2GB RAM available${NC}"
    echo -e "${YELLOW}ML features may be slower${NC}"
fi

# Install dependencies
echo ""
echo -e "${YELLOW}[3/5] Installing ML dependencies...${NC}"

pip3 install --upgrade pip

echo "  Installing scikit-learn..."
pip3 install "scikit-learn>=1.3.0"

echo "  Installing numpy..."
pip3 install "numpy>=1.24.0"

echo "  Installing pandas..."
pip3 install "pandas>=2.0.0"

echo "  Installing onnxruntime (CPU-only)..."
pip3 install "onnxruntime>=1.15.0"

echo "  Installing onnx..."
pip3 install "onnx>=1.14.0"

echo "  Installing PyTorch (CPU-only)..."
pip3 install "torch>=2.0.0" --index-url https://download.pytorch.org/whl/cpu

echo "  Installing torchvision..."
pip3 install "torchvision>=0.15.0" --index-url https://download.pytorch.org/whl/cpu

echo "  Installing joblib..."
pip3 install "joblib>=1.3.0"

# Verify installation
echo ""
echo -e "${YELLOW}[4/5] Verifying installation...${NC}"

python3 -c "
import sklearn
import numpy
import pandas
import torch
print(f'  PyTorch: {torch.__version__}')
print(f'  sklearn: {sklearn.__version__}')
print(f'  numpy: {numpy.__version__}')
print(f'  pandas: {pandas.__version__}')
print(f'  CUDA available: {torch.cuda.is_available()}')
"

# Test imports
echo ""
echo -e "${YELLOW}[5/5] Testing Sharingan ML modules...${NC}"

python3 -c "
from sharingan_app._internal.ml_sklearn_detector import get_ml_detector
d = get_ml_detector()
print(f'  ml_sklearn_detector: OK (trained={d.is_trained})')
"

python3 -c "
from sharingan_app._internal.ml_onnx_detector import get_onnx_detector
d = get_onnx_detector()
print(f'  ml_onnx_detector: OK')
"

python3 -c "
from sharingan_app._internal.ml_pytorch_models import get_pytorch_detector
d = get_pytorch_detector()
status = d.get_status()
print(f'  ml_pytorch_models: OK (trained={status[\"trained\"]})')
"

echo ""
echo -e "${GREEN}=========================================="
echo "ML Dependencies Installed Successfully!"
echo "==========================================${NC}"
echo ""
echo "To test the ML modules:"
echo -e "${YELLOW}  python3 -m sharingan_app._internal.ml_sklearn_detector${NC}"
echo -e "${YELLOW}  python3 -m sharingan_app._internal.ml_onnx_detector${NC}"
echo -e "${YELLOW}  python3 -m sharingan_app._internal.ml_pytorch_models${NC}"
echo ""
echo "To run the full AI providers test:"
echo -e "${YELLOW}  python3 -m sharingan_app._internal.ai_providers${NC}"
