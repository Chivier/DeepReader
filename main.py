import douban_crawler
import video_crawler
import douban_cleaning
import video_cleaning
import parse_review
import report

import argparse

def main():
    parser = argparse.ArgumentParser()
    # douban book count
    parser.add_argument("--douban", type=int, default=1)
    # video url txt file path
    parser.add_argument("--video", type=str, default="video_link.txt")
    # book name
    parser.add_argument("--book", type=str, required=True)
    args = parser.parse_args()
    
    douban_count = args.douban
    video_url_file = args.video
    book_name = args.book
    
    print(f"Crawling {book_name} from douban")
    douban_spider = douban_crawler.DoubanBookSpider()
    douban_spider.crawl_book(book_name, douban_count)
    
    print(f"Crawling {book_name} from video")
    video_spider = video_crawler.VideoCrawler(book_name)
    video_spider.process_video_urls(video_url_file)
    
    print(f"Cleaning {book_name} from douban")
    douban_cleaning.clean_all_douban_files(book_name + "/website")
    
    print(f"Cleaning {book_name} from video")
    video_cleaning.clean_all_video_files(book_name + "/video")

    # print(f"Parsing {book_name} from douban")
    # parse_review.parse_douban_reviews(book_name)
    
    # print(f"Generating report for {book_name}")
    # report.report_parser(book_name)

if __name__ == "__main__":
    main()