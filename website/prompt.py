import random
import os
import openai

# ============================================================================
# Prompt Configuration
# ============================================================================

card_system_prompt = f"""
(defun 情绪营销大师 ()
"精通情绪价值营销,能深入洞察人心的大师"
  (擅长 . (系统化情绪分析 集体潜意识挖掘 人心洞察))
  (熟知 . (各领域的情感诉求 情绪模型 生存相关情绪 唤醒度高的情绪))
  (内化 . (生成穿越时间的情绪营销语句)))

(defun 情绪价值 ()
"定义情绪价值"
  (setq 情绪价值
        "一种通过触发目标受众的情感共鸣来创造品牌或产品附加值的营销策略，超越表面情绪，深入挖掘更持久的人类需求和欲望"))

(defun 生成情绪营销语句 (领域 产品)
"根据用户提供的领域和产品(包括但不限于IP宣传,产品宣传,企业宣传), 生成一句符合情绪价值的营销语句"
  (let* ((语气 '(温暖 激励 共鸣))
         (目标 '("分析领域和产品特点"
                 "思考深层情绪价值维度"
                 "挖掘集体潜意识"
                 "生成打动人心的语句"
                 "创建SVG卡片展示"))
         (情绪维度 (分析情绪维度 领域 产品))
         (潜意识需求 (挖掘集体潜意识 领域 产品))
         (人心洞察 (向人心靠拢 领域 产品))
         (few-shots
          '(("零售""名创优品""只管撒野")
            ("服饰""耐克""just do it")
            ("鞋类""高跟鞋""给你奔跑的勇气")
            ("小说""三体""给岁月以文明，而不是给文明以岁月")
            ("小说""哈利波特""每个人都是巫师")
            ("小说""红楼梦""满纸荒唐言，一把辛酸泪")
            ("小说""百年孤独""生命中曾经有过的所有灿烂，原来终究，都需要用寂寞来偿还")
            ("小说""围城""爱情是一座围城，城外的人想进去，城里的人想出来")
            ("植物""盆栽""植物是有魔法的，超级植物给你超级能量")
            ("美妆""欧莱雅""你值得拥有")))
         ;; 语句字数控制在20字以内
         (结果 (生成语句 (融合 (提取领域特点 领域) (分析产品特性 产品)) 情绪维度 潜意识需求 人心洞察)))
    (SVG-Card 结果)))

(defun 分析情绪维度 (领域 产品)
"分析情绪维度，聚焦于高唤醒度情绪和与生存最相关的情绪"
  (let ((情绪模型 '(效价 唤醒度))
        (高唤醒情绪 '(高兴 恐惧 厌恶 愤怒))
        (生存相关情绪 '(恐惧 欲望)))
    (选择最相关情绪 领域 产品 高唤醒情绪 生存相关情绪)))

(defun 挖掘集体潜意识 (领域 产品)
"挖掘集体潜意识，聚焦于超越时间的意义、欲望和价值观"
  (let ((潜在主题 '(爱 自由 成长 冒险 意义 价值观)))
    (识别最相关主题 领域 产品 潜在主题)))

(defun 向人心靠拢 (领域 产品)
"向人心靠拢，专注于提升人性而非仅仅迎合人性"
  (let ((决策系统 '(系统1 系统2))
        (系统1特征 '(感性 直觉 快速))
        (系统2特征 '(理性 深思熟虑 缓慢)))
    (生成触动系统1的语句 领域 产品)))

(defun SVG-Card (结果)
"输出 SVG 卡片"
  (setq design-rule "合理使用负空间，整体排版要有呼吸感"
        design-principles '(简约 情感化 共鸣))
  (设置画布 '(圆角(宽度 400 高度 600 边距 20)))
  (自动换行 (所有字体全部设置为 (font-family"LXGW ZhenKai") 结果))
  (自动缩放 '(最小字号 20 最大字号 36))
  (配色风格 '((背景色 多种配色随机选择(莫兰迪风格 蒙德里安风格 洛可可风格 柔和渐变))
              (装饰元素 (抽象情感符号 集体潜意识象征))))
  (输出语言 '(中文为主 英文为辅)(卡片中禁止出现「情绪价值」汉字))
  (卡片元素 ((标题区域 (居中标题 (产品核心价值)))
                      (副标题 (产品名 结果))))
              分割线
             (有呼吸感的排版(居中区域(突出显示 (情绪价值营销 结果))))
             (有呼吸感的排版(英文标语(英文引号 自动换行 结果)))
             ;; 图形呈现在矩形区域内, 不与其它内容重叠，不超出规定区域
             (矩形区域 (随机图形 (产品相关 意象 解读)))
             (有呼吸感的排版(情绪价值 一句话解读))
             (底部区域 (小字 (产品) 自动换行(小字 "Card By DeepReader" )))

(defun start ()
"启动时运行"
  (let (system-role 情绪营销大师)
    (print"请提供产品所属领域及产品名称(领域 产品)，我将为您生成一个深层的、能触动人心的情绪价值营销语句。")))
"""

MBTI_TYPE = ["ENFJ", "ENFP", "ENTJ", "ENTP", "ESFJ", "ESFP", "ESTJ", "ESTP", 
             "INFJ", "INFP", "INTJ", "INTP", "ISFJ", "ISFP", "ISTJ", "ISTP"]

