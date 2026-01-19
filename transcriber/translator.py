"""Translation module for English to Chinese translation."""

import re
from typing import Optional
from deep_translator import GoogleTranslator


def is_english_text(text: str, threshold: float = 0.5) -> bool:
    """
    Check if text contains significant English content.
    
    Args:
        text: Text to check
        threshold: Minimum ratio of English characters to consider as English (0.0-1.0)
    
    Returns:
        True if text is predominantly English
    """
    # Remove punctuation and whitespace
    clean_text = re.sub(r'[^\w\s]', '', text)
    if not clean_text.strip():
        return False
    
    # Count English letters (a-z, A-Z)
    english_chars = len(re.findall(r'[a-zA-Z]', clean_text))
    # Count Chinese characters
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
    
    total_chars = len(clean_text.replace(' ', ''))
    if total_chars == 0:
        return False
    
    # If has English and ratio is above threshold
    english_ratio = english_chars / total_chars
    
    # Consider as English if:
    # 1. English ratio > threshold AND
    # 2. English chars > Chinese chars
    return english_ratio >= threshold and english_chars > chinese_chars


def translate_to_chinese(text: str, max_retries: int = 3) -> Optional[str]:
    """
    Translate English text to Traditional Chinese.
    
    Args:
        text: Text to translate
        max_retries: Maximum number of retry attempts
    
    Returns:
        Translated text, or None if translation fails
    """
    if not text or not text.strip():
        return None
    
    # Check if translation is needed
    if not is_english_text(text):
        return None
    
    try:
        translator = GoogleTranslator(source='en', target='zh-TW')
        
        # Handle long text by chunking (Google Translate has 5000 char limit)
        max_chunk_size = 4500
        if len(text) <= max_chunk_size:
            # Translate directly
            translated = translator.translate(text)
            return translated
        else:
            # Split by sentences and translate in chunks
            sentences = re.split(r'([.!?]+\s+)', text)
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= max_chunk_size:
                    current_chunk += sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = sentence
            
            if current_chunk:
                chunks.append(current_chunk)
            
            # Translate each chunk
            translated_chunks = []
            for chunk in chunks:
                if chunk.strip():
                    translated = translator.translate(chunk)
                    translated_chunks.append(translated)
            
            return ' '.join(translated_chunks)
    
    except Exception as e:
        print(f"⚠ Translation failed: {e}")
        return None


def add_translation(text: str, indent: str = "  ") -> str:
    """
    Add Chinese translation below English text if needed.
    
    Args:
        text: Original text
        indent: Indentation for translation line
    
    Returns:
        Text with translation appended (if English detected), otherwise original text
    """
    translation = translate_to_chinese(text)
    
    if translation:
        return f"{text}\n{indent}*翻譯: {translation}*"
    
    return text
