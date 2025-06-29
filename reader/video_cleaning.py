import nerif
import os
model_name = "gpt-4o-mini"

def clean_video(file_name):
    with open(file_name, "r") as f:
        text = f.read()
    
    prompt = f"""Act as a spelling corrector and improver. (replyWithRewrittenText)

Strictly follow these rules:
- Correct spelling, grammar and punctuation
- (maintainOriginalLanguage)
- NEVER surround the rewritten text with quotes
- (maintainURLs)
- Don't change emojis
- Split the text into paragraphs

Text: {text}

Fixed Text:
    """
    model = nerif.model.SimpleChatModel(model_name)
    response = model.chat(prompt)
    
    # print(response)
    
    new_file_name = file_name.replace(".txt", "_cleaned.txt")
    with open(new_file_name, "w") as f:
        f.write(response)
    return response

def clean_all_video_files(path="example_book/video"):
    # 检查目录是否存在
    if not os.path.exists(path):
        print(f"Video directory {path} does not exist, skipping video cleaning")
        return
    
    # 获取文件列表
    files = os.listdir(path)
    txt_files = [f for f in files if f.endswith(".txt") and not f.endswith("_cleaned.txt")]
    
    if not txt_files:
        print(f"No video transcript files found in {path}")
        return
    
    for file in txt_files:
        if file.endswith(".txt") and not file.endswith("_cleaned.txt"):
            print(f"Cleaning {file}")
            clean_video(f"{path}/{file}")

if __name__ == "__main__":
    clean_all_video_files()
