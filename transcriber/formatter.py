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
    """Convert Markdown content to PDF with CJK font support using fpdf2."""
    from fpdf import FPDF
    import re
    
    # Try to load CJK font
    font_name = 'Arial'  # Default fallback
    
    class PDF(FPDF):
        def header(self):
            pass
        
        def footer(self):
            self.set_y(-15)
            self.set_font(font_name, '', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    # Create PDF
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Try to load CJK font
    try:
        # Try Microsoft JhengHei (繁體中文)
        pdf.add_font('CJK', '', r'C:\Windows\Fonts\msjh.ttc', uni=True)
        pdf.add_font('CJK', 'B', r'C:\Windows\Fonts\msjhbd.ttc', uni=True)
        font_name = 'CJK'
    except:
        try:
            # Try SimSun (簡體中文)
            pdf.add_font('CJK', '', r'C:\Windows\Fonts\simsun.ttc', uni=True)
            pdf.add_font('CJK', 'B', r'C:\Windows\Fonts\simhei.ttf', uni=True)
            font_name = 'CJK'
        except:
            # Use Arial as fallback
            font_name = 'Arial'
    
    pdf.add_page()
    
    # Parse Markdown and add to PDF
    lines = markdown_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            pdf.ln(5)
            continue
        
        # Title (# heading)
        if line.startswith('# '):
            pdf.set_font(font_name, 'B', 16)
            pdf.multi_cell(0, 10, line[2:])
            pdf.ln(5)
        
        # Separator
        elif line == '---':
            pdf.ln(3)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
        
        # Bold text (speaker lines)
        elif line.startswith('**') and '**' in line[2:]:
            pdf.set_font(font_name, 'B', 11)
            # Remove ** markers
            clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
            pdf.multi_cell(0, 7, clean_line)
        
        # Regular text
        else:
            pdf.set_font(font_name, '', 11)
            pdf.multi_cell(0, 7, line)
    
    # Save PDF
    pdf.output(str(output_path))


