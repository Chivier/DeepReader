# DeepReader API Documentation

## Overview

DeepReader provides both command-line and web interfaces for processing books and generating reviews.

## Command Line Interface

### Basic Usage

```bash
python reader/main.py --book "书名" --douban 1 --auto true
```

### Parameters

- `--book`: Book name (required)
- `--douban`: Number of Douban editions to crawl (default: 1)
- `--video`: Video source - "auto" for automatic search or file path (default: "auto")
- `--auto`: Automatic mode, no user prompts (default: False)
- `--auto-video`: Enable automatic Bilibili video search
- `--max-videos`: Maximum videos to download (default: 3)

### Examples

```bash
# Basic book processing
python reader/main.py --book "三体" --douban 1 --auto true

# With automatic video search
python reader/main.py --book "三体" --auto-video --max-videos 5

# Interactive mode
python reader/main.py --book "三体"
```

## Web Interface

### Starting the Server

```bash
streamlit run website/chatbot.py
```

### Features

- Interactive book discussions
- Bookmark generation
- Book management
- Multi-format export (SVG, PNG, PDF)

## API Modules

### Douban Crawler

```python
from reader.douban_crawler import DoubanBookSpider

spider = DoubanBookSpider()
spider.crawl_book("书名", count=1)
```

### Bilibili Auto Crawler

```python
from reader.bilibili_auto_crawler import auto_process_book_videos

result = auto_process_book_videos("书名", download_videos=True, max_videos=3)
```

### Review Parser

```python
from reader.parse_review import parse_reviews

parse_reviews("书名")
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_BASE_URL`: API endpoint URL
- `DEEPREADER_MODEL_NAME`: Model name to use

### File Structure

```
book_name/
├── website/          # Douban review data
├── video/           # Video content and subtitles
├── parsed_reviews/  # Processed review data
└── final_report.md  # Generated report
```