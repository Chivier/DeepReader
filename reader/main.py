import time
import douban_crawler
import video_crawler
import douban_cleaning
import video_cleaning
from parse_review import parse_reviews
import report
from bilibili_auto_crawler import auto_process_book_videos

import threading
import os
import argparse

def show_waiting_animation(thread):
    dots = 0
    while thread.is_alive():
        print(".", end="", flush=True)
        time.sleep(0.5)
        dots += 1
        if dots >= 6:
            print("\r" + " " * 6 + "\r", end="", flush=True)
            dots = 0

def main():
    parser = argparse.ArgumentParser(description="DeepReader - AI书评生成系统")
    # douban book count
    parser.add_argument("--douban", type=int, default=1, help="豆瓣爬取书籍数量")
    # video url txt file path or auto search
    parser.add_argument("--video", type=str, default="auto", help="视频链接文件路径，或使用'auto'自动搜索")
    # book name
    parser.add_argument("--book", type=str, required=True, help="书籍名称")
    # auto mode
    parser.add_argument("--auto", type=bool, default=False, help="自动模式")
    # auto video search
    parser.add_argument("--auto-video", action="store_true", help="自动搜索Bilibili视频")
    # max videos to download
    parser.add_argument("--max-videos", type=int, default=3, help="最大视频下载数量")
    args = parser.parse_args()
    
    douban_count = args.douban
    video_url_file = args.video
    book_name = args.book
    auto = args.auto
    
    # -----------------------------------------------------
    # Auto search and download Bilibili videos
    # -----------------------------------------------------
    if args.auto_video or video_url_file == "auto":
        if auto:
            user_input = "Y"
        else:
            user_input = input(f"Auto search and process {book_name} videos from Bilibili? (Y/N): ")
        
        if user_input.upper() in ["Y", "YES"]:
            print(f"🔍 Starting auto video search for {book_name}...")
            
            def auto_video_process():
                result = auto_process_book_videos(
                    book_name, 
                    download_videos=True, 
                    max_videos=args.max_videos
                )
                return result
            
            # Start auto video processing in a thread
            print("Auto video processing", end="", flush=True)
            auto_thread = threading.Thread(target=auto_video_process)
            auto_thread.start()
            
            show_waiting_animation(auto_thread)
            print("\n✅ Auto video processing completed!")
    
    # -----------------------------------------------------
    # Manual video crawling (if video file is provided)
    # -----------------------------------------------------
    elif os.path.exists(video_url_file):
        if auto:
            user_input = "Y"
        else:
            user_input = input(f"Crawl {book_name} from manual video links? (Y/N): ")
        
        if user_input.upper() in ["Y", "YES"]:
            print(f"Starting to crawl {book_name} from video, please wait...")
            print("Spider is working", end="", flush=True)
            video_spider = video_crawler.VideoCrawler(book_name)
            # Start the crawling process in a thread
            crawl_thread = threading.Thread(target=video_spider.process_video_urls, args=(video_url_file,))
            crawl_thread.start()
            
            # Show animation while the thread is running
            show_waiting_animation(crawl_thread)
                    
            print("\nVideo crawling completed!")
    else:
        print(f"⚠️ Video file {video_url_file} not found, skipping video processing")
    
    # -----------------------------------------------------
    # Clean video
    # -----------------------------------------------------
    if auto:
        user_input = "Y"
    else:
        user_input = input(f"Clean {book_name} from video? (Y/N): ")
    if user_input.upper() in ["Y", "YES"]:
        print(f"Cleaning {book_name} from video, please wait...")
        print("Cleaning in progress", end="", flush=True)
        # Start the cleaning process in a thread
        clean_thread = threading.Thread(target=video_cleaning.clean_all_video_files, args=(book_name + "/video",))
        clean_thread.start()
        
        show_waiting_animation(clean_thread)
        
        print("\nVideo cleaning completed!")
    
    # -----------------------------------------------------
    # Crawl douban
    # -----------------------------------------------------
    if auto:
        user_input = "Y"
    else:
        user_input = input(f"Crawl {book_name} from douban? (Y/N): ")
    if user_input.upper() in ["Y", "YES"]:
        print(f"Starting to crawl {book_name} from douban, please wait...")
        # Create a background animation while the spider is working
        print("Spider is working", end="", flush=True)
        douban_spider = douban_crawler.DoubanBookSpider()
        # Start the crawling process
        crawl_thread = threading.Thread(target=douban_spider.crawl_book, args=(book_name, douban_count))
        crawl_thread.start()
        
        show_waiting_animation(crawl_thread)
        
        print("\nCrawling completed!")
    
    # -----------------------------------------------------
    # Clean douban
    # -----------------------------------------------------
    if auto:
        user_input = "Y"
    else:
        user_input = input(f"Clean {book_name} from douban? (Y/N): ")
    if user_input.upper() in ["Y", "YES"]:
        print(f"Cleaning {book_name} from douban, please wait...")
        print("Cleaning in progress", end="", flush=True)
        # Start the cleaning process in a thread
        clean_thread = threading.Thread(target=douban_cleaning.clean_all_douban_files, args=(book_name + "/website",))
        clean_thread.start()
        
        # Show animation while the thread is running
        show_waiting_animation(clean_thread)
        
        print("\nDouban cleaning completed!")
    
    # -----------------------------------------------------
    # Parse reviews
    # -----------------------------------------------------
    if auto:
        user_input = "Y"
    else:
        user_input = input(f"Parse {book_name} reviews? (Y/N): ")
    if user_input.upper() in ["Y", "YES"]:
        print(f"Parsing {book_name} reviews, please wait...")
        print("Parsing in progress", end="", flush=True)
        # Start the parsing process in a thread
        parse_thread = threading.Thread(target=parse_reviews, args=(book_name,))
        parse_thread.start()
        
        # Show animation while the thread is running
        show_waiting_animation(parse_thread)
        
        print("\nParsing completed!")
    
    # -----------------------------------------------------
    # Generate report
    # -----------------------------------------------------
    if auto:
        user_input = "Y"
    else:
        user_input = input(f"Generate report for {book_name}? (Y/N): ")
    if user_input.upper() in ["Y", "YES"]:
        print(f"Generating report for {book_name}, please wait...")
        print("Report generation in progress", end="", flush=True)
        # Start the report generation process in a thread
        report_thread = threading.Thread(target=report.report_parser, args=(book_name,))
        report_thread.start()
        
        # Show animation while the thread is running
        show_waiting_animation(report_thread)
        
        print("\nReport generation completed!")

if __name__ == "__main__":
    main()