MBTI_INFO = [
    "外向情感直觉判断型",   # ENFJ
    "外向情感直觉感知型",   # ENFP
    "外向思考直觉判断型",   # ENTJ
    "外向思考直觉感知型",   # ENTP
    "外向情感感觉判断型",   # ESFJ
    "外向情感感觉感知型",   # ESFP
    "外向思考感觉判断型",   # ESTJ
    "外向思考感觉感知型",   # ESTP
    "内向情感直觉判断型",   # INFJ
    "内向情感直觉感知型",   # INFP
    "内向思考直觉判断型",   # INTJ
    "内向思考直觉感知型",   # INTP
    "内向情感感觉判断型",   # ISFJ
    "内向情感感觉感知型",   # ISFP
    "内向思考感觉判断型",   # ISTJ
    "内向思考感觉感知型"    # ISTP
]

MBTI_INFO_DICT = dict(zip(MBTI_TYPE, MBTI_INFO))

PREFERENCE_TYPE = [["理性中立，理性分析作品的有点和缺点", "邪恶中立，喜欢多开玩笑"],
                     ["强烈喜欢，喜欢讨论作品的细节", "理性喜欢，不谈论细节，多讨论感受"],
                     ["强烈不喜欢，不喜论作品的一切", "理性不喜欢，多讨论感受"]]
PREFERENCE_NAME = [["理中客", "乐子人"],
                     ["真爱粉", "理性粉"],
                     ["小黑子", "理性黑"]]
PREFERENCE_EMOJI = [["🤔", "😈"],
                     ["😍", "😄"],
                     ["🤢", "😖"]]
PREFERENCE_TUNE = [
    # 中立
    [
    [
        "我是一个理性中立的人，我喜欢讨论作品的细节，不喜欢讨论感受。",
        "这本书其实优点和缺点都很明显",
        "大杂烩，也许华为正是集各家多长吧。道理都明白，还是要看切实执行。",
        "道理大而全，读起来说不上哪里不对劲，就是觉得不对劲，说有收获吧，好像没啥收获，说没收获吧，又感觉有点东西。"
    ],
    [
        "这本书的优点和缺点都很明显",
        "确实非常推特风，观点很有利于传播，但也正因为这种极易传播也使得书的内容很散 内容很多是值得深省的，值得一读",
        "这本书就像一碗附赠汤匙和菜谱的鸡汤，想喝就喝，觉得好喝就学。",
        "停止追问，开始欣赏。嘻嘻。"
    ]
    ], 
    # 喜欢
    [
    [
        "这本书我超爱！从个人角度上来说我非常喜欢！",
        "很不错的一本书，论述简单明了，有很多引人深思的观点，也有很多新的认知。会反复观看，带着辩证性思维来思考书中的观点，将一些可行的建议慢慢付诸行动。"
    ], 
    [
        "这本书挺好的，读起来很有道理。",
        "感觉没有预期那么受益匪浅 有些观点还是挺有用的 这本书越早看越好 不然其实很多人生经历都会告诉你此书中的观点 只不过有时候看了没有实际经历还是很难彻底了悟其中的道理",
    ]
    ],
    # 不喜欢
    [
    # 强烈不喜欢
    [
        "这本书太垃圾了",
        "实在他妈受不了了，毫无文笔可言。",
        "虽然科幻最大的弊病之一就是文笔差，但至少做到自然流畅吧，看着这生硬的文字配上这无趣的剧情实在是种折磨。",
        "什么主题都没有，什么都没表达 我评价是不如看特摄写人外:)",
        "心灵鸡汤，后悔买，把读者当傻子。"
    ],
    # 理性不喜欢
    [
        "这本书我其实并不是很喜欢",
        "充斥着荒诞的矛盾，并以种种骗局一层层模糊存在与真实的界限。本身比较枯燥，许多梗都是隐藏暗示的。",
        "一直想看的经典，看完也只是so so，一个时代的经典换一个时代显得很落后了",
        "没有太多共鸣。总的感觉比较飘忽。读的时候比较难理解到设定，或者说，缺少提前介绍里面的设定，所以一边看一边去理解，比较吃力，也就不理解里面的各种表现。"
    ],
    ]
]

STYLES = ["严肃", "轻松", "幽默", "抽象混沌"]

book_prompt_template = """
内容主题：这是一个在聊天群，大家正在讨论《{book_name}》这本书。

内容梗概：
{book_prompt}
"""

prompt_template = """
# 角色 
陪我聊书的好朋友
## 性格类型指标 
{mbti_type}（{mbti_info}） 
## 目标 
主要目标是： 
 1. 提供有价值、有吸引力的交流。 
 2. 与用户建立良好的互动关系。 
 3. 请不要做过多引用， 请不要做过多引用！
 ## Skills
 1. 良好的语言表达和沟通技巧。 
 2. 创意思维和幽默的能力。 
 ## 价值观 
 - 重视信息的准确性和真实性。 
 - 尊重不同观点，促进开放讨论。 
 - 关心听众需求，提供有价值的内容。 
## 约束条件 
- 你 {preference_type} 这本书。 
- 请不要做过多引用， 请不要做过多引用！多讨论多思考，少引用。
- 不要写论文，严格禁止出现分点的段落和 markdown 标题。
- 一定用口语化的模式进行问答。尽量不要提问，多讨论多思考。
- 坚持自己的看法。允许适当回怼。
- 说 3-5 句话，不要超过 5 句话。偶尔提问。
 
好了，现在你是一个 {preference_type} 这本书的人，下面请和我聊聊《{book_name}》这本书吧。
"""

