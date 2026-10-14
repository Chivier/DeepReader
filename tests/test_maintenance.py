"""Offline regressions for security and product maintenance."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests
from cairosvg import svg2png, svg2pdf
from streamlit.testing.v1 import AppTest

from reader import douban_crawler, douban_cleaning, report, llm, paths
from reader.main import PipelineThread, parse_bool, show_waiting_animation
from reader.video_crawler import VideoCrawler
from website.bookmarks import validate_svg

ROOT = Path(__file__).resolve().parents[1]
SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="600"><rect width="400" height="600" fill="#fff"/><text x="20" y="40">DeepReader</text></svg>'

@pytest.mark.parametrize('name', ['', ' ', '..', '../secret', 'a/b', 'a\\b', 'a\x00b', 'x'*121])
def test_book_names_cannot_escape_storage(name):
    with pytest.raises(ValueError):
        paths.validate_book_name(name)

def test_chinese_title_and_symlink_boundary(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, 'DATA_DIR', tmp_path)
    assert paths.book_directory(' 三体 ') == tmp_path / '三体'
    (tmp_path/'逃逸').symlink_to(tmp_path.parent, target_is_directory=True)
    with pytest.raises(ValueError):
        paths.book_directory('逃逸')

def test_crawler_skips_malformed_results_and_sets_timeout(monkeypatch):
    response = Mock(text='<h3>missing link</h3><h3><a href="https://www.douban.com/link2/?url=https%3A%2F%2Fbook.douban.com%2Fsubject%2F123%2F">book</a></h3><h3><a href="https://example.com/">other</a></h3>')
    get = Mock(return_value=response)
    monkeypatch.setattr(douban_crawler.requests, 'get', get)
    assert douban_crawler.DoubanBookSpider().search_book('三体') == ['https://book.douban.com/subject/123/']
    assert get.call_args.kwargs['timeout'] == 30
    response.raise_for_status.assert_called_once()

def test_crawler_failure_does_not_poison_retry(tmp_path, monkeypatch):
    spider = douban_crawler.DoubanBookSpider()
    monkeypatch.setattr(spider, 'search_book', lambda _: None)
    with pytest.raises(ValueError):
        spider.crawl_book('三体', output_dir=str(tmp_path))
    assert not (tmp_path/'website').exists()

def test_cleaner_only_processes_text_and_preserves_dots(tmp_path):
    (tmp_path/'book_info.json').write_text('{}')
    (tmp_path/'review.1.txt').write_text('原始书评', encoding='utf-8')
    douban_cleaning.clean_all_douban_files(tmp_path)
    assert (tmp_path/'review.1_cleaned.txt').read_text() == '原始书评'
    assert not (tmp_path/'book_info_cleaned.txt').exists()

@pytest.mark.parametrize('url,expected', [
    ('https://www.bilibili.com/video/BV1xx411c7mD/', 'bilibili_BV1xx411c7mD'),
    ('https://youtu.be/dQw4w9WgXcQ', 'ytb_dQw4w9WgXcQ'),
    ('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'ytb_dQw4w9WgXcQ'),
    ('https://www.youtube.com/watch', None),
    ('https://bilibili.com', None),
    ('https://bilibili.com.evil.example/video/BV123', None),
    ('https://youtu.be/../../secret', None),
    ('file:///video/BV123', None),
])
def test_video_id_handles_invalid_and_trailing_slash_urls(tmp_path, url, expected):
    assert VideoCrawler(tmp_path).get_video_id(url) == expected

def test_false_flag_and_worker_exception():
    assert parse_bool('false') is False
    assert parse_bool('true') is True
    with pytest.raises(argparse.ArgumentTypeError):
        parse_bool('maybe')
    def fail():
        raise RuntimeError('pipeline failed')
    thread = PipelineThread(target=fail)
    thread.start()
    thread.join()
    with pytest.raises(RuntimeError, match='pipeline failed'):
        show_waiting_animation(thread)

def test_llm_configuration_and_empty_response(monkeypatch):
    monkeypatch.setenv('DEEPREADER_MODEL_NAME', 'configured-model')
    completion = Mock(return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='分析结果'))]))
    client = Mock(chat=SimpleNamespace(completions=SimpleNamespace(create=completion)))
    monkeypatch.setattr(llm, 'OpenAI', Mock(return_value=client))
    assert llm.SimpleChatModel().chat('内容') == '分析结果'
    assert completion.call_args.kwargs['model'] == 'configured-model'
    completion.return_value.choices[0].message.content = None
    with pytest.raises(ValueError):
        llm.SimpleChatModel().chat('内容')

def test_report_written_where_ui_reads_it(tmp_path, monkeypatch):
    (tmp_path/'parsed_data.csv').write_text('story,feeling,evaluation,thinking\n情节,感受,评价,思考\n')
    monkeypatch.setattr(report, 'SimpleChatModel', lambda **_: SimpleNamespace(chat=lambda _: '生成报告'))
    assert report.report_parser(str(tmp_path)) == '生成报告'
    assert (tmp_path/'report.md').read_text() == '生成报告'

@pytest.mark.parametrize('fragment', [
    '<script>alert(1)</script>',
    '<image href="file:///etc/passwd"/>',
    '<use href="https://example.com/x.svg"/>',
    '<rect fill="url(file:///secret)"/>',
    '<rect onclick="alert(1)"/>',
    '<style>@import "https://example.com/x";</style>',
    '<foreignObject/>',
])
def test_bookmarks_reject_active_or_external_content(fragment):
    with pytest.raises(ValueError):
        validate_svg(SVG.replace('</svg>', fragment+'</svg>'))

def test_svg_exports_and_dimension_limits():
    svg = validate_svg(SVG)
    assert svg2png(bytestring=svg.encode()).startswith(b'\x89PNG')
    assert svg2pdf(bytestring=svg.encode()).startswith(b'%PDF')
    with pytest.raises(ValueError):
        validate_svg(SVG.replace('width="400"', 'width="999999"'))

def test_home_and_add_book_render_and_reject_bad_title():
    home = AppTest.from_file(str(ROOT/'website/Home.py')).run()
    assert not home.exception
    add = AppTest.from_file(str(ROOT/'website/pages/2_➕_添加新书.py')).run()
    assert not add.exception
    add.text_input[0].set_value('../unsafe')
    add.button[0].click().run()
    assert not add.exception
    assert add.error
    assert not add.session_state.generation_status['is_running']

def test_chat_and_bookmark_survive_download_rerun(tmp_path, monkeypatch):
    import runtime
    import openai
    monkeypatch.setattr(runtime, 'CHAT_HISTORY_DIR', tmp_path)
    monkeypatch.setattr(runtime, 'BOOKMARKS_DIR', tmp_path)
    monkeypatch.setenv('OPENAI_API_KEY', 'offline-test-key')
    contents = iter(['问题一\n问题二\n问题三', '模拟回答', '压缩内容', '压缩内容', '```svg\n'+SVG+'\n```'])
    completion = Mock(side_effect=lambda **_: SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=next(contents)))]))
    monkeypatch.setattr(openai, 'OpenAI', lambda **_: SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=completion))))
    chat = AppTest.from_file(str(ROOT/'website/pages/1_💬_聊天室.py'))
    chat.query_params['book'] = '三国演义'
    chat.run()
    assert not chat.exception
    chat.chat_input[0].set_value('我想聊聊人物').run()
    assert not chat.exception
    assert chat.session_state.messages[-1]['content'] == '模拟回答'
    assert len(list(tmp_path.glob('*.json'))) == 1
    session_id = chat.session_state.chat_session_id
    next(button for button in chat.button if '生成书签' in button.label).click().run()
    assert not chat.exception
    assert len(chat.get('download_button')) == 3
    assert chat.session_state.chat_session_id == session_id
    chat.run()
    assert not chat.exception
    assert len(chat.get('download_button')) == 3
    assert len(list(tmp_path.glob('*.svg'))) == 1

@pytest.mark.parametrize('has_reviews', [True, False])
def test_add_book_pipeline_success_and_failure(tmp_path, monkeypatch, has_reviews):
    import runtime
    from reader import parse_review
    monkeypatch.setattr(paths, 'DATA_DIR', tmp_path/'data')
    monkeypatch.setattr(runtime, 'BOOK_PROMPT_DIR', tmp_path/'prompts')
    monkeypatch.setattr(douban_crawler.DoubanBookSpider, 'get_book_info', lambda *_: {'title': '离线测试书'})
    monkeypatch.setattr(douban_crawler.DoubanBookSpider, 'get_review_urls', lambda *_args, **_kwargs: ['https://book.douban.com/review/123/'] if has_reviews else [])
    monkeypatch.setattr(douban_crawler.DoubanBookSpider, 'get_reviews', lambda *_: [['https://book.douban.com/review/123/', '原始书评内容']])
    monkeypatch.setattr(parse_review.model, 'chat', lambda _: '解析内容')
    monkeypatch.setattr(report, 'SimpleChatModel', lambda **_: SimpleNamespace(chat=lambda _: '完整报告'))
    monkeypatch.setattr(douban_crawler.time, 'sleep', lambda _: None)
    script = f'''
import runpy, queue, streamlit as st
ns = runpy.run_path({str(ROOT/'website/pages/2_➕_添加新书.py')!r})
q = queue.Queue()
ns['generate_book_prompt_sync']('离线测试书', False, q, 'https://book.douban.com/subject/123/', True)
events = []
while not q.empty():
    events.append(q.get())
st.session_state.test_events = events
'''
    app = AppTest.from_string(script).run(timeout=10)
    assert not app.exception
    events = app.session_state.test_events
    guide = tmp_path/'prompts'/'离线测试书.md'
    if has_reviews:
        assert events[-1]['type'] == 'success'
        assert '完整报告' in guide.read_text()
        parsed = json.loads((tmp_path/'data'/'离线测试书'/'parsed_data.json').read_text())
        assert parsed[0][1] == 'https://book.douban.com/review/123/'
    else:
        assert events[-1]['type'] == 'error'
        assert not guide.exists()
        assert (tmp_path/'data'/'离线测试书'/'website'/'book_info.json').exists()
