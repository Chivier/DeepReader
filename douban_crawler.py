import requests
import os
from bs4 import BeautifulSoup
import time
import json
import random
from urllib.parse import urlparse, parse_qs
import re

JINA_READER_URL = "https://reader.victorique.site/"

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
        # 设置请求头，模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 豆瓣搜索URL
        self.search_url = 'https://www.douban.com/search?q={}&cat=1001'
        
    def search_book(self, book_name):
        """搜索图书，获取图书详情页URL"""
        try:
            response = requests.get(self.search_url.format(book_name), headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # find all h3 from soup, get the url from the href
            h3s = soup.find_all('h3')
            book_urls = []
            for h3 in h3s:
                url = h3.find('a')['href']
                # url example: https://www.douban.com/link2/?url=https%3A%2F%2Fbook.douban.com%2Fsubject%2F36860223%2F&query=%E7%AA%84%E9%97%A8&cat_id=1001&type=search&pos=11
                # get subject id from url params
                subject_id = extract_subject_id(url)
                book_urls.append(f"https://book.douban.com/subject/{subject_id}/")
            
            if len(book_urls) > 0:
                return book_urls
            else:
                return None
        except Exception as e:
            print(f"搜索图书时出错: {e}")
            return None

    def get_book_info(self, book_url):
        """获取图书基本信息"""
        try:
            response = requests.get(book_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取标题
            title = soup.find('h1').text.strip() if soup.find('h1') else ''
            
            # 获取评分
            rating = soup.find('strong', class_='ll rating_num')
            rating = rating.text.strip() if rating else '暂无评分'
            
            # 获取作者
            info = soup.find('div', id='info')
            author = info.find('a').text.strip() if info and info.find('a') else '未知作者'
            
            book_info = {
                'title': title,
                'rating': rating,
                'author': author
            }
            return book_info
        except Exception as e:
            print(f"获取图书信息时出错: {e}")
            return None
        
    def get_review_urls(self, book_url, range=5):
        """获取长评"""
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
                print(f"获取长评时出错: {e}")
                return reviews
            offset += 1
        return reviews

    def get_reviews(self, review_urls):
        """获取长评内容"""
        reviews = []
        for review_url in review_urls:
            review_url = JINA_READER_URL + review_url
            response = requests.get(review_url, headers=self.headers)
            text = response.text
            reviews.append([review_url, text])
            # sleep 1-1.5 random seconds
            time.sleep(random.uniform(1, 1.5))
            
        return reviews
    
    def crawl_book(self, book_name, output_dir="example_book"):
        """主爬虫函数"""
        # 搜索图书
        book_urls = self.search_book(book_name)
        if not book_urls:
            print(f"未找到图书: {book_name}")
            return
        
        # get book reviews urls
        reviews_urls = self.get_review_urls(book_urls[0])
        
        # get reviews
        reviews = self.get_reviews(reviews_urls)
        
        # Create directory structure: {output_dir}/website/
        if not os.path.exists(f"{output_dir}/website"):
            os.makedirs(f"{output_dir}/website")

        for review in reviews:
            review_url = review[0]
            review_text = review[1]
            review_id = review_url.split('/')[-2]
            review_id = review_id.split('?')[0]
            # Save review to {output_dir}/website/douban_{review_id}.txt
            with open(f"{output_dir}/website/douban_{review_id}.txt", "w") as f:
                f.write(review_text)