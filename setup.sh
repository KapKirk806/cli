#!/bin/bash

# Multi-Agent CLI Setup Script

echo "=========================================="
echo "  Multi-Agent CLI System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

# Create virtual environment (optional but recommended)
echo ""
read -p "Create a virtual environment? (recommended) [Y/n]: " create_venv
create_venv=${create_venv:-Y}

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv

    echo "Activating virtual environment..."
    source venv/bin/activate

    echo "✓ Virtual environment created and activated"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data logs config
echo "✓ Directories created"

# Setup environment variables
echo ""
echo "=========================================="
echo "  API Key Configuration"
echo "=========================================="
echo ""

if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env

    echo ""
    echo "Please enter your API keys:"
    echo ""

    read -p "Gemini API Key (get at https://ai.google.dev/): " gemini_key
    read -p "YouTube API Key (get at https://console.cloud.google.com/): " youtube_key

    # Update .env file
    if [ -n "$gemini_key" ]; then
        sed -i "s/your-gemini-api-key-here/$gemini_key/" .env
    fi

    if [ -n "$youtube_key" ]; then
        sed -i "s/your-youtube-api-key-here/$youtube_key/" .env
    fi

    echo "✓ API keys saved to .env file"
else
    echo ".env file already exists. Skipping API key setup."
    echo "Edit .env manually if you need to update keys."
fi

# Make main.py executable
chmod +x main.py

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "To get started:"
echo ""

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
fi

echo "2. Set your API keys (if not already done):"
echo "   export GEMINI_API_KEY='your-key'"
echo "   export YOUTUBE_API_KEY='your-key'"
echo ""
echo "   OR source the .env file:"
echo "   set -a; source .env; set +a"
echo ""
echo "3. Run the CLI:"
echo "   python main.py"
echo ""
echo "For more information, see README.md"
echo ""
