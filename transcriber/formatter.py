"""Markdown formatting for transcription output."""

from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import opencc
    _converter = opencc.OpenCC('s2twp')  # 簡體 → 繁體台灣用語
except ImportError:
    _converter = None

from .transcribe import TranscriptResult, format_time


def convert_to_traditional(text: str) -> str:
    """Convert simplified Chinese to traditional Chinese (Taiwan)."""
    if _converter is None:
        return text
    return _converter.convert(text)


def format_markdown(result: TranscriptResult, timestamp: Optional[datetime] = None) -> str:
    """Format transcription result as Markdown with traditional Chinese conversion."""
    
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
        # Speaker label bold, timestamp separate
        lines.append(f"**[{segment.speaker}]**  {time_range}")
        lines.append("")
        # Convert main transcript text to traditional Chinese
        text = convert_to_traditional(segment.text)
        lines.append(text)
        lines.append("")
        
        # Add translation if available (displayed as blockquote with [翻譯]: prefix)
        if hasattr(segment, 'translation') and segment.translation:
            translation = convert_to_traditional(segment.translation)
            lines.append(f"> **[翻譯]:** {translation}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Convert entire output to traditional Chinese (catch any remaining simplified)
    content = "\n".join(lines)
    return convert_to_traditional(content)


def save_markdown(
    result: TranscriptResult,
    output_dir: Path,
    timestamp: Optional[datetime] = None,
    generate_pdf: bool = True
) -> Path:
    """Save transcription result as Markdown file, optionally generate PDF."""
    
    if timestamp is None:
        timestamp = datetime.now()
    
    content = format_markdown(result, timestamp)
    output_path = output_dir / f"{result.audio_path.stem}.md"
    
    output_path.write_text(content, encoding="utf-8")
    print(f"✓ Markdown saved: {output_path}")
    
    # Generate PDF if requested
    if generate_pdf:
        pdf_path = output_dir / f"{result.audio_path.stem}.pdf"
        try:
            markdown_to_pdf(content, pdf_path)
            print(f"✓ PDF saved: {pdf_path}")
        except Exception as e:
            print(f"⚠ PDF generation failed: {e}")
    
    return output_path


def markdown_to_pdf(markdown_content: str, output_path: Path) -> None:
    """Convert Markdown content to PDF with CJK font support using pypandoc + xelatex."""
    import pypandoc
    import tempfile
    
    # Ensure Pandoc is available
    try:
        pypandoc.get_pandoc_version()
    except OSError:
        print("  Downloading Pandoc...")
        pypandoc.download_pandoc()
    
    # Write markdown to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(markdown_content)
        temp_md = f.name
    
    try:
        # PDF engine settings for CJK support
        extra_args = [
            '--pdf-engine=xelatex',
            '-V', 'CJKmainfont=Microsoft JhengHei',  # 微軟正黑體
            '-V', 'geometry:margin=2cm',
            '-V', 'fontsize=11pt',
            '-V', 'documentclass=article',
            '--highlight-style=tango',
        ]
        
        pypandoc.convert_file(
            temp_md,
            'pdf',
            outputfile=str(output_path),
            extra_args=extra_args
        )
    finally:
        # Cleanup temp file
        import os
        os.unlink(temp_md)

