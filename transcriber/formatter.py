"""Markdown formatting for transcription output with translation and PDF export."""

from pathlib import Path
from datetime import datetime
from typing import Optional

from .transcribe import TranscriptResult, format_time
from .translator import add_translation, is_english_text
from .pdf_generator import markdown_to_pdf


def format_markdown(
    result: TranscriptResult,
    timestamp: Optional[datetime] = None,
    enable_translation: bool = True,
) -> str:
    """
    Format transcription result as beautifully formatted Markdown.
    
    Args:
        result: Transcription result
        timestamp: Timestamp for the transcription
        enable_translation: Whether to translate English segments to Chinese
    
    Returns:
        Formatted Markdown content
    """
    
    if timestamp is None:
        timestamp = datetime.now()
    
    # Calculate total duration
    total_duration = 0
    if result.segments:
        total_duration = result.segments[-1].end
    
    duration_str = format_time(total_duration)
    
    # Header section with metadata
    lines = [
        "# 📝 會議轉錄記錄",
        "",
        "## 📊 基本資訊",
        "",
        "| 項目 | 內容 |",
        "|------|------|",
        f"| 📁 檔案名稱 | `{result.audio_path.name}` |",
        f"| ⏱️ 總時長 | {duration_str} |",
        f"| 🕐 轉錄時間 | {timestamp.strftime('%Y-%m-%d %H:%M:%S')} |",
        f"| 🌐 偵測語言 | {result.language.upper()} |",
        f"| 👥 講者數量 | {len(set(s.speaker for s in result.segments))} |",
        "",
        "---",
        "",
        "## 💬 逐字稿內容",
        "",
    ]
    
    # Transcription content
    current_speaker = None
    segment_count = 0
    
    for segment in result.segments:
        # Add speaker header if changed
        if segment.speaker != current_speaker:
            current_speaker = segment.speaker
            segment_count += 1
            
            if segment_count > 1:
                lines.append("")  # Space between speakers
            
            lines.append(f"### 🎤 {segment.speaker}")
            lines.append("")
        
        # Format time range
        time_range = f"`{format_time(segment.start)} - {format_time(segment.end)}`"
        
        # Add segment with timestamp
        lines.append(f"**{time_range}**")
        lines.append("")
        
        # Add text with optional translation
        if enable_translation and is_english_text(segment.text):
            # This segment is English, add translation
            formatted_text = add_translation(segment.text, indent="  > ")
            lines.append(formatted_text)
        else:
            lines.append(segment.text)
        
        lines.append("")
    
    # Footer
    lines.extend([
        "",
        "---",
        "",
        f"*本文件由 Auto-Transcriber 自動生成於 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
    ])
    
    return "\n".join(lines)


def save_markdown(
    result: TranscriptResult,
    output_dir: Path,
    timestamp: Optional[datetime] = None,
    enable_translation: bool = True,
    generate_pdf: bool = True,
) -> Path:
    """
    Save transcription result as Markdown file.
    
    Args:
        result: Transcription result
        output_dir: Output directory
        timestamp: Timestamp for the transcription
        enable_translation: Whether to translate English segments to Chinese
        generate_pdf: Whether to also generate PDF file
    
    Returns:
        Path to the saved Markdown file
    """
    
    if timestamp is None:
        timestamp = datetime.now()
    
    # Generate markdown content
    print("Formatting markdown...")
    content = format_markdown(result, timestamp, enable_translation)
    
    # Save markdown
    output_path = output_dir / f"{result.audio_path.stem}.md"
    output_path.write_text(content, encoding="utf-8")
    print(f"✓ Markdown saved: {output_path}")
    
    # Generate PDF if requested
    if generate_pdf:
        try:
            pdf_path = markdown_to_pdf(output_path)
            print(f"✓ PDF generated: {pdf_path}")
        except Exception as e:
            print(f"⚠ PDF generation failed: {e}")
            print(f"  Install Pandoc: winget install JohnMacFarlane.Pandoc")
    
    return output_path
