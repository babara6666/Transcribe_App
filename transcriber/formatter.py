"""Markdown formatting for transcription output."""

from pathlib import Path
from datetime import datetime
from typing import Optional

from .transcribe import TranscriptResult, format_time


def format_markdown(result: TranscriptResult, timestamp: Optional[datetime] = None) -> str:
    """Format transcription result as Markdown."""
    
    if timestamp is None:
        timestamp = datetime.now()
    
    lines = [
        "# 會議轉錄記錄",
        "",
        f"**檔案名稱:** {result.audio_path.name}",
        f"**轉錄時間:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**偵測語言:** {result.language}",
        "",
        "---",
        "",
    ]
    
    for segment in result.segments:
        time_range = f"({format_time(segment.start)} - {format_time(segment.end)})"
        lines.append(f"**[{segment.speaker}]:** {time_range}")
        lines.append(segment.text)
        lines.append("")
    
    return "\n".join(lines)


def save_markdown(
    result: TranscriptResult,
    output_dir: Path,
    timestamp: Optional[datetime] = None
) -> Path:
    """Save transcription result as Markdown file."""
    
    if timestamp is None:
        timestamp = datetime.now()
    
    content = format_markdown(result, timestamp)
    output_path = output_dir / f"{result.audio_path.stem}.md"
    
    output_path.write_text(content, encoding="utf-8")
    print(f"✓ Saved: {output_path}")
    
    return output_path