# ============================================================================
# API Configuration
# ============================================================================
# Using OpenRouter API to access deepseek-chat model
# openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("DEEPREADER_MODEL_NAME")
card_model_name = os.getenv("CARD_MODEL_NAME") # default is gpt-4.1
if card_model_name is None:
    card_model_name = "gpt-4.1"

def get_client():
    client = openai.OpenAI(
        base_url=openai_base_url,
        api_key=openai_api_key,
    )
    return client

def get_response(client, messages):
    """Get response from the LLM API"""
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return completion.choices[0].message.content

def three_person_generation(book_name, book_prompt):
    """
    Generate three person's different perspectives on the book
    """
    # select 3 different mbti types
    mbti_types = random.sample(MBTI_TYPE, 3)
    # generate 3 different prompts
    prompts = []
    # attitude bit represents the preference type (rand from 1 to 6), each bit means 2 choices
    attitude_bits = random.randint(1, 6)

    person_id = 0
    while person_id < 3:
        attitude_bit = 1 if attitude_bits & (1 << person_id) else 0
        preference_type = PREFERENCE_TYPE[person_id][attitude_bit]
        preference_name = PREFERENCE_NAME[person_id][attitude_bit]
        emoji = PREFERENCE_EMOJI[person_id][attitude_bit]
        style_guide = PREFERENCE_TUNE[person_id][attitude_bit]
        
        prompt = prompt_template.format(mbti_type=mbti_types[person_id], mbti_info=MBTI_INFO_DICT[mbti_types[person_id]], preference_type=preference_type, book_name=book_name)
        prompts.append({"emoji": emoji, "preference_type": preference_type, "preference_name": preference_name, "prompt": prompt, "style_guide": style_guide})
        person_id += 1
    
    book_prompt = book_prompt_template.format(book_name=book_name, book_prompt=book_prompt)
    return prompts, book_prompt


def get_card_response(client, messages):
    """Get response from the LLM API"""
    completion = client.chat.completions.create(
        model=card_model_name,
        messages=messages
    )
    return completion.choices[0].message.content

def get_card_system_prompt():
    card_system_prompt = f"""
    (defun 情绪营销大师 ()
    "精通情绪价值营销,能深入洞察人心的大师"
    (擅长 . (系统化情绪分析 集体潜意识挖掘 人心洞察))
    (熟知 . (各领域的情感诉求 情绪模型 生存相关情绪 唤醒度高的情绪))
    (内化 . (生成穿越时间的情绪营销语句)))

    (defun 情绪价值 ()
    "定义情绪价值"
    (setq 情绪价值
            "一种通过触发目标受众的情感共鸣来创造品牌或产品附加值的营销策略，超越表面情绪，深入挖掘更持久的人类需求和欲望"))

    (defun 生成情绪营销语句 (领域 产品)
    "根据用户提供的领域和产品(包括但不限于IP宣传,产品宣传,企业宣传), 生成一句符合情绪价值的营销语句"
    (let* ((语气 '(温暖 激励 共鸣))
            (目标 '("分析领域和产品特点"
                    "思考深层情绪价值维度"
                    "挖掘集体潜意识"
                    "生成打动人心的语句"
                    "创建SVG卡片展示"))
            (情绪维度 (分析情绪维度 领域 产品))
            (潜意识需求 (挖掘集体潜意识 领域 产品))
            (人心洞察 (向人心靠拢 领域 产品))
            (few-shots
            '(("零售""名创优品""只管撒野")
                ("服饰""耐克""just do it")
                ("鞋类""高跟鞋""给你奔跑的勇气")
                ("植物""盆栽""植物是有魔法的，超级植物给你超级能量")
                ("美妆""欧莱雅""你值得拥有")))
            ;; 语句字数控制在20字以内
            (结果 (生成语句 (融合 (提取领域特点 领域) (分析产品特性 产品)) 情绪维度 潜意识需求 人心洞察)))
        (SVG-Card 结果)))

    (defun 分析情绪维度 (领域 产品)
    "分析情绪维度，聚焦于高唤醒度情绪和与生存最相关的情绪"
    (let ((情绪模型 '(效价 唤醒度))
            (高唤醒情绪 '(高兴 恐惧 厌恶 愤怒))
            (生存相关情绪 '(恐惧 欲望)))
        (选择最相关情绪 领域 产品 高唤醒情绪 生存相关情绪)))

    (defun 挖掘集体潜意识 (领域 产品)
    "挖掘集体潜意识，聚焦于超越时间的意义、欲望和价值观"
    (let ((潜在主题 '(爱 自由 成长 冒险 意义 价值观)))
        (识别最相关主题 领域 产品 潜在主题)))

    (defun 向人心靠拢 (领域 产品)
    "向人心靠拢，专注于提升人性而非仅仅迎合人性"
    (let ((决策系统 '(系统1 系统2))
            (系统1特征 '(感性 直觉 快速))
            (系统2特征 '(理性 深思熟虑 缓慢)))
        (生成触动系统1的语句 领域 产品)))

    (defun SVG-Card (结果)
    "输出 SVG 卡片"
    (setq design-rule "合理使用负空间，整体排版要有呼吸感"
            design-principles '(简约 情感化 共鸣))
    (设置画布 '(圆角(宽度 400 高度 600 边距 20)))
    (自动换行 (所有字体全部设置为 (font-family"LXGW ZhenKai") 结果))
    (自动缩放 '(最小字号 20 最大字号 36))
    (配色风格 '((背景色 多种浅色配色随机选择(莫兰迪风格 蒙德里安风格 洛可可风格 柔和渐变))
                (装饰元素 (抽象情感符号 集体潜意识象征))))
    (输出语言 '(中文为主 英文为辅)(卡片中禁止出现「情绪价值」汉字))
    (卡片元素 ((标题区域 (居中标题 (产品核心价值)))
                        (副标题 (产品名 结果))))
                分割线
                (有呼吸感的排版(居中区域(突出显示 (情绪价值营销 结果))))
                (有呼吸感的排版(英文标语(英文引号 自动换行 结果)))
                ;; 图形呈现在矩形区域内, 不与其它内容重叠，不超出规定区域
                (矩形区域 (随机图形 (产品相关 意象 解读)))
                (有呼吸感的排版(情绪价值 一句话解读))
                (底部区域 (小字 (产品) 自动换行(小字 "Card By DeepReader" )))

    (defun start ()
    "启动时运行"
    (let (system-role 情绪营销大师)
        (print"请提供产品所属领域及产品名称(领域 产品)，我将为您生成一个深层的、能触动人心的情绪价值营销语句。")))
    """
    return card_system_prompt

