#!/bin/bash

echo "╔═══════════════════════════════════════╗"
echo "║  A.L.E.X v0.2 - Setup                ║"
echo "║  Frontend React + Backend FastAPI    ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Python Backend
echo -e "${YELLOW}[1/4] Verificando Python...${NC}"
if ! command -v python &> /dev/null; then
    echo "Error: Python no instalado"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"

echo ""
echo -e "${YELLOW}[2/4] Instalando dependencias Python...${NC}"
pip install fastapi uvicorn psutil --break-system-packages
echo -e "${GREEN}✓ Dependencias Python instaladas${NC}"

# Node Frontend
echo ""
echo -e "${YELLOW}[3/4] Verificando Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "Error: Node.js no instalado"
    exit 1
fi

NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ Node.js ${NODE_VERSION}, npm ${NPM_VERSION}${NC}"

echo ""
echo -e "${YELLOW}[4/4] Instalando dependencias Node...${NC}"
npm install
echo -e "${GREEN}✓ Dependencias Node instaladas${NC}"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Setup completado                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
echo ""
echo "Para ejecutar:"
echo ""
echo "Terminal 1 (Backend):"
echo "  python api.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  npm run dev"
echo ""
echo "Frontend en http://localhost:5173"
echo ""
