import requests
import os
from bs4 import BeautifulSoup
import time
import json
import random
from urllib.parse import urlparse, parse_qs
import re
import autogen
from typing import List, Dict, Any, Optional

JINA_READER_URL = os.environ.get('JINA_READER_URL', '')

def extract_subject_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    book_url = query_params.get('url', [''])[0]
    
    if book_url:
        book_url = urlparse(book_url)
        path_parts = book_url.path.split('/')
        subject_id = path_parts[-2] if len(path_parts) > 2 else None
        return subject_id
    
    return None

class DoubanBookSpider:
    def __init__(self, progress_callback=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.search_url = 'https://www.douban.com/search?q={}&cat=1001'
        self.progress_callback = progress_callback
        
    def _report_progress(self, message):
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)
            
    def search_book(self, book_name) -> Optional[List[str]]:
        try:
            self._report_progress(f"Searching for book: {book_name}")
            response = requests.get(self.search_url.format(book_name), headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            h3s = soup.find_all('h3')
            book_urls = []
            for h3 in h3s:
                url = h3.find('a')['href']
                subject_id = extract_subject_id(url)
                book_urls.append(f"https://book.douban.com/subject/{subject_id}/")
            
            if len(book_urls) > 0:
                self._report_progress(f"Found {len(book_urls)} book URLs")
                return book_urls
            else:
                self._report_progress(f"No books found for: {book_name}")
                return None
        except Exception as e:
            self._report_progress(f"Search book error: {e}")
            return None

    def get_book_info(self, book_url) -> Optional[Dict[str, str]]:
        try:
            self._report_progress(f"Getting book info from: {book_url}")
            response = requests.get(book_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('h1').text.strip() if soup.find('h1') else ''
            rating = soup.find('strong', class_='ll rating_num')
            rating = rating.text.strip() if rating else 'no rating'
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
            self._report_progress(f"Get book info error: {e}")
            return None
        
    def get_review_urls(self, book_url, range=5) -> List[str]:
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
                pattern = r'https://book\.douban\.com/review/\d+/'
                matches = re.findall(pattern, text)
                reviews.extend(matches)
                self._report_progress(f"Found {len(matches)} reviews on page {offset+1}")
            except Exception as e:
                self._report_progress(f"Get review URLs error: {e}")
                return reviews
            offset += 1
        return reviews

    def get_reviews(self, review_urls) -> List[List[str]]:
        reviews = []
        total = len(review_urls)
        for i, review_url in enumerate(review_urls):
            self._report_progress(f"Downloading review {i+1}/{total}: {review_url}")
            review_url = JINA_READER_URL + review_url
            response = requests.get(review_url, headers=self.headers)
            text = response.text
            reviews.append([review_url, text])
            wait_time = random.uniform(10, 15)
            self._report_progress(f"Waiting {wait_time:.1f}s before next request")
            time.sleep(wait_time)
            
        return reviews
    
    def crawl_book(self, book_name, limit=2) -> Dict[str, Any]:
        results = {
            "book_name": book_name,
            "success": False,
            "book_urls": [],
            "review_count": 0,
            "error": None
        }
        
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
        
        reviews_urls = []
        for book_url in book_urls[:limit]:
            reviews_urls.extend(self.get_review_urls(book_url))
        
        reviews = self.get_reviews(reviews_urls)
        results["review_count"] = len(reviews)
        
        for review in reviews:
            review_url = review[0]
            review_text = review[1]
            review_id = review_url.split('/')[-2]
            review_id = review_id.split('?')[0]
            filepath = f"{book_name}/website/douban_{review_id}.txt"
            with open(filepath, "w") as f:
                f.write(review_text)
            self._report_progress(f"Saved review to: {filepath}")
        
        results["success"] = True
        self._report_progress(f"Successfully crawled {len(reviews)} reviews for {book_name}")
        return results

# AutoGen function for crawling books
def crawl_douban_book(book_name: str, limit: int = 2) -> Dict[str, Any]:
    """
    AutoGen-compatible function to crawl book reviews from Douban.
    
    Args:
        book_name: Name of the book to search for
        limit: Maximum number of book URLs to process
        
    Returns:
        Dictionary with crawling results
    """
    spider = DoubanBookSpider()
    return spider.crawl_book(book_name, limit)

# Register functions with AutoGen
def register_functions(agent):
    """Register crawler functions with an AutoGen agent"""
    agent.register_function(
        function_map={
            "crawl_douban_book": crawl_douban_book,
        }
    )

if __name__ == "__main__":
    # Create config for AutoGen
    config_list = [
        {
            "model": "ollama/qwen2.5:32b",
            "api_base": "http://localhost:11434",
        }
    ]
    
    # Create AutoGen agents
    crawler_agent = autogen.AssistantAgent(
        name="douban_crawler",
        system_message="You are an agent specialized in crawling book information from Douban.",
        llm_config={"config_list": config_list},
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="user",
        human_input_mode="TERMINATE",
    )
    
    # Register the crawler function
    register_functions(crawler_agent)
    
    # Start a conversation to crawl a book
    user_proxy.initiate_chat(
        crawler_agent,
        message="Crawl book reviews for '战略级天使' with a limit of 2."
    )