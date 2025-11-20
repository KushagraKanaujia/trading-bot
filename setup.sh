#!/bin/bash

# Trading Bot V2.0 Setup Script
# This script automates the setup process for the trading bot

set -e  # Exit on error

echo "========================================"
echo "Trading Bot V2.0 - Automated Setup"
echo "========================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}[1/10] Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if [[ "$(printf '%s\n' "3.10" "$python_version" | sort -V | head -n1)" != "3.10" ]]; then
    echo -e "${RED}Error: Python 3.10+ required${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python version OK${NC}"
echo ""

# Create virtual environment
echo -e "${YELLOW}[2/10] Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}[3/10] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo -e "${YELLOW}[4/10] Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ Pip upgraded${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}[5/10] Installing dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Check PostgreSQL
echo -e "${YELLOW}[6/10] Checking PostgreSQL...${NC}"
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL found${NC}"

    # Create database if it doesn't exist
    if ! psql -lqt | cut -d \| -f 1 | grep -qw trading_bot; then
        echo "Creating database 'trading_bot'..."
        createdb trading_bot
        echo -e "${GREEN}✓ Database created${NC}"
    else
        echo -e "${GREEN}✓ Database already exists${NC}"
    fi
else
    echo -e "${RED}✗ PostgreSQL not found. Please install PostgreSQL first.${NC}"
    echo "macOS: brew install postgresql@14"
    echo "Ubuntu: sudo apt-get install postgresql-14"
fi
echo ""

# Check Redis
echo -e "${YELLOW}[7/10] Checking Redis...${NC}"
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}! Redis is installed but not running${NC}"
        echo "Start with: redis-server (macOS/Linux)"
        echo "Or: brew services start redis (macOS)"
    fi
else
    echo -e "${RED}✗ Redis not found. Please install Redis first.${NC}"
    echo "macOS: brew install redis"
    echo "Ubuntu: sudo apt-get install redis-server"
fi
echo ""

# Setup environment file
echo -e "${YELLOW}[8/10] Setting up environment file...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file from template${NC}"
    echo -e "${YELLOW}! Please edit .env with your API credentials${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Initialize database
echo -e "${YELLOW}[9/10] Initializing database...${NC}"
python3 -c "from src.models import init_db; init_db()" 2>/dev/null && echo -e "${GREEN}✓ Database initialized${NC}" || echo -e "${YELLOW}! Database initialization failed. Run manually after setting up .env${NC}"
echo ""

# Create necessary directories
echo -e "${YELLOW}[10/10] Creating directories...${NC}"
mkdir -p logs data models notebooks
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Summary
echo "========================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials:"
echo "   nano .env"
echo ""
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "4. Start the application:"
echo "   uvicorn src.api.main:app --reload"
echo ""
echo "5. View documentation:"
echo "   cat README_V2.md"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Never commit your .env file to version control!${NC}"
echo ""
