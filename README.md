# DeepReader

A sophisticated AI-powered system for generating high-quality book reviews and facilitating in-depth literary discussions.

## English

### Overview
DeepReader is an innovative project designed to generate comprehensive and insightful book reviews by analyzing and synthesizing high-quality reviews from various sources. The system aims to create meaningful literary discussions by separating objective content from subjective interpretations and exploring deeper themes.

### Key Features
1. **Intelligent Review Collection**
   - Scrapes and processes reviews from Douban
   - Extracts content from Bilibili/YouTube book review videos
   - Handles multiple translations and editions

2. **Content Analysis**
   - Separates reviews into distinct components:
     - Plot Summary (Objective)
     - Personal Reactions (Subjective)
     - Critical Evaluation
     - Extended Analysis

3. **Advanced Processing**
   - Merges objective plot information
   - Analyzes subjective viewpoints
   - Generates comprehensive discussions
   - Integrates with web search for expanded context

### Modules

#### Data Collection
- Douban review crawler
  - Organizes reviews across different translations
- Video content processing
  - Downloads and transcribes video reviews
  - Subtitle correction and processing

#### Data Processing
- Data cleaning and standardization
- Review decomposition into structured components
- CSV format generation for structured analysis

### Future Development
- Integration with Deep Research framework for interactive discussions
- Podcast generation featuring AI-powered literary discussions
- Semi-automated podcast production system

## License
[MIT License](LICENSE)
