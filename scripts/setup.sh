#!/bin/bash

# DeepReader Setup Script
# This script sets up the development environment for DeepReader

set -e

echo "🚀 Setting up DeepReader development environment..."

# Check Python version
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1-2)
required_version="3.9"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python version: $(python3 --version)"

# Create virtual environment
if [ ! -d "deepreader-env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv deepreader-env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source deepreader-env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
if [ -f "requirements_dev.txt" ]; then
    echo "🛠️ Installing development dependencies..."
    pip install -r requirements_dev.txt
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p website/chat_history
mkdir -p website/bookmarks
mkdir -p website/book_prompt
mkdir -p logs

# Set up pre-commit hooks (if available)
if command -v pre-commit &> /dev/null; then
    echo "🪝 Setting up pre-commit hooks..."
    pre-commit install
fi

# Check for environment file
if [ ! -f ".env" ]; then
    echo "⚠️ Creating .env template..."
    cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
DEEPREADER_MODEL_NAME=gpt-4

# Optional: Alternative API providers
# OPENAI_BASE_URL=https://api.deepseek.com/v1
# DEEPREADER_MODEL_NAME=deepseek-chat

# Environment
ENVIRONMENT=development
EOF
    echo "📝 Please edit .env file with your API keys"
fi

# Run font installation script
if [ -f "font-install.sh" ]; then
    echo "🔤 Installing fonts..."
    chmod +x font-install.sh
    ./font-install.sh
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate the virtual environment: source deepreader-env/bin/activate"
echo "3. Start the web interface: streamlit run website/chatbot.py"
echo "4. Or run CLI: python reader/main.py --book \"书名\" --auto true"
echo ""
echo "📖 For more information, see:"
echo "   - DEPLOYMENT.md for deployment guide"
echo "   - docs/API.md for API documentation"
echo "   - README.md for project overview"