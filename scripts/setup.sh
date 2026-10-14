#!/bin/bash

# DeepReader Setup Script
# This script sets up the development environment for DeepReader

set -e

echo "🚀 Setting up DeepReader development environment..."

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
python3 -c 'import sys; assert sys.version_info >= (3, 12), "Python 3.12+ required"'

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

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Edit .env with your API key before generating content."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate the virtual environment: source deepreader-env/bin/activate"
echo "3. Start the web interface: streamlit run website/Home.py"
echo "4. Or run CLI: python reader/main.py --book \"书名\" --auto true"
echo ""
echo "📖 For more information, see:"
echo "   - DEPLOYMENT.md for deployment guide"
echo "   - docs/API.md for API documentation"
echo "   - README.md for project overview"