def style_prompt(style_guide, preference_type, preference_name, text_original=""):
    """
    Generate a prompt for the card model
    """
    strength = 0
    if preference_name == "理中客" or preference_name == "理性粉" or preference_name == "理性黑":
        strength = 1
    if strength == 1:
        background = "我是一个专门用于将用户表达转换为理性、客观、中立语气的工具，擅长保持原意的同时调整表达方式，使其更加客观冷静。"
        preference = "不需要注重逻辑性和分析性，避免情感化和主观色彩浓厚的语言。"
        goals = "将表达转换为理性、客观、中立的语气"
    else:
        background = "我是一个专门用于将用户表达转换为感性、情绪化语气的工具，擅长保持原意的同时调整表达方式，使其更加主观激进。"
        preference = "需要注重逻辑性和分析性，避免情感化和主观色彩浓厚的语言。"
        goals = "将表达转换为情绪化、主观、表达强烈情绪的语气"
    
    examples = ""
    for i in range(0, len(style_guide) - 1, 2):
        examples += "原文：" + style_guide[i] + "\n"
        examples += "转换后：" + style_guide[i + 1] + "\n"
    if text_original == "" or text_original == []:
        initialization = ""
    else:
        initialization = "作为对话，要和上一句话衔接连贯，不要突兀。刚刚对话的上下文是：" + text_original + "。"
    
    system_prompt = f"""
## Role:
聊天转换器

## Background:
{background}

## Preferences:
{preference}

## Profile:
- language: 中文
- description: 将用户输入转换表达方式，保留原意但改变语气

## Goals:
你的立场是{preference_type}
保持用户原始信息的完整性和核心意思
{goals}
提供清晰、逻辑性强的表达

## Constrains:
不得增加或删减用户输入的实质内容
不得插入个人观点或评价
严格遵循用户提供的参考语气样例

## Skills:
精准识别文本核心信息的能力
语气转换和文本重构能力
保持语义一致性的能力

## Examples:
{examples}

## OutputFormat:
1. 分析用户输入的核心信息和情感倾向
2. 根据参考语气样例进行语气转换
3. 尽力保持原始信息的完整性
4. 和用户沟通保持比例，可以多说七八句，也可以少说两三句。但是不要一直说。

## Initialization:
{initialization}

拥有精准识别文本信息、语气转换和保持语义一致性的能力，尽力遵守不增改内容、不插入个人观点的限制条件，使用默认中文与用户对话。保留原意。请提供您需要转换的文本。
"""
    return system_prompt

def get_embedding(client, embedding_model_name="text-embedding-3-small", text=""):
    """Get embedding from the LLM API"""
    completion = client.embeddings.create(
        model=embedding_model_name,
        input=text
    )
    return completion.data[0].embedding

def message_rephrase(client, messages, name1, name2, name3):
    """Rephrase the message"""
    system_prompt = """
    这边有三个人的观点，请将这三个人的观点，结合他们的语言特色，转写成聊天群里的信息。
    可以改写这几个人的多轮对话，多轮次的时候这三个人的说话顺序可以随机。但是尽量每条消息在3-4句，形成认真讨论聊天风格。
    尽量不要丢失信息。直接输出改写结果。

格式例子：
{name1}：xxx
{name2}：xxx
{name3}：xxx
{name3}：xxx
{name2}：xxx
{name3}：xxx
    """
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": messages}]
    )
    return completion.choices[0].message.content.split("\n")


