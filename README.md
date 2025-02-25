# DeepReader

A sophisticated AI-powered system for generating high-quality book reviews and facilitating in-depth literary discussions.

[English](#english) | [中文](#chinese)

<a name="english"></a>,
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

---

<a name="chinese"></a>
## 中文

### 项目概述
DeepReader 是一个创新的 AI 驱动系统，旨在通过分析和整合各种来源的高质量书评，生成深度的读书报告和文学讨论。

### 项目起因
1. 提供高效的文学作品检索
2. 系统化整理观点，并提供原文引用
3. 促进深度思考和讨论

### 核心功能
1. **获取高质量书评**
   - 从大量优质书评中分析和思考
   - 对客观内容和主观评价进行分离
   - 进行有效的信息合并和讨论

2. **深度分析**
   - 对书评中引申话题进行挖掘
   - 实现更深层次的文学讨论
   - 生成类似 DeepResearch 的高质量长书评

### 系统模块

#### 数据收集
- 豆瓣长评爬虫
  - 对不同译本的评论进行整理和收集
- Bilibili/YouTube 视频爬取
  - 视频下载和字幕转换
  - 字幕校正处理

#### 数据处理
- 数据清洗
- 书评拆解为四个模块：
  - 剧情（客观内容）
  - 感受（个人体验）
  - 评价（主观评论）
  - 延伸思考（深度探讨）

### 未来规划
- 基于生成的长书评和 Deep Research 框架进行深度交互
- 结合 podcast 系统，实现 AI 驱动的书评播客
- 开发半自动播客生成系统

## License
[MIT License](LICENSE)
