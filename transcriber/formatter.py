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
        
        # Add translation if available (displayed as blockquote)
        if hasattr(segment, 'translation') and segment.translation:
            lines.append(f"> {segment.translation}")
        
        lines.append("")
    
    return "\n".join(lines)


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
    """Convert Markdown content to PDF with CJK font support using WeasyPrint."""
    import markdown as md_lib
    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration
    
    # Convert Markdown to HTML
    html_content = md_lib.markdown(
        markdown_content,
        extensions=['tables', 'fenced_code', 'nl2br']
    )
    
    # Build complete HTML with embedded CSS
    full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        body {{
            font-family: "Noto Sans TC", "Microsoft JhengHei", "微軟正黑體", sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            font-size: 24pt;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 25px;
            font-size: 18pt;
        }}
        
        h3 {{
            color: #2980b9;
            margin-top: 20px;
            font-size: 16pt;
            page-break-after: avoid;
        }}
        
        p {{
            margin: 8px 0;
        }}
        
        strong {{
            color: #2c3e50;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin: 10px 0;
            color: #555;
            font-style: italic;
            background-color: #f8f9fa;
            padding: 10px 15px;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 20px 0;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
            font-size: 10pt;
        }}
        
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
    </style>
</head>
<body>
    {html_content}
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #ddd; text-align: center; color: #7f8c8d; font-size: 9pt;">
        <p>Auto-generated transcript</p>
    </div>
</body>
</html>
"""
    
    # Configure fonts and generate PDF
    font_config = FontConfiguration()
    HTML(string=full_html).write_pdf(str(output_path), font_config=font_config)
