"""Auto-Transcriber with Speaker Diarization using WhisperX."""

from .config import Config, load_config
from .scanner import scan_directory, get_pending_files
from .transcribe import transcribe_audio, TranscriptResult
from .formatter import format_markdown, save_markdown
from .audio_converter import (
    convert_to_m4a,
    batch_convert_to_m4a,
    is_supported_audio,
    SUPPORTED_FORMATS,
)
from .translator import (
    translate_to_chinese,
    is_english_text,
    add_translation,
)
from .pdf_generator import (
    markdown_to_pdf,
    batch_convert_to_pdf,
)

__all__ = [
    "Config",
    "load_config",
    "scan_directory",
    "get_pending_files",
    "transcribe_audio",
    "TranscriptResult",
    "format_markdown",
    "save_markdown",
    "convert_to_m4a",
    "batch_convert_to_m4a",
    "is_supported_audio",
    "SUPPORTED_FORMATS",
    "translate_to_chinese",
    "is_english_text",
    "add_translation",
    "markdown_to_pdf",
    "batch_convert_to_pdf",
]