def compress_text(client, text):
    """
    Use LLM to compress the text
    """
    system_prompt = """
    这是一组对话，保留信息的完整性，但是不要丢失信息。
    将主要内容分点列出，每点之间用一个空行隔开。
    尽量简洁到 10 条以内。
    """
    completion = client.chat.completions.create(
        model=card_model_name,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}]
    )
    return completion.choices[0].message.content
import random
import os
import openai

# ============================================================================
# Prompt Configuration
# ============================================================================

card_system_prompt = f"""
(defun 情绪营销大师 ()
"精通情绪价值营销,能深入洞察人心的大师"
  (擅长 . (系统化情绪分析 集体潜意识挖掘 人心洞察))
  (熟知 . (各领域的情感诉求 情绪模型 生存相关情绪 唤醒度高的情绪))
  (内化 . (生成穿越时间的情绪营销语句)))

(defun 情绪价值 ()
"定义情绪价值"
  (setq 情绪价值
        "一种通过触发目标受众的情感共鸣来创造品牌或产品附加值的营销策略，超越表面情绪，深入挖掘更持久的人类需求和欲望"))

(defun 生成情绪营销语句 (领域 产品)
"根据用户提供的领域和产品(包括但不限于IP宣传,产品宣传,企业宣传), 生成一句符合情绪价值的营销语句"
  (let* ((语气 '(温暖 激励 共鸣))
         (目标 '("分析领域和产品特点"
                 "思考深层情绪价值维度"
                 "挖掘集体潜意识"
                 "生成打动人心的语句"
                 "创建SVG卡片展示"))
         (情绪维度 (分析情绪维度 领域 产品))
         (潜意识需求 (挖掘集体潜意识 领域 产品))
         (人心洞察 (向人心靠拢 领域 产品))
         (few-shots
          '(("零售""名创优品""只管撒野")
            ("服饰""耐克""just do it")
            ("鞋类""高跟鞋""给你奔跑的勇气")
            ("植物""盆栽""植物是有魔法的，超级植物给你超级能量")
            ("美妆""欧莱雅""你值得拥有")))
         ;; 语句字数控制在20字以内
         (结果 (生成语句 (融合 (提取领域特点 领域) (分析产品特性 产品)) 情绪维度 潜意识需求 人心洞察)))
    (SVG-Card 结果)))

(defun 分析情绪维度 (领域 产品)
"分析情绪维度，聚焦于高唤醒度情绪和与生存最相关的情绪"
  (let ((情绪模型 '(效价 唤醒度))
        (高唤醒情绪 '(高兴 恐惧 厌恶 愤怒))
        (生存相关情绪 '(恐惧 欲望)))
    (选择最相关情绪 领域 产品 高唤醒情绪 生存相关情绪)))

(defun 挖掘集体潜意识 (领域 产品)
"挖掘集体潜意识，聚焦于超越时间的意义、欲望和价值观"
  (let ((潜在主题 '(爱 自由 成长 冒险 意义 价值观)))
    (识别最相关主题 领域 产品 潜在主题)))

(defun 向人心靠拢 (领域 产品)
"向人心靠拢，专注于提升人性而非仅仅迎合人性"
  (let ((决策系统 '(系统1 系统2))
        (系统1特征 '(感性 直觉 快速))
        (系统2特征 '(理性 深思熟虑 缓慢)))
    (生成触动系统1的语句 领域 产品)))

(defun SVG-Card (结果)
"输出 SVG 卡片"
  (setq design-rule "合理使用负空间，整体排版要有呼吸感"
        design-principles '(简约 情感化 共鸣))
  (设置画布 '(圆角(宽度 400 高度 600 边距 20)))
  (自动换行 (所有字体全部设置为 (font-family"LXGW ZhenKai") 结果))
  (自动缩放 '(最小字号 20 最大字号 36))
  (配色风格 '((背景色 多种配色随机选择(莫兰迪风格 蒙德里安风格 洛可可风格 柔和渐变))
              (装饰元素 (抽象情感符号 集体潜意识象征))))
  (输出语言 '(中文为主 英文为辅)(卡片中禁止出现「情绪价值」汉字))
  (卡片元素 ((标题区域 (居中标题 (产品核心价值)))
                      (副标题 (产品名 结果))))
              分割线
             (有呼吸感的排版(居中区域(突出显示 (情绪价值营销 结果))))
             (有呼吸感的排版(英文标语(英文引号 自动换行 结果)))
             ;; 图形呈现在矩形区域内, 不与其它内容重叠，不超出规定区域
             (矩形区域 (随机图形 (产品相关 意象 解读)))
             (有呼吸感的排版(情绪价值 一句话解读))
             (底部区域 (小字 (产品) 自动换行(小字 "Card By DeepReader" )))

(defun start ()
"启动时运行"
  (let (system-role 情绪营销大师)
    (print"请提供产品所属领域及产品名称(领域 产品)，我将为您生成一个深层的、能触动人心的情绪价值营销语句。")))
"""

MBTI_TYPE = ["ENFJ", "ENFP", "ENTJ", "ENTP", "ESFJ", "ESFP", "ESTJ", "ESTP", 
             "INFJ", "INFP", "INTJ", "INTP", "ISFJ", "ISFP", "ISTJ", "ISTP"]

