# DeepReader Deployment Guide

## Overview

DeepReader is an AI-powered system for generating comprehensive book reviews and facilitating literary discussions. This guide provides step-by-step instructions for deploying the system in production or development environments.

## System Requirements

### Hardware Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 20GB storage
- **Recommended**: 8GB RAM, 4 CPU cores, 50GB storage
- **For video processing**: Additional 10GB temporary storage

### Software Requirements
- Python 3.9+ (Python 3.12+ recommended)
- pip or conda package manager
- Git
- Internet connection for API calls and web scraping

## Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/DeepReader.git
cd DeepReader
```

### 2. Environment Setup

#### Option A: Using pip (Recommended)

```bash
# Create virtual environment
python -m venv deepreader-env
source deepreader-env/bin/activate  # On Windows: deepreader-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using conda

```bash
# Create conda environment
conda create -n deepreader python=3.12
conda activate deepreader

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables Configuration

Create a `.env` file in the project root:

```bash
# Required API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
DEEPREADER_MODEL_NAME=gpt-4

# Optional: Alternative API providers
# OPENAI_BASE_URL=https://api.deepseek.com/v1
# DEEPREADER_MODEL_NAME=deepseek-chat
```

### 4. Font Installation (For Bookmark Generation)

```bash
# Make font installation script executable and run
chmod +x font-install.sh
./font-install.sh
```

## Deployment Options

### Development Deployment

For development and testing:

```bash
# Start the web interface
streamlit run website/chatbot.py

# The application will be available at http://localhost:8501
```

### Production Deployment

#### Option 1: Direct Streamlit Deployment

```bash
# Install production server
pip install streamlit

# Run with production settings
streamlit run website/chatbot.py --server.port 8501 --server.address 0.0.0.0
```

#### Option 2: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "website/chatbot.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

Build and run:

```bash
# Build Docker image
docker build -t deepreader .

# Run container
docker run -p 8501:8501 --env-file .env deepreader
```

#### Option 3: Cloud Deployment

##### Streamlit Cloud
1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Add environment variables in Streamlit Cloud settings
4. Deploy automatically

##### Other Cloud Platforms
- **Heroku**: Use `Procfile` with `web: streamlit run website/chatbot.py --server.port $PORT`
- **AWS/GCP/Azure**: Use container services with the Docker image above

## Configuration

### API Configuration

The system supports multiple AI providers:

1. **OpenAI GPT Models**:
   ```bash
   OPENAI_BASE_URL=https://api.openai.com/v1
   DEEPREADER_MODEL_NAME=gpt-4
   ```

2. **DeepSeek (Recommended for cost-effectiveness)**:
   ```bash
   OPENAI_BASE_URL=https://api.deepseek.com/v1
   DEEPREADER_MODEL_NAME=deepseek-chat
   ```

3. **Other OpenAI-compatible APIs**:
   ```bash
   OPENAI_BASE_URL=your_api_endpoint
   DEEPREADER_MODEL_NAME=your_model_name
   ```

### System Configuration

Key configuration files:
- `requirements.txt`: Python dependencies
- `.env`: Environment variables
- `website/book_prompt/`: Book-specific prompts and information

## Usage

### 1. Web Interface

Access the web interface at `http://localhost:8501` (or your deployed URL).

Features:
- Interactive book discussions
- Multi-persona conversations
- Bookmark generation and export
- Book selection and management

### 2. Command Line Interface

Process books directly via CLI:

```bash
# Basic book processing
python reader/main.py --book "Book Title" --douban 1 --auto true

# With video processing
python reader/main.py --book "Book Title" --douban 1 --video video_links.txt --auto true

# Interactive mode
python reader/main.py --book "Book Title"
```

### 3. Adding New Books

1. **Via Web Interface**: Use the book addition page (coming soon)
2. **Manual Addition**: Create `.md` files in `website/book_prompt/`

## Monitoring and Maintenance

### Log Files

Application logs are stored in:
- `website/chat_history/`: Chat conversation logs
- `website/bookmarks/`: Generated bookmarks
- Book processing outputs in respective book directories

### Performance Monitoring

Monitor these metrics:
- API response times
- Memory usage during video processing
- Storage usage for book data

### Backup and Recovery

Important directories to backup:
- `website/book_prompt/`: Book information
- `website/chat_history/`: User conversations
- `website/bookmarks/`: Generated bookmarks
- Processed book data directories

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Verify API key is correct and has sufficient credits
   - Check API endpoint URL format

2. **Font Issues**:
   - Run `font-install.sh` script
   - Install system fonts for Chinese text support

3. **Video Processing Issues**:
   - Ensure sufficient disk space
   - Check yt-dlp is properly installed

4. **Memory Issues**:
   - Increase system memory for large video files
   - Process books one at a time

### Performance Optimization

1. **API Optimization**:
   - Use efficient models (e.g., deepseek-chat)
   - Implement request caching

2. **Storage Optimization**:
   - Clean up temporary video files
   - Compress processed data

3. **Network Optimization**:
   - Use CDN for static assets
   - Implement proper caching headers

## Security Considerations

1. **API Keys**:
   - Never commit API keys to version control
   - Use environment variables or secure key management

2. **Web Scraping**:
   - Respect robots.txt and rate limits
   - Implement proper error handling

3. **User Data**:
   - Implement data retention policies
   - Secure chat history storage

## Support and Updates

For issues and updates:
- Check the GitHub repository for latest releases
- Report bugs via GitHub issues
- Follow deployment best practices for updates

---

**Note**: This system is designed for educational and research purposes. Ensure compliance with all applicable laws and platform terms of service when scraping content.