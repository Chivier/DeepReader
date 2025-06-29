# DeepReader Web Interface

## 启动应用

```bash
# 进入 website 目录
cd website

# 设置 Cairo 库路径（macOS）
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# 启动多页面应用
streamlit run Home.py

# 或使用启动脚本
./run_app.sh
```

## 页面结构

1. **主页 (Home.py)**: 应用介绍和导航
2. **聊天室 (pages/1_💬_聊天室.py)**: 书籍对话界面
3. **书籍生成器 (pages/2_📚_书籍生成器.py)**: 爬取书评并生成prompt

## 功能说明

### 聊天室
- 选择已有书籍进行对话
- 系统提示和推荐问题固定在顶部
- 支持生成书签（SVG/PNG/PDF）
- 侧边栏可快速导航到书籍生成器

### 书籍生成器
- 输入书名自动爬取豆瓣书评
- 可选自动搜索视频书评
- 实时显示处理进度
- 生成的prompt自动保存到 `book_prompt/` 目录
- 完成后可直接跳转到聊天界面

## 注意事项

1. 首次使用需要安装 Cairo 库：
   ```bash
   brew install cairo
   pip install cairosvg
   ```

2. 确保设置了必要的环境变量：
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL` (可选)
   - `DEEPREADER_MODEL_NAME` (可选)

3. 书籍生成过程耗时较长（3-15分钟），请耐心等待