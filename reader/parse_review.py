import nerif
import os
import pandas as pd
import json

model_name = "openrouter/deepseek/deepseek-r1"
model_name = "openrouter/anthropic/claude-3.7-sonnet"
# model_name = "ollama/deepseek-r1:32b"

model = nerif.model.SimpleChatModel(model_name)

prompt_story = """帮我从书评中找到这本书的剧情部分。请严格遵循以下规则：
- 输出所有和剧情部分相关的句子
- 请严格遵循书评原文的文本，不要进行任何修改

书评：
<REVIEW>

剧情：
"""

prompt_feeling = """帮我从书评中找到这本书的感受部分。请严格遵循以下规则：
- 输出所有和感受部分相关的句子
- 请严格遵循书评原文的文本，不要进行任何修改

书评：
<REVIEW>

阅读感受：
"""

prompt_evaluation = """帮我从书评中找到这本书的评价部分。请严格遵循以下规则：
- 输出所有和评价部分相关的句子
- 请严格遵循书评原文的文本，不要进行任何修改

书评：
<REVIEW>

评价：
"""

prompt_thinking = """帮我从书评中找到这本书的思考部分。请严格遵循以下规则：
- 输出所有和思考部分相关的句子
- 和书本内容无关的句子都算是评论者的思考
- 和作者相关的生平经历也算做是评论者的思考
- 请严格遵循书评原文的文本，不要进行任何修改

书评：
<REVIEW>

思考：
"""

def review_parser(review_file):
    with open(review_file, "r", encoding="utf-8") as f:
        review = f.read()
    prompt1 = prompt_story.replace("<REVIEW>", review)
    story = model.chat(prompt1)
    prompt2 = prompt_feeling.replace("<REVIEW>", review)
    feeling = model.chat(prompt2)
    prompt3 = prompt_evaluation.replace("<REVIEW>", review)
    evaluation = model.chat(prompt3)
    prompt4 = prompt_thinking.replace("<REVIEW>", review)
    thinking = model.chat(prompt4)
    return story, feeling, evaluation, thinking



def parse_reviews(book_path="example_book"):
    douban_folder = os.path.join(book_path, "website")
    video_folder = os.path.join(book_path, "video")
    parsed_data = []
    # create a table with the following columns:

    # - source
    # - source_url
    # - story
    # - feeling
    # - evaluation
    # - thinking

    log_file = "log.txt"
    # read all files in the douban_folder
    for file in os.listdir(douban_folder):
        if file.endswith("cleaned.txt"):
            review_id = file.split("_cleaned.txt")[0]
            review_url = f"https://book.douban.com/review/{review_id}/"
            file_path = os.path.join(douban_folder, file)
            story, feeling, evaluation, thinking = review_parser(file_path)
            source = "douban"   
            parsed_data.append([source, review_url, story, feeling, evaluation, thinking])
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{file_path} parsed successfully\n")
                f.write(f"story: {story}\n")
                f.write(f"feeling: {feeling}\n")
                f.write(f"evaluation: {evaluation}\n")
                f.write(f"thinking: {thinking}\n")
                f.write("\n")
            

    # read all files in the video_folder
    for file in os.listdir(video_folder):
        if file.endswith("cleaned.txt"):
            review_id = file.split("_cleaned.txt")[0]
            if file.startswith("ytb_"):
                source = "youtube"
                review_url = f"https://www.youtube.com/watch?v={review_id}"
            elif file.startswith("bilibili_"):
                source = "bilibili"
                review_url = f"https://www.bilibili.com/video/{review_id}"
            else:
                source = "unknown"
                review_url = f"https://book.douban.com/review/{review_id}/"
            file_path = os.path.join(video_folder, file)
            story, feeling, evaluation, thinking = review_parser(file_path)
            parsed_data.append([source, review_url, story, feeling, evaluation, thinking])
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{file_path} parsed successfully\n")
                f.write(f"story: {story}\n")
                f.write(f"feeling: {feeling}\n")
                f.write(f"evaluation: {evaluation}\n")
                f.write(f"thinking: {thinking}\n")
                f.write("\n")
                
    # save the parsed data to a csv file
    csv_file_path = os.path.join(book_path, "parsed_data.csv")
    json_file_path = os.path.join(book_path, "parsed_data.json")
    df = pd.DataFrame(parsed_data, columns=["source", "source_url", "story", "feeling", "evaluation", "thinking"])
    df.to_csv(csv_file_path, index=False)

    # save the parsed data to a json file
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, ensure_ascii=False)