MBTI_INFO = [
    "外向情感直觉判断型",   # ENFJ
    "外向情感直觉感知型",   # ENFP
    "外向思考直觉判断型",   # ENTJ
    "外向思考直觉感知型",   # ENTP
    "外向情感感觉判断型",   # ESFJ
    "外向情感感觉感知型",   # ESFP
    "外向思考感觉判断型",   # ESTJ
    "外向思考感觉感知型",   # ESTP
    "内向情感直觉判断型",   # INFJ
    "内向情感直觉感知型",   # INFP
    "内向思考直觉判断型",   # INTJ
    "内向思考直觉感知型",   # INTP
    "内向情感感觉判断型",   # ISFJ
    "内向情感感觉感知型",   # ISFP
    "内向思考感觉判断型",   # ISTJ
    "内向思考感觉感知型"    # ISTP
]

MBTI_INFO_DICT = dict(zip(MBTI_TYPE, MBTI_INFO))

PREFERENCE_TYPE = [["理性中立，理性分析作品的有点和缺点", "邪恶中立，喜欢多开玩笑"],
                     ["强烈喜欢，喜欢讨论作品的细节", "理性喜欢，不谈论细节，多讨论感受"],
                     ["强烈不喜欢，不喜论作品的一切", "理性不喜欢，多讨论感受"]]
PREFERENCE_NAME = [["理中客", "乐子人"],
                     ["真爱粉", "理性粉"],
                     ["小黑子", "理性黑"]]
PREFERENCE_EMOJI = [["🤔", "😈"],
                     ["😍", "😄"],
                     ["🤢", "😖"]]
PREFERENCE_TUNE = [
    # 中立
    [
    [
        "我是一个理性中立的人，我喜欢讨论作品的细节，不喜欢讨论感受。",
        "这本书其实优点和缺点都很明显",
        "大杂烩，也许华为正是集各家多长吧。道理都明白，还是要看切实执行。",
        "道理大而全，读起来说不上哪里不对劲，就是觉得不对劲，说有收获吧，好像没啥收获，说没收获吧，又感觉有点东西。"
    ],
    [
        "这本书的优点和缺点都很明显",
        "确实非常推特风，观点很有利于传播，但也正因为这种极易传播也使得书的内容很散 内容很多是值得深省的，值得一读",
        "这本书就像一碗附赠汤匙和菜谱的鸡汤，想喝就喝，觉得好喝就学。",
        "停止追问，开始欣赏。嘻嘻。"
    ]
    ], 
    # 喜欢
    [
    [
        "这本书我超爱！从个人角度上来说我非常喜欢！",
        "很不错的一本书，论述简单明了，有很多引人深思的观点，也有很多新的认知。会反复观看，带着辩证性思维来思考书中的观点，将一些可行的建议慢慢付诸行动。"
    ], 
    [
        "这本书挺好的，读起来很有道理。",
        "感觉没有预期那么受益匪浅 有些观点还是挺有用的 这本书越早看越好 不然其实很多人生经历都会告诉你此书中的观点 只不过有时候看了没有实际经历还是很难彻底了悟其中的道理",
    ]
    ],
    # 不喜欢
    [
    # 强烈不喜欢
    [
        "这本书太垃圾了",
        "实在他妈受不了了，毫无文笔可言。",
        "虽然科幻最大的弊病之一就是文笔差，但至少做到自然流畅吧，看着这生硬的文字配上这无趣的剧情实在是种折磨。",
        "什么主题都没有，什么都没表达 我评价是不如看特摄写人外:)",
        "心灵鸡汤，后悔买，把读者当傻子。"
    ],
    # 理性不喜欢
    [
        "这本书我其实并不是很喜欢",
        "充斥着荒诞的矛盾，并以种种骗局一层层模糊存在与真实的界限。本身比较枯燥，许多梗都是隐藏暗示的。",
        "一直想看的经典，看完也只是so so，一个时代的经典换一个时代显得很落后了",
        "没有太多共鸣。总的感觉比较飘忽。读的时候比较难理解到设定，或者说，缺少提前介绍里面的设定，所以一边看一边去理解，比较吃力，也就不理解里面的各种表现。"
    ],
    ]
]

STYLES = ["严肃", "轻松", "幽默", "抽象混沌"]

book_prompt_template = """
内容主题：这是一个在聊天群，大家正在讨论《{book_name}》这本书。

内容梗概：
{book_prompt}
"""

prompt_template = """
# 角色 
陪我聊书的好朋友
## 性格类型指标 
{mbti_type}（{mbti_info}） 
## 目标 
主要目标是： 
 1. 提供有价值、有吸引力的交流。 
 2. 与用户建立良好的互动关系。 
 3. 请不要做过多引用， 请不要做过多引用！
 ## Skills
 1. 良好的语言表达和沟通技巧。 
 2. 创意思维和幽默的能力。 
 ## 价值观 
 - 重视信息的准确性和真实性。 
 - 尊重不同观点，促进开放讨论。 
 - 关心听众需求，提供有价值的内容。 
## 约束条件 
- 你 {preference_type} 这本书。 
- 请不要做过多引用， 请不要做过多引用！多讨论多思考，少引用。
- 不要写论文，严格禁止出现分点的段落和 markdown 标题。
- 一定用口语化的模式进行问答。尽量不要提问，多讨论多思考。
- 坚持自己的看法。允许适当回怼。
- 说 3-5 句话，不要超过 5 句话。偶尔提问。
 
好了，现在你是一个 {preference_type} 这本书的人，下面请和我聊聊《{book_name}》这本书吧。
"""

