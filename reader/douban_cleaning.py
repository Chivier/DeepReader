import autogen
from typing import List, Optional, Dict, Any
import os
import argparse

# Define the configuration for AutoGen agents
config_list = [
    {
        "model": "ollama/qwen2.5:32b",
        "api_base": "http://localhost:11434",
    }
]

# Define the assistant configurations
assistant_config = {
    "name": "book_assistant",
    "system_message": "You are a helpful assistant for book analysis.",
    "human_input_mode": "NEVER",
    "llm_config": {"config_list": config_list},
}

crawler_config = {
    "name": "crawler_agent",
    "system_message": "You are an agent specialized in crawling book information.",
    "human_input_mode": "NEVER",
    "llm_config": {"config_list": config_list},
}

cleaning_config = {
    "name": "cleaning_agent",
    "system_message": "You are an agent specialized in cleaning and processing text data.",
    "human_input_mode": "NEVER",
    "llm_config": {"config_list": config_list},
}

analysis_config = {
    "name": "analysis_agent",
    "system_message": "You are an agent specialized in analyzing book data and generating reports.",
    "human_input_mode": "NEVER", 
    "llm_config": {"config_list": config_list},
}

# Create the agents
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    system_message="A human user who interacts with the AI assistants.",
)

book_assistant = autogen.AssistantAgent(**assistant_config)
crawler_agent = autogen.AssistantAgent(**crawler_config)
cleaning_agent = autogen.AssistantAgent(**cleaning_config)
analysis_agent = autogen.AssistantAgent(**analysis_config)

# Import the necessary modules for the tasks
import douban_crawler
import video_crawler
import douban_cleaning
import video_cleaning
from parse_review import parse_reviews
import report
import threading

# Define the functions for each task
def crawl_douban(book_name: str, count: int = 1) -> None:
    """Crawl book information from Douban."""
    douban_spider = douban_crawler.DoubanBookSpider()
    douban_spider.crawl_book(book_name, count)
    return f"Completed crawling {count} books for '{book_name}' from Douban."

def crawl_video(book_name: str, video_url_file: str) -> None:
    """Crawl video information related to the book."""
    video_spider = video_crawler.VideoCrawler(book_name)
    video_spider.process_video_urls(video_url_file)
    return f"Completed crawling videos for '{book_name}' from {video_url_file}."

def clean_douban_data(book_name: str) -> None:
    """Clean the Douban book information."""
    douban_cleaning.clean_all_douban_files(f"{book_name}/website")
    return f"Completed cleaning Douban data for '{book_name}'."

def clean_video_data(book_name: str) -> None:
    """Clean the video transcriptions."""
    video_cleaning.clean_all_video_files(f"{book_name}/video")
    return f"Completed cleaning video data for '{book_name}'."

def parse_book_reviews(book_name: str) -> None:
    """Parse and analyze book reviews."""
    parse_reviews(book_name)
    return f"Completed parsing reviews for '{book_name}'."

def generate_report(book_name: str) -> None:
    """Generate a comprehensive report for the book."""
    report.report_parser(book_name)
    return f"Completed generating report for '{book_name}'."

# Register the functions with the agents
def register_functions():
    # Register crawler functions
    crawler_agent.register_function(
        function_map={
            "crawl_douban": crawl_douban,
            "crawl_video": crawl_video,
        }
    )
    
    # Register cleaning functions
    cleaning_agent.register_function(
        function_map={
            "clean_douban_data": clean_douban_data,
            "clean_video_data": clean_video_data,
        }
    )
    
    # Register analysis functions
    analysis_agent.register_function(
        function_map={
            "parse_book_reviews": parse_book_reviews,
            "generate_report": generate_report,
        }
    )

def process_book(book_name: str, douban_count: int = 1, video_url_file: str = "video_link.txt", auto: bool = False):
    """Process a book using the agent-based workflow."""
    
    # Register all functions
    register_functions()
    
    # Create the workflow for processing the book
    task_description = f"""
    Process the book '{book_name}' with the following steps:
    
    1. Crawl information from Douban (count: {douban_count})
    2. Crawl video information (from file: {video_url_file})
    3. Clean the Douban data
    4. Clean the video data
    5. Parse and analyze book reviews
    6. Generate a comprehensive report
    
    Please execute each step in order and provide updates after each step.
    """
    
    # Start the conversation between agents
    user_proxy.initiate_chat(
        book_assistant,
        message=task_description
    )
    
    # The assistant will coordinate with other agents to complete the task

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--douban", type=int, default=1, help="Number of Douban books to crawl")
    parser.add_argument("--video", type=str, default="video_link.txt", help="Path to video URL file")
    parser.add_argument("--book", type=str, required=True, help="Book name to process")
    parser.add_argument("--auto", action="store_true", help="Run in automatic mode without prompts")
    
    args = parser.parse_args()
    
    process_book(
        book_name=args.book,
        douban_count=args.douban,
        video_url_file=args.video,
        auto=args.auto
    )

if __name__ == "__main__":
    main()
