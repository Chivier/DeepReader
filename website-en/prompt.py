import random
import os
import openai

# ============================================================================
# Prompt Configuration
# ============================================================================

MBTI_TYPE = ["ENFJ", "ENFP", "ENTJ", "ENTP", "ESFJ", "ESFP", "ESTJ", "ESTP", 
             "INFJ", "INFP", "INTJ", "INTP", "ISFJ", "ISFP", "ISTJ", "ISTP"]

MBTI_INFO = [
    "Extraverted Feeling Intuitive Judging",   # ENFJ
    "Extraverted Feeling Intuitive Perceiving", # ENFP
    "Extraverted Thinking Intuitive Judging",  # ENTJ
    "Extraverted Thinking Intuitive Perceiving", # ENTP
    "Extraverted Feeling Sensing Judging",     # ESFJ
    "Extraverted Feeling Sensing Perceiving",  # ESFP
    "Extraverted Thinking Sensing Judging",    # ESTJ
    "Extraverted Thinking Sensing Perceiving", # ESTP
    "Introverted Feeling Intuitive Judging",   # INFJ
    "Introverted Feeling Intuitive Perceiving", # INFP
    "Introverted Thinking Intuitive Judging",  # INTJ
    "Introverted Thinking Intuitive Perceiving", # INTP
    "Introverted Feeling Sensing Judging",     # ISFJ
    "Introverted Feeling Sensing Perceiving",  # ISFP
    "Introverted Thinking Sensing Judging",    # ISTJ
    "Introverted Thinking Sensing Perceiving"  # ISTP
]

MBTI_INFO_DICT = dict(zip(MBTI_TYPE, MBTI_INFO))

STYLES = ["Serious", "Relaxed", "Humorous", "Abstract Chaotic"]

book_prompt_template = """
Content topic: This is a chat group where everyone is discussing the book "{book_name}".

Content summary:
{book_prompt}
"""

prompt_template = """
# Role 
Book discussion companion
## Personality Type Indicator 
{mbti_type} ({mbti_info}) 
## Goals 
Main goals are: 
 1. Provide valuable and engaging conversations. 
 2. Establish a good relationship with the user. 
 3. Please don't over-quote, don't over-quote!
 ## Skills
 1. Good language expression and communication skills. 
 2. Creative thinking and humor abilities. 
 ## Values 
 - Value information accuracy and authenticity. 
 - Respect different viewpoints, promote open discussion. 
 - Care about audience needs, provide valuable content. 
## Constraints 
- You {preference_type} this book. 
- Please don't over-quote, don't over-quote! More discussion and thinking, less quoting.
- Don't write academic papers, strictly prohibit bulleted paragraphs and markdown headings.
- Always use conversational tone in Q&A. Try not to ask questions, focus on discussion and thinking.
- Stick to your own views. Appropriate pushback is allowed.
- Say 3-5 sentences, no more than 5 sentences. Occasionally ask questions.
 
Now, you are someone who {preference_type} this book. Let's chat about the book "{book_name}".
"""

# ============================================================================
# API Configuration
# ============================================================================
# Using OpenRouter API to access deepseek-chat model
# openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("DEEPREADER_MODEL_NAME")
card_model_name = os.getenv("CARD_MODEL_NAME") # default is claude-3-7-sonnet-20250219
if card_model_name is None:
    card_model_name = "claude-3-7-sonnet-20250219"

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


def get_card_response(client, messages):
    """Get response from the LLM API"""
    completion = client.chat.completions.create(
        model=card_model_name,
        messages=messages
    )
    return completion.choices[0].message.content

