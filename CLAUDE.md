# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DeepReader is an AI-powered system for generating comprehensive book reviews and facilitating literary discussions. It consists of two main components:

1. **Data Collection & Processing Pipeline** (`reader/` directory)
   - Crawls and processes book reviews from Douban
   - Downloads and transcribes video reviews from Bilibili/YouTube
   - Cleans and structures review data
   - Generates comprehensive reports

2. **Interactive Web Interface** (`website/` directory)
   - Streamlit-based chatbot for book discussions
   - Multi-persona conversation system
   - Bookmark generation with SVG/PNG/PDF export
   - Dynamic prompt generation

## Common Development Commands

### Running the Main Pipeline
```bash
# Basic usage - process a single book
python reader/main.py --book "书名" --douban 1 --auto true

# With video processing
python reader/main.py --book "书名" --douban 1 --video ./video_file.txt --auto true

# Interactive mode (prompts for each step)
python reader/main.py --book "书名" --douban 2
```

### Running the Web Interface
```bash
# Start the Streamlit chatbot
streamlit run website/chatbot.py
```

### Installing Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

## Architecture Overview

### Data Flow
1. **Collection**: `douban_crawler.py` + `video_crawler.py` → Raw review data
2. **Cleaning**: `douban_cleaning.py` + `video_cleaning.py` → Structured data
3. **Processing**: `parse_review.py` → Categorized reviews (plot, reactions, analysis)
4. **Reporting**: `report.py` → Final comprehensive reports

### Key Components
- **Main Pipeline**: `reader/main.py` orchestrates the entire processing workflow
- **Web Interface**: `website/chatbot.py` provides interactive book discussions
- **Prompt System**: `website/prompt.py` manages AI conversation templates
- **Book Prompts**: `website/book_prompt/` contains structured book information

### File Structure
```
reader/           # Data processing pipeline
├── main.py       # Main orchestration script
├── *_crawler.py  # Data collection modules
├── *_cleaning.py # Data cleaning modules
├── parse_review.py # Review categorization
└── report.py     # Report generation

website/          # Web interface
├── chatbot.py    # Main Streamlit application
├── prompt.py     # AI prompt management
├── page2.py      # Additional UI components
└── book_prompt/  # Book-specific prompts (.md files)
```

## Environment Setup

### Required Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for LLM interactions
- `OPENAI_BASE_URL`: Custom OpenAI API endpoint (if using alternative provider)
- `DEEPREADER_MODEL_NAME`: Specific model name to use

### Python Requirements
- Python 3.12+ recommended
- Dependencies listed in `requirements.txt`
- Key libraries: streamlit, openai, beautifulsoup4, whisper, yt-dlp

## Development Guidelines

### Adding New Books
1. Add book information to `website/book_prompt/书名.md`
2. Use existing book prompts as templates
3. Include plot summary, themes, and discussion points

### Modifying AI Conversations
- Main conversation prompts in `website/prompt.py`
- System prompts use structured templates
- Multi-persona generation handled by `three_person_generation()`

### Data Processing Pipeline
- Each step is modular and can run independently
- Use `--auto true` flag for batch processing
- Interactive mode allows step-by-step execution

## Testing and Validation

### Manual Testing
- Use example commands from `run.sh` and `run2.sh`
- Test with different book names and parameter combinations
- Verify output quality in generated reports

### Web Interface Testing
- Start Streamlit app and test book selection
- Verify conversation flow and bookmark generation
- Check multi-persona dialogue functionality