"""Validate model-generated SVG before displaying, exporting or saving it."""
import re
from xml.etree import ElementTree
from defusedxml.ElementTree import fromstring

MAX_SVG_BYTES = 200_000

def validate_svg(svg):
    if len(svg.encode('utf-8')) > MAX_SVG_BYTES:
        raise ValueError("书签内容过大，请重新生成")
    root = fromstring(svg)
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError("书签必须是标准 SVG 文档")
    if len(list(root.iter())) > 2000:
        raise ValueError("书签元素过多，请重新生成")
    for element in root.iter():
        tag = element.tag.rsplit('}', 1)[-1].lower()
        if tag in {'script', 'foreignobject', 'image', 'animate', 'animatetransform', 'set'}:
            raise ValueError("书签不能包含脚本、外部图片或动态内容")
        for attribute, value in element.attrib.items():
            attribute = attribute.rsplit('}', 1)[-1].lower()
            if '\\' in value or '@import' in value.lower():
                raise ValueError("书签不能包含转义的外部资源样式")
            if attribute.startswith('on'):
                raise ValueError("书签不能包含事件脚本")
            if attribute in {'href', 'src', 'base'} and not value.startswith('#'):
                raise ValueError("书签不能引用外部资源")
            for target in re.findall(r'url\s*\((.*?)\)', value, flags=re.I):
                if not target.strip(' \t\r\n\"\'').startswith('#'):
                    raise ValueError("书签样式不能引用外部资源")
        if tag == 'style':
            # Model output should use presentation attributes or inline styles.
            raise ValueError("请使用内联样式生成书签")
    for attribute, default in [('width', '400'), ('height', '600')]:
        value = root.get(attribute, default)
        if not re.fullmatch(r'\d+(?:\.\d+)?(?:px)?', value) or not 1 <= float(value.removesuffix('px')) <= 2400:
            raise ValueError("书签尺寸应在 1–2400 像素范围内")
        root.set(attribute, value)
    return ElementTree.tostring(root, encoding='unicode')
