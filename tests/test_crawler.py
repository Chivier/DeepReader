"""
Tests for crawler modules
"""

import pytest
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from reader.douban_crawler import DoubanBookSpider


class TestDoubanCrawler:
    """Test cases for Douban crawler"""
    
    def test_spider_initialization(self):
        """Test spider can be initialized"""
        spider = DoubanBookSpider()
        assert spider is not None
    
    def test_book_search_validation(self):
        """Test book name validation"""
        spider = DoubanBookSpider()
        
        # Test empty book name
        with pytest.raises(ValueError):
            spider.validate_book_name("")
        
        # Test valid book name
        result = spider.validate_book_name("三体")
        assert result == "三体"
    
    @pytest.mark.asyncio
    async def test_search_functionality(self):
        """Test search functionality (mock test)"""
        # This would require mocking actual HTTP requests
        # For now, just test the method exists
        spider = DoubanBookSpider()
        assert hasattr(spider, 'search_book')
        assert callable(getattr(spider, 'search_book', None))