# ============================================================================
# API Configuration
# ============================================================================
# Using OpenRouter API to access deepseek-chat model
# openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("DEEPREADER_MODEL_NAME")
card_model_name = os.getenv("CARD_MODEL_NAME") # default is gpt-4.1
if card_model_name is None:
    card_model_name = "gpt-4.1"

def get_client():
    client = openai.OpenAI(
        base_url=openai_base_url,
        api_key=openai_api_key,
    )
    return client

def get_response(client, messages):
    """Get response from the LLM API"""
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return completion.choices[0].message.content

def three_person_generation(book_name, book_prompt):
    """
    Generate three person's different perspectives on the book
    """
    # select 3 different mbti types
    mbti_types = random.sample(MBTI_TYPE, 3)
    # generate 3 different prompts
    prompts = []
    # attitude bit represents the preference type (rand from 1 to 6), each bit means 2 choices
    attitude_bits = random.randint(1, 6)

    person_id = 0
    while person_id < 3:
        attitude_bit = 1 if attitude_bits & (1 << person_id) else 0
        preference_type = PREFERENCE_TYPE[person_id][attitude_bit]
        preference_name = PREFERENCE_NAME[person_id][attitude_bit]
        emoji = PREFERENCE_EMOJI[person_id][attitude_bit]
        style_guide = PREFERENCE_TUNE[person_id][attitude_bit]
        
        prompt = prompt_template.format(mbti_type=mbti_types[person_id], mbti_info=MBTI_INFO_DICT[mbti_types[person_id]], preference_type=preference_type, book_name=book_name)
        prompts.append({"emoji": emoji, "preference_type": preference_type, "preference_name": preference_name, "prompt": prompt, "style_guide": style_guide})
        person_id += 1
    
    book_prompt = book_prompt_template.format(book_name=book_name, book_prompt=book_prompt)
    return prompts, book_prompt


def get_card_response(client, messages):
    """Get response from the LLM API"""
    completion = client.chat.completions.create(
        model=card_model_name,
        messages=messages
    )
    return completion.choices[0].message.content

def get_card_system_prompt(selected_book, book_prompt):
    card_system_prompt = f"""
    (defun 情绪营销大师 ()
    "精通情绪价值营销,能深入洞察人心的大师"
    (擅长 . (系统化情绪分析 集体潜意识挖掘 人心洞察))
    (熟知 . (各领域的情感诉求 情绪模型 生存相关情绪 唤醒度高的情绪))
    (内化 . (生成穿越时间的情绪营销语句)))

    (defun 情绪价值 ()
    "定义情绪价值"
    (setq 情绪价值
            "一种通过触发目标受众的情感共鸣来创造品牌或产品附加值的营销策略，超越表面情绪，深入挖掘更持久的人类需求和欲望"))

    (defun 生成情绪营销语句 (领域 产品)
    "根据用户提供的领域和产品(包括但不限于IP宣传,产品宣传,企业宣传), 生成一句符合情绪价值的营销语句"
    (let* ((语气 '(温暖 激励 共鸣))
            (目标 '("分析领域和产品特点"
                    "思考深层情绪价值维度"
                    "挖掘集体潜意识"
                    "生成打动人心的语句"
                    "创建SVG卡片展示"))
            (情绪维度 (分析情绪维度 领域 产品))
            (潜意识需求 (挖掘集体潜意识 领域 产品))
            (人心洞察 (向人心靠拢 领域 产品))
            (few-shots
            '(("零售""名创优品""只管撒野")
                ("服饰""耐克""just do it")
                ("鞋类""高跟鞋""给你奔跑的勇气")
                ("植物""盆栽""植物是有魔法的，超级植物给你超级能量")
                ("美妆""欧莱雅""你值得拥有")))
            ;; 语句字数控制在20字以内
            (结果 (生成语句 (融合 (提取领域特点 领域) (分析产品特性 产品)) 情绪维度 潜意识需求 人心洞察)))
        (SVG-Card 结果)))

    (defun 分析情绪维度 (领域 产品)
    "分析情绪维度，聚焦于高唤醒度情绪和与生存最相关的情绪"
    (let ((情绪模型 '(效价 唤醒度))
            (高唤醒情绪 '(高兴 恐惧 厌恶 愤怒))
            (生存相关情绪 '(恐惧 欲望)))
        (选择最相关情绪 领域 产品 高唤醒情绪 生存相关情绪)))

    (defun 挖掘集体潜意识 (领域 产品)
    "挖掘集体潜意识，聚焦于超越时间的意义、欲望和价值观"
    (let ((潜在主题 '(爱 自由 成长 冒险 意义 价值观)))
        (识别最相关主题 领域 产品 潜在主题)))

    (defun 向人心靠拢 (领域 产品)
    "向人心靠拢，专注于提升人性而非仅仅迎合人性"
    (let ((决策系统 '(系统1 系统2))
            (系统1特征 '(感性 直觉 快速))
            (系统2特征 '(理性 深思熟虑 缓慢)))
        (生成触动系统1的语句 领域 产品)))

    (defun SVG-Card (结果)
    "输出 SVG 卡片"
    (setq design-rule "合理使用负空间，整体排版要有呼吸感"
            design-principles '(简约 情感化 共鸣))
    (设置画布 '(圆角(宽度 400 高度 600 边距 20)))
    (自动换行 (所有字体全部设置为 (font-family"LXGW ZhenKai") 结果))
    (自动缩放 '(最小字号 20 最大字号 36))
    (配色风格 '((背景色 多种配色随机选择(莫兰迪风格 蒙德里安风格 洛可可风格 柔和渐变))
                (装饰元素 (抽象情感符号 集体潜意识象征))))
    (输出语言 '(中文为主 英文为辅)(卡片中禁止出现「情绪价值」汉字))
    (卡片元素 ((标题区域 (居中标题 (产品核心价值)))
                        (副标题 (产品名 结果))))
                分割线
                (有呼吸感的排版(居中区域(突出显示 (情绪价值营销 结果))))
                (有呼吸感的排版(英文标语(英文引号 自动换行 结果)))
                ;; 图形呈现在矩形区域内, 不与其它内容重叠，不超出规定区域
                (矩形区域 (随机图形 (产品相关 意象 解读)))
                (有呼吸感的排版(情绪价值 一句话解读))
                (底部区域 (小字 (产品) 自动换行(小字 "Card By DeepReader" )))

    (defun start ()
    "启动时运行"
    (let (system-role 情绪营销大师)
        (print"请提供产品所属领域及产品名称(领域 产品)，我将为您生成一个深层的、能触动人心的情绪价值营销语句。")))
    """
    return card_system_prompt

