"""
Bilibili 自动视频搜索和下载模块
自动搜索和这本书相关的，超过 5 分钟的中长视频
"""

import requests
import json
import time
import os
import re
from datetime import datetime
import yt_dlp
from typing import List, Dict, Optional

class BilibiliAutoCrawler:
    """Bilibili 自动爬虫类"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def search_videos(self, book_name: str, min_duration: int = 300) -> List[Dict]:
        """
        搜索与书籍相关的视频
        
        Args:
            book_name: 书籍名称
            min_duration: 最小时长（秒），默认5分钟
            
        Returns:
            视频信息列表
        """
        print(f"正在搜索《{book_name}》相关视频...")
        
        # 构建搜索关键词
        search_keywords = [
            f"{book_name} 书评",
            f"{book_name} 解读",
            f"{book_name} 分析",
            f"{book_name} 读后感",
            f"{book_name} 推荐"
        ]
        
        all_videos = []
        
        for keyword in search_keywords:
            try:
                videos = self._search_single_keyword(keyword, min_duration)
                all_videos.extend(videos)
                time.sleep(1)  # 避免请求过于频繁
            except Exception as e:
                print(f"搜索关键词 '{keyword}' 时出错: {e}")
                continue
        
        # 去重和排序
        unique_videos = self._deduplicate_videos(all_videos)
        sorted_videos = sorted(unique_videos, key=lambda x: x.get('play_count', 0), reverse=True)
        
        print(f"找到 {len(sorted_videos)} 个相关视频")
        return sorted_videos[:10]  # 返回前10个最热门的视频
    
    def _search_single_keyword(self, keyword: str, min_duration: int) -> List[Dict]:
        """搜索单个关键词"""
        search_url = "https://api.bilibili.com/x/web-interface/search/type"
        
        params = {
            'search_type': 'video',
            'keyword': keyword,
            'order': 'totalrank',  # 按综合排序
            'duration': 3,  # 10-30分钟
            'page': 1,
            'page_size': 20
        }
        
        try:
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') != 0:
                print(f"API返回错误: {data.get('message', 'Unknown error')}")
                return []
            
            videos = []
            for item in data.get('data', {}).get('result', []):
                video_info = self._parse_video_info(item)
                if video_info and video_info.get('duration', 0) >= min_duration:
                    videos.append(video_info)
            
            return videos
            
        except Exception as e:
            print(f"搜索请求失败: {e}")
            return []
    
    def _parse_video_info(self, item: Dict) -> Optional[Dict]:
        """解析视频信息"""
        try:
            # 解析时长
            duration_str = item.get('duration', '')
            duration = self._parse_duration(duration_str)
            
            # 解析播放量
            play_count = self._parse_play_count(item.get('play', ''))
            
            video_info = {
                'bvid': item.get('bvid', ''),
                'title': self._clean_title(item.get('title', '')),
                'author': item.get('author', ''),
                'duration': duration,
                'play_count': play_count,
                'description': item.get('description', ''),
                'url': f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                'pic': item.get('pic', ''),
                'pubdate': item.get('pubdate', 0)
            }
            
            return video_info
            
        except Exception as e:
            print(f"解析视频信息失败: {e}")
            return None
    
    def _parse_duration(self, duration_str: str) -> int:
        """解析时长字符串为秒数"""
        try:
            if not duration_str:
                return 0
            
            parts = duration_str.split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            else:
                return 0
        except:
            return 0
    
    def _parse_play_count(self, play_str: str) -> int:
        """解析播放量字符串为数字"""
        try:
            if not play_str:
                return 0
            
            # 移除HTML标签
            play_str = re.sub(r'<[^>]+>', '', play_str)
            
            # 处理万、千等单位
            if '万' in play_str:
                number = float(re.search(r'([\d.]+)', play_str).group(1))
                return int(number * 10000)
            elif '千' in play_str:
                number = float(re.search(r'([\d.]+)', play_str).group(1))
                return int(number * 1000)
            else:
                number = re.search(r'(\d+)', play_str)
                return int(number.group(1)) if number else 0
                
        except:
            return 0
    
    def _clean_title(self, title: str) -> str:
        """清理标题中的HTML标签"""
        return re.sub(r'<[^>]+>', '', title)
    
    def _deduplicate_videos(self, videos: List[Dict]) -> List[Dict]:
        """去除重复视频"""
        seen_bvids = set()
        unique_videos = []
        
        for video in videos:
            bvid = video.get('bvid', '')
            if bvid and bvid not in seen_bvids:
                seen_bvids.add(bvid)
                unique_videos.append(video)
        
        return unique_videos
    
    def download_videos(self, videos: List[Dict], book_name: str, max_videos: int = 3) -> List[str]:
        """
        下载视频和字幕
        
        Args:
            videos: 视频信息列表
            book_name: 书籍名称
            max_videos: 最大下载数量
            
        Returns:
            下载成功的视频文件路径列表
        """
        if not videos:
            print("没有可下载的视频")
            return []
        
        # 创建下载目录
        download_dir = f"{book_name}/video"
        os.makedirs(download_dir, exist_ok=True)
        
        downloaded_files = []
        
        # 配置 yt-dlp
        ydl_opts = {
            'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
            'format': 'best[height<=720]',  # 限制分辨率以节省空间
            'writesubtitles': True,  # 下载字幕
            'writeautomaticsub': True,  # 下载自动生成的字幕
            'subtitleslangs': ['zh-CN', 'zh-Hans', 'zh'],  # 中文字幕
            'ignoreerrors': True,  # 忽略错误继续下载
        }
        
        print(f"开始下载前 {min(max_videos, len(videos))} 个视频...")
        
        for i, video in enumerate(videos[:max_videos]):
            try:
                print(f"正在下载第 {i+1} 个视频: {video['title']}")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video['url']])
                
                # 记录下载信息
                info_file = f"{download_dir}/video_{i+1}_info.json"
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(video, f, ensure_ascii=False, indent=2)
                
                downloaded_files.append(info_file)
                print(f"✅ 视频下载完成: {video['title']}")
                
                time.sleep(2)  # 下载间隔
                
            except Exception as e:
                print(f"❌ 下载视频失败: {video['title']}, 错误: {e}")
                continue
        
        print(f"下载完成，共成功下载 {len(downloaded_files)} 个视频")
        return downloaded_files
    
    def extract_subtitles_text(self, book_name: str) -> str:
        """
        提取所有视频的字幕文本
        
        Args:
            book_name: 书籍名称
            
        Returns:
            合并后的字幕文本
        """
        video_dir = f"{book_name}/video"
        if not os.path.exists(video_dir):
            return ""
        
        all_text = []
        
        # 查找所有字幕文件
        subtitle_files = []
        for file in os.listdir(video_dir):
            if file.endswith(('.vtt', '.srt', '.ass')):
                subtitle_files.append(os.path.join(video_dir, file))
        
        print(f"找到 {len(subtitle_files)} 个字幕文件")
        
        for subtitle_file in subtitle_files:
            try:
                text = self._extract_text_from_subtitle(subtitle_file)
                if text:
                    all_text.append(f"# 视频字幕: {os.path.basename(subtitle_file)}\n\n{text}\n\n")
            except Exception as e:
                print(f"提取字幕失败: {subtitle_file}, 错误: {e}")
        
        # 保存合并后的文本
        if all_text:
            output_file = f"{video_dir}/all_subtitles.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_text))
            print(f"字幕文本已保存到: {output_file}")
            return '\n'.join(all_text)
        
        return ""
    
    def _extract_text_from_subtitle(self, subtitle_file: str) -> str:
        """从字幕文件提取纯文本"""
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 处理不同的字幕格式
        if subtitle_file.endswith('.vtt'):
            return self._extract_from_vtt(content)
        elif subtitle_file.endswith('.srt'):
            return self._extract_from_srt(content)
        else:
            # 简单的文本提取
            lines = content.split('\n')
            text_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('WEBVTT', 'NOTE', '{')):
                    # 移除时间戳
                    if '-->' not in line and not line.isdigit():
                        text_lines.append(line)
            return '\n'.join(text_lines)
    
    def _extract_from_vtt(self, content: str) -> str:
        """从VTT格式提取文本"""
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('WEBVTT') and '-->' not in line and not line.startswith('NOTE'):
                # 移除HTML标签
                line = re.sub(r'<[^>]+>', '', line)
                if line:
                    text_lines.append(line)
        
        return '\n'.join(text_lines)
    
    def _extract_from_srt(self, content: str) -> str:
        """从SRT格式提取文本"""
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.isdigit() and '-->' not in line:
                text_lines.append(line)
        
        return '\n'.join(text_lines)
    
    def create_video_links_file(self, videos: List[Dict], book_name: str) -> str:
        """
        创建视频链接文件供传统爬虫使用
        
        Args:
            videos: 视频信息列表
            book_name: 书籍名称
            
        Returns:
            链接文件路径
        """
        links_file = f"{book_name}_video_links.txt"
        
        with open(links_file, 'w', encoding='utf-8') as f:
            f.write(f"# 《{book_name}》相关视频链接\n")
            f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for i, video in enumerate(videos, 1):
                f.write(f"# {i}. {video['title']}\n")
                f.write(f"# 作者: {video['author']}\n")
                f.write(f"# 时长: {video['duration']}秒\n")
                f.write(f"# 播放量: {video['play_count']}\n")
                f.write(f"{video['url']}\n\n")
        
        print(f"视频链接文件已创建: {links_file}")
        return links_file

def auto_process_book_videos(book_name: str, download_videos: bool = True, max_videos: int = 3) -> Dict:
    """
    自动处理书籍相关视频的完整流程
    
    Args:
        book_name: 书籍名称
        download_videos: 是否下载视频
        max_videos: 最大处理视频数量
        
    Returns:
        处理结果信息
    """
    crawler = BilibiliAutoCrawler()
    
    try:
        # 1. 搜索视频
        print("🔍 开始搜索相关视频...")
        videos = crawler.search_videos(book_name)
        
        if not videos:
            return {
                'success': False,
                'message': '未找到相关视频',
                'videos_found': 0
            }
        
        # 2. 创建链接文件
        print("📝 创建视频链接文件...")
        links_file = crawler.create_video_links_file(videos, book_name)
        
        result = {
            'success': True,
            'videos_found': len(videos),
            'links_file': links_file,
            'videos': videos
        }
        
        # 3. 下载视频（可选）
        if download_videos:
            print("⬇️ 开始下载视频...")
            downloaded_files = crawler.download_videos(videos, book_name, max_videos)
            result['downloaded_files'] = downloaded_files
            result['downloaded_count'] = len(downloaded_files)
            
            # 4. 提取字幕
            print("📄 提取字幕文本...")
            subtitle_text = crawler.extract_subtitles_text(book_name)
            result['subtitle_text'] = subtitle_text
            result['has_subtitles'] = bool(subtitle_text)
        
        print(f"✅ 视频处理完成！找到 {len(videos)} 个视频")
        return result
        
    except Exception as e:
        print(f"❌ 视频处理失败: {e}")
        return {
            'success': False,
            'message': str(e),
            'videos_found': 0
        }

if __name__ == "__main__":
    # 测试代码
    book_name = "三体"
    result = auto_process_book_videos(book_name, download_videos=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))