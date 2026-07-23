# chatbot/markdown_utils.py
import re
import markdown


def clean_markdown(text: str) -> str:
    """ينظف أخطاء التنسيق الشائعة قبل التحويل لـ HTML."""
    text = re.sub(r'^(#{1,6})\s*\*\*(.+?)\*\*\s*$', r'\1 \2', text, flags=re.MULTILINE)
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def markdown_to_html(text: str) -> str:
    """ينظف النص ثم يحوله لـ HTML جاهز للعرض."""
    cleaned = clean_markdown(text)
    return markdown.markdown(
        cleaned,
        extensions=['tables', 'fenced_code', 'nl2br']
    )