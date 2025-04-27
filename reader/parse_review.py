import nerif
import os
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urlparse, parse_qs
import re
import autogen
from typing import List, Dict, Any, Optional

# model_name = "openrouter/deepseek/deepseek-r1"
model_name = "openrouter/anthropic/claude-3.7-sonnet"
# model_name = "ollama/deepseek-r1:32b"

model = nerif.model.SimpleChatModel(model_name)

prompt_story = """帮我从书评中找到这本书的剧情部分。请严格遵循以下规则：
- 输出所有和剧情部分相关的句子
- 请严格遵循书评原文的文本，不要进行任何修改
- 如果没有剧情部分，请输出"没有涉及剧情"

书评：
<REVIEW>

剧情：
"""

prompt_feeling = """帮我从书评中找到这本书的感受部分。请严格遵循以下规则：
- 输出所有和感受部分相关的句子
- 请严格遵循书评原文的文本，不要进行任何修改
- 如果没有感受部分，请输出"没有涉及感受"
书评：
<REVIEW>

阅读感受：
"""

prompt_evaluation = """帮我从书评中找到这本书的评价部分。请严格遵循以下规则：
- 输出所有和评价部分相关的句子
- 请严格遵循书评原文的文本，不要进行任何修改
- 如果没有评价部分，请输出"没有包含评价"

书评：
<REVIEW>

评价：
"""

