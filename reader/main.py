import time
import os
import argparse
import threading
import autogen

# Import your existing modules
import douban_crawler
import video_crawler
import douban_cleaning
import video_cleaning
from parse_review import parse_reviews
import report


class TaskAgent:
    """Agent responsible for executing specific book analysis tasks"""
    
    def __init__(self, book_name, douban_count=1, video_url_file="video_link.txt"):
        self.book_name = book_name
        self.douban_count = douban_count
        self.video_url_file = video_url_file
        
    def crawl_video(self):
        """Crawl video content for the book"""
        print(f"Starting to crawl {self.book_name} from video, please wait...")
        video_spider = video_crawler.VideoCrawler(self.book_name)
        video_spider.process_video_urls(self.video_url_file)
        return "Video crawling completed!"
    
    def clean_video(self):
        """Clean video data for the book"""
        print(f"Cleaning {self.book_name} from video, please wait...")
        video_cleaning.clean_all_video_files(f"{self.book_name}/video")
        return "Video cleaning completed!"
    
    def crawl_douban(self):
        """Crawl Douban content for the book"""
        print(f"Starting to crawl {self.book_name} from douban, please wait...")
        douban_spider = douban_crawler.DoubanBookSpider()
        douban_spider.crawl_book(self.book_name, self.douban_count)
        return "Douban crawling completed!"
    
    def clean_douban(self):
        """Clean Douban data for the book"""
        print(f"Cleaning {self.book_name} from douban, please wait...")
        douban_cleaning.clean_all_douban_files(f"{self.book_name}/website")
        return "Douban cleaning completed!"
    
    def parse_book_reviews(self):
        """Parse reviews for the book"""
        print(f"Parsing {self.book_name} reviews, please wait...")
        parse_reviews(self.book_name)
        return "Review parsing completed!"
    
    def generate_report(self):
        """Generate analysis report for the book"""
        print(f"Generating report for {self.book_name}, please wait...")
        report.report_parser(self.book_name)
        return "Report generation completed!"


class ProgressDisplay:
    """Displays progress animation during tasks"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the progress animation"""
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the progress animation"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("\r" + " " * 20 + "\r", end="", flush=True)  # Clear animation
    
    def _animate(self):
        """Display the dots animation"""
        dots = 0
        while self.running:
            print(".", end="", flush=True)
            time.sleep(0.5)
            dots += 1
            if dots >= 6:
                print("\r" + " " * 6 + "\r", end="", flush=True)
                dots = 0


class WorkflowManager:
    """Manages the overall book analysis workflow"""
    
    def __init__(self, book_name, douban_count=1, video_url_file="video_link.txt", auto_mode=False):
        self.book_name = book_name
        self.task_agent = TaskAgent(book_name, douban_count, video_url_file)
        self.progress = ProgressDisplay()
        self.auto_mode = auto_mode
        
        # Define the workflow steps and corresponding agent methods
        self.workflow_steps = [
            {"name": f"Crawl {book_name} from video", "method": self.task_agent.crawl_video},
            {"name": f"Clean {book_name} from video", "method": self.task_agent.clean_video},
            {"name": f"Crawl {book_name} from douban", "method": self.task_agent.crawl_douban},
            {"name": f"Clean {book_name} from douban", "method": self.task_agent.clean_douban},
            {"name": f"Parse {book_name} reviews", "method": self.task_agent.parse_book_reviews},
            {"name": f"Generate report for {book_name}", "method": self.task_agent.generate_report}
        ]
    
    def execute_step(self, step):
        """Execute a single workflow step with progress animation"""
        if self.auto_mode or self.get_user_confirmation(step["name"]):
            self.progress.start()
            try:
                result = step["method"]()
                self.progress.stop()
                print(f"\n{result}")
            except Exception as e:
                self.progress.stop()
                print(f"\nError during {step['name']}: {str(e)}")
    
    def get_user_confirmation(self, task_name):
        """Get user confirmation for a task"""
        user_input = input(f"{task_name}? (Y/N): ")
        return user_input.upper() in ["Y", "YES"]
    
    def run_workflow(self):
        """Run the complete book analysis workflow"""
        print(f"Starting analysis workflow for '{self.book_name}'")
        for step in self.workflow_steps:
            self.execute_step(step)
        print(f"Analysis workflow for '{self.book_name}' completed!")


def main():
    parser = argparse.ArgumentParser(description="Book Analysis Workflow")
    parser.add_argument("--douban", type=int, default=1, help="Number of Douban book entries to process")
    parser.add_argument("--video", type=str, default="video_link.txt", help="Path to video URL text file")
    parser.add_argument("--book", type=str, required=True, help="Book name to analyze")
    parser.add_argument("--auto", action="store_true", help="Run in automatic mode without prompts")
    args = parser.parse_args()
    
    # Set up the autogen system configuration
    config = {
        "seed": 42,  # For reproducibility
        "temperature": 0,  # Deterministic responses
        "config_list": autogen.config_list_from_json(
            "OAI_CONFIG_LIST",  # This would be your API configuration list
            filter_dict={"model": ["gpt-4"]}
        ),
    }
    
    # Create the workflow manager instance
    workflow_manager = WorkflowManager(
        book_name=args.book,
        douban_count=args.douban,
        video_url_file=args.video,
        auto_mode=args.auto
    )
    
    # Create agents (in a real implementation, these would communicate with each other)
    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        code_execution_config={"work_dir": "coding"}
    )
    
    assistant = autogen.AssistantAgent(
        name="BookAnalysisAssistant",
        system_message="You are a helpful assistant for book analysis.",
        llm_config=config,
    )
    
    # Run the workflow
    workflow_manager.run_workflow()


if __name__ == "__main__":
    main()
