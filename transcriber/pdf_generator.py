"""PDF generation from Markdown with CJK font support."""

import subprocess
from pathlib import Path
from typing import Optional
import tempfile
import shutil


def check_pandoc() -> bool:
    """Check if Pandoc is installed."""
    try:
        subprocess.run(
            ["pandoc", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def markdown_to_pdf(
    md_path: Path,
    pdf_path: Optional[Path] = None,
    font_family: str = "Microsoft JhengHei",
    font_size: int = 12,
) -> Path:
    """
    Convert Markdown to PDF with CJK font support using Pandoc.
    
    Args:
        md_path: Input Markdown file path
        pdf_path: Output PDF file path (optional, auto-generated if None)
        font_family: Font family for CJK characters (default: Microsoft JhengHei)
        font_size: Font size in points (default: 12)
    
    Returns:
        Path to the generated PDF file
        
    Raises:
        RuntimeError: If Pandoc is not available or conversion fails
    """
    
    if not check_pandoc():
        raise RuntimeError(
            "Pandoc not found. Please install Pandoc.\n"
            "Download: https://pandoc.org/installing.html\n"
            "Or use: winget install JohnMacFarlane.Pandoc"
        )
    
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")
    
    # Generate output path if not provided
    if pdf_path is None:
        pdf_path = md_path.with_suffix(".pdf")
    
    print(f"Converting Markdown → PDF: {md_path.name}")
    
    # Create LaTeX header for CJK support
    latex_header = f"""
\\usepackage{{xeCJK}}
\\setCJKmainfont{{{font_family}}}
\\usepackage{{fancyhdr}}
\\usepackage{{geometry}}
\\geometry{{
    a4paper,
    left=2.5cm,
    right=2.5cm,
    top=3cm,
    bottom=3cm
}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{\\small 會議轉錄記錄}}
\\fancyfoot[C]{{\\thepage}}
\\renewcommand{{\\headrulewidth}}{{0.4pt}}
\\usepackage{{hyperref}}
\\hypersetup{{
    colorlinks=true,
    linkcolor=blue,
    urlcolor=blue
}}
"""
    
    # Write header to temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.tex',
        delete=False,
        encoding='utf-8'
    ) as header_file:
        header_file.write(latex_header)
        header_path = Path(header_file.name)
    
    try:
        # Pandoc conversion command
        cmd = [
            "pandoc",
            str(md_path),
            "-o", str(pdf_path),
            "--pdf-engine=xelatex",
            f"--include-in-header={header_path}",
            f"--variable=fontsize:{font_size}pt",
            "--variable=documentclass:article",
            "--variable=papersize:a4",
            "--toc",  # Table of contents
            "--number-sections",  # Number sections
        ]
        
        # Run conversion
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='ignore')
            raise RuntimeError(f"Pandoc conversion failed:\n{stderr}")
        
        print(f"✓ PDF generated: {pdf_path.name}")
        return pdf_path
        
    finally:
        # Clean up temp header file
        if header_path.exists():
            header_path.unlink()


def batch_convert_to_pdf(
    md_files: list[Path],
    output_dir: Optional[Path] = None,
    font_family: str = "Microsoft JhengHei",
) -> list[Path]:
    """
    Batch convert multiple Markdown files to PDF.
    
    Args:
        md_files: List of Markdown files
        output_dir: Output directory (optional, uses input directory if None)
        font_family: Font family for CJK characters
    
    Returns:
        List of generated PDF file paths
    """
    
    pdf_files = []
    
    for md_path in md_files:
        try:
            if output_dir:
                pdf_path = output_dir / f"{md_path.stem}.pdf"
            else:
                pdf_path = None
            
            pdf = markdown_to_pdf(
                md_path,
                pdf_path=pdf_path,
                font_family=font_family
            )
            pdf_files.append(pdf)
            
        except Exception as e:
            print(f"❌ Failed to convert {md_path.name}: {e}")
    
    return pdf_files