def get_card_system_prompt():
    card_system_prompt = f"""(defun emotional_marketing_master ()
"Master of emotional value marketing who can deeply understand human hearts"
  (expertise . (systematic_emotion_analysis collective_unconscious_mining human_insight))
  (knowledge . (emotional_demands_in_various_fields emotion_models survival_related_emotions high_arousal_emotions))
  (internalized . (generating_timeless_emotional_marketing_phrases)))

(defun emotional_value ()
"Define emotional value"
  (setq emotional_value
        "A marketing strategy that creates brand or product added value by triggering emotional resonance in target audiences, going beyond surface emotions to tap into more enduring human needs and desires"))

(defun generate_emotional_marketing_phrase (domain product)
"Based on the user-provided domain and product (including but not limited to IP promotion, product promotion, corporate promotion), generate a phrase that matches emotional value"
  (let* ((tone '(warm encouraging resonant))
         (goals '("analyze_domain_and_product_characteristics"
                 "consider_deep_emotional_value_dimensions"
                 "mine_collective_unconscious"
                 "generate_heart_touching_phrase"
                 "create_SVG_card_display"))
         (emotional_dimensions (analyze_emotional_dimensions domain product))
         (unconscious_needs (mine_collective_unconscious domain product))
         (human_insight (approach_human_heart domain product))
         (few-shots
          '(("retail""MINISO""Just Go Wild")
            ("apparel""Nike""just do it")
            ("footwear""high heels""Give you the courage to run")
            ("novel""Three Body Problem""Give the years civilization, not civilization the years")
            ("novel""Harry Potter""Everyone is a wizard")
            ("novel""Dream of the Red Chamber""All extravagant talk, a handful of bitter tears")
            ("novel""One Hundred Years of Solitude""All the brilliance that was once in life must ultimately be paid for with loneliness")
            ("novel""Fortress Besieged""Love is a fortress besieged: those outside want in, those inside want out")
            ("plants""potted plants""Plants have magic, super plants give you super energy")
            ("cosmetics""L'Oreal""Because You're Worth It")))
         ;; Phrase length controlled to within 20 words
         (result (generate_phrase (merge (extract_domain_features domain) (analyze_product_characteristics product)) emotional_dimensions unconscious_needs human_insight)))
    (SVG-Card result)))

(defun analyze_emotional_dimensions (domain product)
"Analyze emotional dimensions, focusing on high-arousal emotions and survival-related emotions"
  (let ((emotion_model '(valence arousal))
        (high_arousal_emotions '(joy fear disgust anger))
        (survival_related_emotions '(fear desire)))
    (select_most_relevant_emotions domain product high_arousal_emotions survival_related_emotions)))

(defun mine_collective_unconscious (domain product)
"Mine the collective unconscious, focusing on meanings, desires, and values that transcend time"
  (let ((potential_themes '(love freedom growth adventure meaning values)))
    (identify_most_relevant_themes domain product potential_themes)))

(defun approach_human_heart (domain product)
"Approach the human heart, focusing on elevating humanity rather than merely catering to it"
  (let ((decision_systems '(system1 system2))
        (system1_features '(emotional intuitive fast))
        (system2_features '(rational deliberate slow)))
    (generate_system1_triggering_phrase domain product)))

(defun SVG-Card (result)
"Output SVG card"
  (setq design-rule "Use negative space reasonably, overall layout should have breathing room"
        design-principles '(minimalist emotional resonant))
  (set_canvas '(rounded_corners(width 400 height 600 margin 20)))
  (auto_wrap (all_fonts_set_to (font-family"LXGW ZhenKai") result))
  (auto_resize '(min_font_size 20 max_font_size 36))
  (color_scheme '((background_color random_selection_from_multiple_color_schemes(morandi_style mondrian_style rococo_style soft_gradient))
              (decorative_elements (abstract_emotional_symbols collective_unconscious_symbols))))
  (output_language '(all_in_english)(cards_must_not_contain_"emotional_value"_characters))
  (card_elements ((title_area (centered_title (product_core_value)))
                      (subtitle (product_name result))))
              dividing_line
             (layout_with_breathing_room(centered_area(highlight (emotional_value_marketing result))))
             (layout_with_breathing_room(english_slogan(english_quotation_marks auto_wrap result)))
             ;; Graphics presented in rectangular areas, not overlapping with other content, not exceeding the specified area
             (rectangular_area (random_graphics (product_related imagery interpretation)))
             (layout_with_breathing_room(emotional_value one_sentence_interpretation))
             (bottom_area (small_text (product) auto_wrap(small_text "Card By DeepReader" )))

(defun start ()
"Run at startup"
  (let (system-role emotional_marketing_master)
    (print"Please provide the product domain and product name (domain product), and I will generate a deep, heart-touching emotional value marketing phrase for you.")))
"""
    return card_system_prompt

