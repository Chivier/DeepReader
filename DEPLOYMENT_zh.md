# DeepReader 部署指南

## 项目概述

DeepReader 是一个基于人工智能的系统，用于生成全面的书评和促进文学讨论。本指南提供了在生产环境或开发环境中部署系统的详细说明。

## 系统要求

### 硬件要求
- **最低配置**: 4GB 内存，2核 CPU，20GB 存储空间
- **推荐配置**: 8GB 内存，4核 CPU，50GB 存储空间
- **视频处理**: 额外需要 10GB 临时存储空间

### 软件要求
- Python 3.9+（推荐 Python 3.12+）
- pip 或 conda 包管理器
- Git
- 互联网连接（用于 API 调用和网页爬取）

## 安装指南

### 1. 克隆仓库

```bash
git clone https://github.com/your-repo/DeepReader.git
cd DeepReader
```

### 2. 环境配置

#### 方法 A: 使用 pip（推荐）

```bash
# 创建虚拟环境
python -m venv deepreader-env
source deepreader-env/bin/activate  # Windows 用户: deepreader-env\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 方法 B: 使用 conda

```bash
# 创建 conda 环境
conda create -n deepreader python=3.12
conda activate deepreader

# 安装依赖
pip install -r requirements.txt
```

### 3. 环境变量配置

在项目根目录创建 `.env` 文件：

```bash
# 必需的 API 配置
OPENAI_API_KEY=你的_openai_api_密钥
OPENAI_BASE_URL=https://api.openai.com/v1
DEEPREADER_MODEL_NAME=gpt-4

# 可选：其他 API 提供商
# OPENAI_BASE_URL=https://api.deepseek.com/v1
# DEEPREADER_MODEL_NAME=deepseek-chat
```

### 4. 字体安装（用于书签生成）

```bash
# 为字体安装脚本添加执行权限并运行
chmod +x font-install.sh
./font-install.sh
```

## 部署选项

### 开发环境部署

用于开发和测试：

```bash
# 启动 Web 界面
streamlit run website/chatbot.py

# 应用将在 http://localhost:8501 可用
```

### 生产环境部署

#### 方法 1: 直接 Streamlit 部署

```bash
# 安装生产服务器
pip install streamlit

# 使用生产设置运行
streamlit run website/chatbot.py --server.port 8501 --server.address 0.0.0.0
```

#### 方法 2: Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    wget \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8501

# 运行应用
CMD ["streamlit", "run", "website/chatbot.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

构建和运行：

```bash
# 构建 Docker 镜像
docker build -t deepreader .

# 运行容器
docker run -p 8501:8501 --env-file .env deepreader
```

#### 方法 3: 云部署

##### Streamlit Cloud
1. 将代码推送到 GitHub 仓库
2. 将仓库连接到 Streamlit Cloud
3. 在 Streamlit Cloud 设置中添加环境变量
4. 自动部署

##### 其他云平台
- **Heroku**: 使用 `Procfile`，内容为 `web: streamlit run website/chatbot.py --server.port $PORT`
- **AWS/GCP/Azure**: 使用上述 Docker 镜像的容器服务

## 配置

### API 配置

系统支持多个 AI 提供商：

1. **OpenAI GPT 模型**:
   ```bash
   OPENAI_BASE_URL=https://api.openai.com/v1
   DEEPREADER_MODEL_NAME=gpt-4
   ```

2. **DeepSeek（推荐，成本效益高）**:
   ```bash
   OPENAI_BASE_URL=https://api.deepseek.com/v1
   DEEPREADER_MODEL_NAME=deepseek-chat
   ```

3. **其他兼容 OpenAI 的 API**:
   ```bash
   OPENAI_BASE_URL=你的_api_端点
   DEEPREADER_MODEL_NAME=你的_模型_名称
   ```

### 系统配置

关键配置文件：
- `requirements.txt`: Python 依赖
- `.env`: 环境变量
- `website/book_prompt/`: 书籍特定的提示和信息

## 使用方法

### 1. Web 界面

访问 Web 界面：`http://localhost:8501`（或你的部署 URL）。

功能特性：
- 交互式书籍讨论
- 多角色对话
- 书签生成和导出
- 书籍选择和管理

### 2. 命令行界面

通过 CLI 直接处理书籍：

```bash
# 基础书籍处理
python reader/main.py --book "书名" --douban 1 --auto true

# 包含视频处理
python reader/main.py --book "书名" --douban 1 --video video_links.txt --auto true

# 交互模式
python reader/main.py --book "书名"
```

### 3. 添加新书籍

1. **通过 Web 界面**: 使用书籍添加页面（即将推出）
2. **手动添加**: 在 `website/book_prompt/` 中创建 `.md` 文件

## 监控和维护

### 日志文件

应用日志存储在：
- `website/chat_history/`: 聊天对话日志
- `website/bookmarks/`: 生成的书签
- 各书籍目录中的书籍处理输出

### 性能监控

监控以下指标：
- API 响应时间
- 视频处理期间的内存使用
- 书籍数据的存储使用

### 备份和恢复

需要备份的重要目录：
- `website/book_prompt/`: 书籍信息
- `website/chat_history/`: 用户对话
- `website/bookmarks/`: 生成的书签
- 已处理的书籍数据目录

## 故障排除

### 常见问题

1. **API 密钥问题**:
   - 验证 API 密钥正确且有足够额度
   - 检查 API 端点 URL 格式

2. **字体问题**:
   - 运行 `font-install.sh` 脚本
   - 安装系统中文字体支持

3. **视频处理问题**:
   - 确保有足够的磁盘空间
   - 检查 yt-dlp 是否正确安装

4. **内存问题**:
   - 为处理大视频文件增加系统内存
   - 一次处理一本书

### 性能优化

1. **API 优化**:
   - 使用高效模型（如 deepseek-chat）
   - 实现请求缓存

2. **存储优化**:
   - 清理临时视频文件
   - 压缩处理后的数据

3. **网络优化**:
   - 为静态资源使用 CDN
   - 实现适当的缓存头

## 安全注意事项

1. **API 密钥**:
   - 绝不将 API 密钥提交到版本控制
   - 使用环境变量或安全密钥管理

2. **网页爬取**:
   - 遵守 robots.txt 和速率限制
   - 实现适当的错误处理

3. **用户数据**:
   - 实施数据保留政策
   - 安全存储聊天历史

## 支持和更新

如遇问题和更新：
- 检查 GitHub 仓库的最新版本
- 通过 GitHub issues 报告错误
- 遵循部署最佳实践进行更新

---

**注意**: 该系统设计用于教育和研究目的。在爬取内容时，请确保遵守所有适用法律和平台服务条款。