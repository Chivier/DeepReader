# DeepReader

A sophisticated AI-powered system for generating high-quality book reviews and facilitating in-depth literary discussions.

## Overview

DeepReader combines advanced web scraping, natural language processing, and AI-powered analysis to create comprehensive book reviews and enable meaningful literary discussions. The system consists of two main components:

1. **Data Collection & Processing Pipeline** - Automated tools for gathering and analyzing book reviews
2. **Interactive Web Interface** - Streamlit-based chatbot for engaging book discussions

## Key Features

### 📚 Intelligent Review Collection
- Scrapes and processes reviews from Douban (Chinese book review platform)
- Downloads and transcribes video reviews from Bilibili/YouTube
- Handles multiple translations and editions
- Automated data cleaning and structuring

### 🤖 AI-Powered Analysis
- Separates reviews into distinct components:
  - Plot Summary (Objective)
  - Personal Reactions (Subjective)
  - Critical Evaluation
  - Extended Analysis
- Generates comprehensive reports combining multiple perspectives
- Creates multi-persona discussions for deeper insights

### 💬 Interactive Chatbot
- Web-based interface for book discussions
- Dynamic conversation generation with multiple AI personas
- Bookmark creation with SVG/PNG/PDF export
- Customizable prompts for different discussion styles

## Installation

### Prerequisites
- Python 3.12+
- OpenAI API key

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/DeepReader.git
cd DeepReader

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="your-custom-endpoint"  # Optional
export DEEPREADER_MODEL_NAME="gpt-4"  # Optional
```

## Usage

### Running the Data Processing Pipeline

```bash
# Basic usage - process a single book
python reader/main.py --book "书名" --douban 1 --auto true

# With video processing
python reader/main.py --book "书名" --douban 1 --video ./video_file.txt --auto true

# Interactive mode (prompts for each step)
python reader/main.py --book "书名" --douban 2
```

### Starting the Web Interface

```bash
# Launch the Streamlit chatbot
streamlit run website/chatbot.py
```

The web interface will be available at `http://localhost:8501`

## Project Structure

```
DeepReader/
├── reader/               # Data processing pipeline
│   ├── main.py          # Main orchestration script
│   ├── douban_crawler.py    # Douban review scraper
│   ├── video_crawler.py     # Video download & transcription
│   ├── douban_cleaning.py   # Review data cleaning
│   ├── video_cleaning.py    # Video transcript processing
│   ├── parse_review.py      # Review categorization
│   └── report.py            # Report generation
│
├── website/             # Web interface
│   ├── chatbot.py       # Main Streamlit application
│   ├── prompt.py        # AI prompt management
│   ├── page2.py         # Bookmark generation
│   └── book_prompt/     # Book-specific prompts
│
├── requirements.txt     # Python dependencies
└── CLAUDE.md           # Development guidelines
```

## Adding New Books

1. Create a new file in `website/book_prompt/书名.md`
2. Use existing book prompts as templates
3. Include:
   - Book metadata (author, year, genre)
   - Plot summary
   - Main themes
   - Discussion points

## Development

For detailed development guidelines, architecture overview, and contribution instructions, please refer to [CLAUDE.md](CLAUDE.md).

### Key Technologies
- **Web Scraping**: BeautifulSoup4, Selenium
- **Video Processing**: yt-dlp, Whisper
- **AI/LLM**: OpenAI API
- **Web Framework**: Streamlit
- **Data Processing**: Pandas, CSV

## License
[MIT License](LICENSE)
