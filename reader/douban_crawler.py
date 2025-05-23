import requests
import os
from bs4 import BeautifulSoup
import time
import json
import random
from urllib.parse import urlparse, parse_qs
import re

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
    def __init__(self):
        # set headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # douban search url
        self.search_url = 'https://www.douban.com/search?q={}&cat=1001'
        
    def search_book(self, book_name):
        """search book, get book detail page url"""
        try:
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
                return book_urls
            else:
                return None
        except Exception as e:
            print(f"search book error: {e}")
            return None

    def get_book_info(self, book_url):
        """get book basic info"""
        try:
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
            return book_info
        except Exception as e:
            print(f"get book info error: {e}")
            return None
        
    def get_review_urls(self, book_url, range=5):
        """get long reviews"""
        offset = 0
        reviews = []
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
            except Exception as e:
                print(f"get long reviews error: {e}")
                return reviews
            offset += 1
        return reviews

    def get_reviews(self, review_urls):
        """get long reviews content"""
        reviews = []
        for review_url in review_urls:
            review_url = JINA_READER_URL + review_url
            response = requests.get(review_url, headers=self.headers)
            text = response.text
            reviews.append([review_url, text])
            # sleep 10-15 random seconds
            time.sleep(random.uniform(10, 15))
            
        return reviews
    
    def crawl_book(self, book_name, limit=2):
        """main crawler function"""
        # search book
        if not os.path.exists(f"{book_name}/website"):
            os.makedirs(f"{book_name}/website")
        else:
            return
            
        book_urls = self.search_book(book_name)
        if not book_urls:
            print(f"Book {book_name} not found")
            return
        
        # get book reviews urls
        reviews_urls = []
        for book_url in book_urls[:limit]:
            reviews_urls.extend(self.get_review_urls(book_url))
        
        # get reviews
        reviews = self.get_reviews(reviews_urls)
        
        # Create directory structure: {book}/website/
        if not os.path.exists(f"{book_name}/website"):
            os.makedirs(f"{book_name}/website")

        for review in reviews:
            review_url = review[0]
            review_text = review[1]
            review_id = review_url.split('/')[-2]
            review_id = review_id.split('?')[0]
            # Save review to {book_name}/website/douban_{review_id}.txt
            with open(f"{book_name}/website/douban_{review_id}.txt", "w") as f:
                f.write(review_text)

if __name__ == "__main__":
    douban_spider = DoubanBookSpider()
    douban_spider.crawl_book("战略级天使")