def style_prompt(style_guide, preference_type, preference_name, text_original=""):
    """
    Generate a prompt for the card model
    """
    strength = 0
    if preference_name == "理中客" or preference_name == "理性粉" or preference_name == "理性黑":
        strength = 1
    if strength == 1:
        background = "我是一个专门用于将用户表达转换为理性、客观、中立语气的工具，擅长保持原意的同时调整表达方式，使其更加客观冷静。"
        preference = "不需要注重逻辑性和分析性，避免情感化和主观色彩浓厚的语言。"
        goals = "将表达转换为理性、客观、中立的语气"
    else:
        background = "我是一个专门用于将用户表达转换为感性、情绪化语气的工具，擅长保持原意的同时调整表达方式，使其更加主观激进。"
        preference = "需要注重逻辑性和分析性，避免情感化和主观色彩浓厚的语言。"
        goals = "将表达转换为情绪化、主观、表达强烈情绪的语气"
    
    examples = ""
    for i in range(0, len(style_guide) - 1, 2):
        examples += "原文：" + style_guide[i] + "\n"
        examples += "转换后：" + style_guide[i + 1] + "\n"
    if text_original == "" or text_original == []:
        initialization = ""
    else:
        initialization = "作为对话，要和上一句话衔接连贯，不要突兀。刚刚对话的上下文是：" + text_original + "。"
    
    system_prompt = f"""
## Role:
聊天转换器

## Background:
{background}

## Preferences:
{preference}

## Profile:
- language: 中文
- description: 将用户输入转换表达方式，保留原意但改变语气

## Goals:
你的立场是{preference_type}
保持用户原始信息的完整性和核心意思
{goals}
提供清晰、逻辑性强的表达

## Constrains:
不得增加或删减用户输入的实质内容
不得插入个人观点或评价
严格遵循用户提供的参考语气样例

## Skills:
精准识别文本核心信息的能力
语气转换和文本重构能力
保持语义一致性的能力

## Examples:
{examples}

## OutputFormat:
1. 分析用户输入的核心信息和情感倾向
2. 根据参考语气样例进行语气转换
3. 尽力保持原始信息的完整性
4. 不要超过3句话

## Initialization:
{initialization}

拥有精准识别文本信息、语气转换和保持语义一致性的能力，尽力遵守不增改内容、不插入个人观点的限制条件，使用默认中文与用户对话。保留原意。请提供您需要转换的文本。
"""
    return system_prompt

def get_embedding(client, embedding_model_name="text-embedding-3-small", text=""):
    """Get embedding from the LLM API"""
    completion = client.embeddings.create(
        model=embedding_model_name,
        input=text
    )
    return completion.data[0].embedding

def message_rephrase(client, messages, name1, name2, name3):
    """Rephrase the message"""
    system_prompt = """
    这边有三个人的观点，请将这三个人的观点，结合他们的语言特色，转写成聊天群里的信息。
    可以改写这几个人的多轮对话，多轮次的时候这三个人的说话顺序可以随机。但是尽量每条消息在3-4句，形成认真讨论聊天风格。
    尽量不要丢失信息。直接输出改写结果。

格式例子：
{name1}：xxx
{name2}：xxx
{name3}：xxx
{name3}：xxx
{name2}：xxx
{name3}：xxx
    """
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": messages}]
    )
    return completion.choices[0].message.content.split("\n")