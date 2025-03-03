import pandas as pd
import os
import nerif

smart_model_name = "openrouter/deepseek/deepseek-r1"

def report_parser(book_name):
    file_path = f"{book_name}/parsed_data.csv"
    df = pd.read_csv(file_path)
    smart_model = nerif.model.SimpleChatModel(model=smart_model_name)
    
    story_prompt = f"""
    你是一个书评专家，我们在讨论的书是{book_name}，以下是一些用户对这本书剧情的描述，
    请根据这些描述，用 1000-2000 字描述这本书的剧情。
    
    """
    
    feeling_prompt = f"""
    你是一个书评专家，我们在讨论的书是{book_name}，以下是一些用户对这本书的感受，
    """
    
    evaluation_prompt = f"""
    你是一个书评专家，我们在讨论的书是{book_name}，以下是一些用户对这本书的评价，
    """
    
    thinking_prompt = f"""
    你是一个书评专家，我们在讨论的书是{book_name}，以下是一些用户对这本书的思考，
    """
    
    
    id = 0
    for index, row in df.iterrows():
        id += 1
        story = row["story"]
        feeling = row["feeling"]
        evaluation = row["evaluation"]
        thinking = row["thinking"]
        
        story_prompt = story_prompt + f"# {id} 的剧情描述：{story}\n"
        feeling_prompt = feeling_prompt + f"# {id} 的感受描述：{feeling}\n"
        evaluation_prompt = evaluation_prompt + f"# {id} 的评价描述：{evaluation}\n"
        thinking_prompt = thinking_prompt + f"# {id} 的思考描述：{thinking}\n"
        
    story_response = smart_model.chat(story_prompt)
    feeling_prompt = "我们今天来讨论一下 " + book_name + "，这本书大致说了：" + story_response + feeling_prompt + "请根据这些描述，用 2000-3000 字你阅读这本书的感受。"
    evaluation_prompt = "我们今天来讨论一下 " + book_name + "，这本书大致说了：" + story_response + evaluation_prompt + "请根据这些描述，用 2000-3000 字你阅读这本书的评价。分别探讨这本书的优点和缺点。"
    thinking_prompt = "我们今天来讨论一下 " + book_name + "，这本书大致说了：" + story_response + thinking_prompt + "请根据这些描述，用 3000-5000 字说说你阅读这本书的思考。可以一定程度上引申和拔高主题。"
    
    feeling_response = smart_model.chat(feeling_prompt)
    evaluation_response = smart_model.chat(evaluation_prompt)
    thinking_response = smart_model.chat(thinking_prompt)
    
    report_prompt = f"""帮我写一篇有深度的书评, 必须完整包含后面的所有内容：
    书名是{book_name}
    
    # 大致剧情：
    {story_response}
    
    # 感受：
    {feeling_response}
    
    # 评价：
    {evaluation_response}
    
    # 思考：
    {thinking_response}
    
    
    请用 markdown 格式输出，请严格遵循：
    - 不要包含任何除了 markdown 文档以外的其他内容。
    - 长度接近 8000 字。
    - 不要提到「用户xx认为」，的观点，用第一人称写书评。
    """
    
    with open(f"{book_name}_prompt.md", "w") as f:
        f.write(report_prompt)
    
    report_response = smart_model.chat(report_prompt)
    
    # 保存到文件
    with open(f"{book_name}.md", "w") as f:
        f.write(report_response)
    
    return report_response

if __name__ == "__main__":
    report_parser("战略级天使")