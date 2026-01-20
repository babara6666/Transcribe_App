"""Translation service using TranslateGemma via Ollama."""

import re
from typing import Optional


def is_english_text(text: str, threshold: float = 0.5) -> bool:
    """
    Detect if text is primarily English.
    
    Args:
        text: Input text
        threshold: Ratio of Latin characters to consider as English
        
    Returns:
        True if text is primarily English
    """
    if not text or not text.strip():
        return False
    
    # Count Latin letters (a-z, A-Z)
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = len(re.findall(r'\S', text))  # Non-whitespace
    
    if total_chars == 0:
        return False
    
    return (latin_chars / total_chars) >= threshold


def translate_text(text: str, source_lang: str = "en", target_lang: str = "zh") -> Optional[str]:
    """
    Translate text using TranslateGemma via Ollama.
    
    Args:
        text: Text to translate
        source_lang: Source language code (default: English)
        target_lang: Target language code (default: Chinese)
        
    Returns:
        Translated text or None if failed
    """
    import ollama
    
    if not text or not text.strip():
        return None
    
    try:
        # TranslateGemma official prompt format
        prompt = f"""You are a professional English (en) to Chinese (zh-Hant) translator. Your goal is to accurately convey the meaning and nuances of the original English text while adhering to Chinese grammar, vocabulary, and cultural sensitivities. Produce only the Traditional Chinese translation, without any additional explanations or commentary. Please translate the following English text into Traditional Chinese:


{text}"""
        
        response = ollama.chat(
            model='translategemma:4b',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.3}
        )
        
        # Handle both new (object) and old (dict) API formats
        if hasattr(response, 'message'):
            translated = response.message.content.strip()
        else:
            translated = response['message']['content'].strip()
        return translated
        
    except Exception as e:
        print(f"    ⚠ Translation failed: {e}")
        return None


def translate_segments(segments: list, show_progress: bool = True) -> list:
    """
    Translate English segments to Chinese.
    
    Args:
        segments: List of segment dicts with 'text' key
        show_progress: Show translation progress
        
    Returns:
        Updated segments with 'translation' key for English segments
    """
    if show_progress:
        print("Translating English segments...")
    
    english_count = 0
    translated_count = 0
    
    for i, seg in enumerate(segments):
        text = seg.get('text', '')
        
        if is_english_text(text):
            english_count += 1
            translation = translate_text(text)
            
            if translation:
                seg['translation'] = translation
                translated_count += 1
                if show_progress:
                    print(f"  ✓ Translated segment {i+1}")
    
    if show_progress:
        print(f"✓ Translation complete: {translated_count}/{english_count} English segments")
    
    return segments


def check_ollama_available() -> bool:
    """Check if Ollama server is running and model is available. Auto-starts if needed."""
    # Try to start Ollama first
    if not _is_ollama_running():
        print("  Starting Ollama server...")
        if not start_ollama():
            return False
    
    try:
        import ollama
        response = ollama.list()
        # New API returns objects with .models attribute
        if hasattr(response, 'models'):
            model_names = [m.model for m in response.models]
        else:
            # Fallback for old API (dict format)
            model_names = [m.get('name', '') for m in response.get('models', [])]
        return any('translategemma' in name for name in model_names)
    except Exception as e:
        print(f"  Ollama check failed: {e}")
        return False


def _is_ollama_running() -> bool:
    """Check if Ollama server is already running."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(('127.0.0.1', 11434))
            return True
    except (socket.error, socket.timeout):
        return False


def start_ollama() -> bool:
    """Start Ollama server in background."""
    import subprocess
    import time
    
    try:
        # Start Ollama serve in background
        subprocess.Popen(
            ['ollama', 'serve'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        # Wait for server to be ready (max 10 seconds)
        for _ in range(20):
            time.sleep(0.5)
            if _is_ollama_running():
                print("  ✓ Ollama server started")
                return True
        
        print("  ⚠ Ollama server failed to start in time")
        return False
        
    except FileNotFoundError:
        print("  ⚠ Ollama not installed. Download from: https://ollama.com/download")
        return False
    except Exception as e:
        print(f"  ⚠ Failed to start Ollama: {e}")
        return False


