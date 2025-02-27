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
    for file in os.listdir(path):
        if file.endswith(".txt") and not file.endswith("_cleaned.txt"):
            print(f"Cleaning {file}")
            clean_video(f"{path}/{file}")

if __name__ == "__main__":
    clean_all_video_files()
