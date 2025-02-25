import nerif
import os

clean_model_name = "ollama/qwen2.5:32b"

def clean_douban(file_name):
    # store the text in a new file
    new_file_name = file_name.split(".")[0] + "_cleaned.txt"

    with open(file_name, "r") as f:
        text = f.read()
    
    if not "下载豆瓣客户端" in text:
        with open(new_file_name, "w") as f:
            f.write(text)
        return
        
        
    if "有关键情节透露" in text:
        # remove the line contains "有关键情节透露" and the following lines
        text = text.split("有关键情节透露")[0]
    
    tagline = "[](https://book.douban.com/annual/2024/?fullscreen=1&&dt_from=book_navigation)"
    if tagline in text:
        # remove all information before the tagline
        text = text.split(tagline)[1]

    with open(new_file_name, "w") as f:
        f.write(text)

def clean_all_douban_files(dir_name):
    for file_name in os.listdir(dir_name):
        if "cleaned" in file_name:
            continue
        clean_douban(os.path.join(dir_name, file_name))

if __name__ == "__main__":
    clean_all_douban_files("example_book/website")