prompt_thinking = """帮我从书评中找到这本书的思考部分。请严格遵循以下规则：
- 输出所有和思考部分相关的句子
- 和书本内容无关的句子都算是评论者的思考
- 和作者相关的生平经历也算做是评论者的思考
- 请严格遵循书评原文的文本，不要进行任何修改
- 如果没有思考部分，请输出"没有涉及思考"
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

JINA_READER_URL = os.environ.get('JINA_READER_URL', '')

def extract_subject_id(url):
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Parse the query parameters
    query_params = parse_qs(parsed_url.query)
    
    # Get the 'url' parameter which contains the actual book URL
    book_url = query_params.get('url', [''])[0]
    
    # Parse the book URL
    if book_url:
        book_url = urlparse(book_url)
        # Split the path and get the subject ID
        path_parts = book_url.path.split('/')
        # The subject ID is typically the second to last element
        subject_id = path_parts[-2] if len(path_parts) > 2 else None
        return subject_id
    
    return None

class DoubanBookSpider:
    def __init__(self, progress_callback=None):
        # set headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # douban search url
        self.search_url = 'https://www.douban.com/search?q={}&cat=1001'
        self.progress_callback = progress_callback
        
    def _report_progress(self, message):
        """Report progress if a callback is provided"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)
            
    def search_book(self, book_name) -> Optional[List[str]]:
        """search book, get book detail page url"""
        try:
            self._report_progress(f"Searching for book: {book_name}")
            response = requests.get(self.search_url.format(book_name), headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # find all h3 from soup, get the url from the href
            h3s = soup.find_all('h3')
            book_urls = []
            for h3 in h3s:
                url = h3.find('a')['href']
                # url example: 
                # https://www.douban.com/link2/?url=https%3A%2F%2Fbook.douban.com%2Fsubject%2F36860223%2F&query=%E7%AA%84%E9%97%A8&cat_id=1001&type=search&pos=11
                # get subject id from url params
                subject_id = extract_subject_id(url)
                book_urls.append(f"https://book.douban.com/subject/{subject_id}/")
            
            if len(book_urls) > 0:
                self._report_progress(f"Found {len(book_urls)} book URLs")
                return book_urls
            else:
                self._report_progress(f"No books found for: {book_name}")
                return None
        except Exception as e:
            self._report_progress(f"search book error: {e}")
            return None

    def get_book_info(self, book_url) -> Optional[Dict[str, str]]:
        """get book basic info"""
        try:
            self._report_progress(f"Getting book info from: {book_url}")
            response = requests.get(book_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # get title
            title = soup.find('h1').text.strip() if soup.find('h1') else ''
            
            # get rating
            rating = soup.find('strong', class_='ll rating_num')
            rating = rating.text.strip() if rating else 'no rating'
            
            # get author
            info = soup.find('div', id='info')
            author = info.find('a').text.strip() if info and info.find('a') else 'unknown author'
            
            book_info = {
                'title': title,
                'rating': rating,
                'author': author
            }
            self._report_progress(f"Retrieved info for book: {title}")
            return book_info
        except Exception as e:
            self._report_progress(f"get book info error: {e}")
            return None
        
    def get_review_urls(self, book_url, range=5) -> List[str]:
        """get long reviews"""
        offset = 0
        reviews = []
        self._report_progress(f"Collecting review URLs from: {book_url}")
        while offset < range:
            try:
                reviews_url = book_url + 'reviews/'
                if offset > 0:
                    reviews_url += f'?sort=hotest&start={offset * 20}'
                
                reader_url = JINA_READER_URL + reviews_url
                response = requests.get(reader_url, headers=self.headers)
                text = response.text
                # find all https://book.douban.com/review/5414380/ pattern
                pattern = r'https://book\.douban\.com/review/\d+/'
                matches = re.findall(pattern, text)
                reviews.extend(matches)
                self._report_progress(f"Found {len(matches)} reviews on page {offset+1}")
            except Exception as e:
                self._report_progress(f"get long reviews error: {e}")
                return reviews
            offset += 1
        return reviews

    def get_reviews(self, review_urls) -> List[List[str]]:
        """get long reviews content"""
        reviews = []
        total = len(review_urls)
        for i, review_url in enumerate(review_urls):
            review_url = JINA_READER_URL + review_url
            self._report_progress(f"Downloading review {i+1}/{total}: {review_url}")
            response = requests.get(review_url, headers=self.headers)
            text = response.text
            reviews.append([review_url, text])
            # sleep 10-15 random seconds
            wait_time = random.uniform(10, 15)
            self._report_progress(f"Waiting {wait_time:.1f}s before next request")
            time.sleep(wait_time)
            
        return reviews
    
    def crawl_book(self, book_name, limit=2) -> Dict[str, Any]:
        """main crawler function"""
        results = {
            "book_name": book_name,
            "success": False,
            "book_urls": [],
            "review_count": 0,
            "error": None
        }
        
        # search book
        if not os.path.exists(f"{book_name}/website"):
            os.makedirs(f"{book_name}/website")
            self._report_progress(f"Created directory: {book_name}/website")
        else:
            self._report_progress(f"Directory already exists: {book_name}/website")
            results["error"] = "Directory already exists, skipping crawl"
            return results
            
        book_urls = self.search_book(book_name)
        if not book_urls:
            results["error"] = f"Book {book_name} not found"
            self._report_progress(results["error"])
            return results
        
        results["book_urls"] = book_urls
        
        # get book reviews urls
        reviews_urls = []
        for book_url in book_urls[:limit]:
            reviews_urls.extend(self.get_review_urls(book_url))
        
        # get reviews
        reviews = self.get_reviews(reviews_urls)
        results["review_count"] = len(reviews)
        
        # Save reviews to files
        for review in reviews:
            review_url = review[0]
            review_text = review[1]
            review_id = review_url.split('/')[-2]
            review_id = review_id.split('?')[0]
            # Save review to {book_name}/website/douban_{review_id}.txt
            filepath = f"{book_name}/website/douban_{review_id}.txt"
            with open(filepath, "w") as f:
                f.write(review_text)
            self._report_progress(f"Saved review to: {filepath}")
        
        results["success"] = True
        self._report_progress(f"Successfully crawled {len(reviews)} reviews for {book_name}")
        return results

# Define AutoGen agent function
def autogen_crawl_book(book_name: str, limit: int = 2) -> Dict[str, Any]:
    """
    AutoGen-compatible function to crawl book reviews from Douban.
    
    Args:
        book_name: Name of the book to search for
        limit: Maximum number of book URLs to process
        
    Returns:
        Dictionary with crawling results
    """
    def progress_callback(message):
        print(f"Douban Crawler: {message}")
    
    spider = DoubanBookSpider(progress_callback=progress_callback)
    result = spider.crawl_book(book_name, limit)
    return result

# Register functions for AutoGen
def register_with_agent(agent):
    """Register crawler functions with an AutoGen agent"""
    agent.register_function(
        function_map={
            "crawl_douban_book": autogen_crawl_book,
        }
    )

# Setup AutoGen configuration
def setup_crawler_agent(config_list=None):
    """Set up and return a configured crawler agent"""
    if config_list is None:
        # Default configuration using local models
        config_list = [
            {
                "model": "ollama/qwen2.5:32b",
                "api_base": "http://localhost:11434",
            }
        ]
    
    # Create the agent
    crawler_agent = autogen.AssistantAgent(
        name="douban_crawler_agent",
        system_message="You are an agent specialized in crawling book information from Douban.",
        human_input_mode="NEVER",
        llm_config={"config_list": config_list},
    )
    
    # Register the functions with the agent
    register_with_agent(crawler_agent)
    
    return crawler_agent

if __name__ == "__main__":
    # Example usage with AutoGen
    config_list = [
        {
            "model": "ollama/qwen2.5:32b",
            "api_base": "http://localhost:11434",
        }
    ]
    
    crawler_agent = setup_crawler_agent(config_list)
    user_proxy = autogen.UserProxyAgent(
        name="user",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
    )
    
    # Start a conversation to crawl a book
    user_proxy.initiate_chat(
        crawler_agent,
        message="Crawl book reviews for '战略级天使' with a limit of 2 book URLs."
    )