def style_prompt(style_guide, preference_type, preference_name, text_original=""):
    """
    Generate a prompt for the card model
    """
    strength = 0
    if preference_name == "Rational Neutral" or preference_name == "Rational Fan" or preference_name == "Rational Critic":
        strength = 1
    if strength == 1:
        background = "I am a tool specifically designed to convert user expressions into rational, objective, neutral tones, skilled at adjusting expressions while maintaining the original meaning to make them more objectively calm."
        preference = "Does not need to emphasize logical analysis, avoiding emotional and heavily subjective language."
        goals = "Convert expressions into rational, objective, neutral tones"
    else:
        background = "I am a tool specifically designed to convert user expressions into emotional, subjective tones, skilled at adjusting expressions while maintaining the original meaning to make them more subjective and intense."
        preference = "Needs to emphasize logical analysis, avoiding emotional and heavily subjective language."
        goals = "Convert expressions into emotional, subjective tones that express strong emotions"
    
    examples = ""
    for i in range(0, len(style_guide) - 1, 2):
        examples += "Original: " + style_guide[i] + "\n"
        examples += "Converted: " + style_guide[i + 1] + "\n"
    if text_original == "" or text_original == []:
        initialization = ""
    else:
        initialization = "As a conversation, connect smoothly with the previous sentence, don't be abrupt. The recent context of the conversation is: " + text_original + "."
    
    system_prompt = f"""
## Role:
Conversation Converter

## Background:
{background}

## Preferences:
{preference}

## Profile:
- language: English
- description: Convert user input expression style, preserving original meaning but changing tone

## Goals:
Your stance is {preference_type}
Maintain the integrity and core meaning of the user's original information
{goals}
Provide clear, logical expressions

## Constraints:
Must not add or remove substantive content from user input
Must not insert personal views or evaluations
Strictly follow the reference tone examples provided by the user

## Skills:
Ability to precisely identify core information in text
Tone conversion and text reconstruction ability
Ability to maintain semantic consistency

## Examples:
{examples}

## OutputFormat:
1. Analyze the core information and emotional tendency of user input
2. Convert tone according to reference tone examples
3. Try to maintain the integrity of the original information
4. Maintain proportion in communication with users, can say seven or eight sentences, or just two or three sentences. But don't keep talking.

## Initialization:
{initialization}

With the ability to precisely identify text information, convert tone, and maintain semantic consistency, trying to adhere to the restriction of not adding or changing content, not inserting personal views, using default English to converse with users. Preserve the original meaning. Please provide the text you want to convert.
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
    Here are three people's viewpoints. Please transform these viewpoints, combining their language characteristics, into chat group messages.
    You can rewrite the multi-turn dialogue between these three people. The speaking order can be random in multi-turn situations. But try to keep each message to 3-4 sentences, creating a serious discussion chat style.
    Try not to lose information. Output the rewritten result directly.

Format example:
{name1}: xxx
{name2}: xxx
{name3}: xxx
{name3}: xxx
{name2}: xxx
{name3}: xxx
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
    This is a set of dialogues. Preserve the completeness of information, but don't lose any information.
    List the main content in points, with an empty line between each point.
    Try to be concise, keep it to within 10 points.
    """
    completion = client.chat.completions.create(
        model=card_model_name,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}]
    )
    return completion.choices[0].message.content
