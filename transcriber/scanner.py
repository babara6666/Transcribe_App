"""File scanner for detecting unprocessed audio files."""

from pathlib import Path
from typing import List

from .audio_converter import SUPPORTED_FORMATS, is_supported_audio


def scan_directory(directory: Path, extension: str = None) -> List[Path]:
    """
    Scan directory for audio files.
    
    Args:
        directory: Directory to scan
        extension: Specific extension to filter (e.g., ".m4a")
                  If None, scans for all supported audio formats
    """
    
    if not directory.exists():
        print(f"⚠ Watch directory does not exist: {directory}")
        return []
    
    if extension:
        # Scan for specific extension
        files = list(directory.glob(f"*{extension}"))
        print(f"Found {len(files)} {extension} file(s) in {directory}")
    else:
        # Scan for all supported audio formats
        files = [
            f for f in directory.iterdir()
            if f.is_file() and is_supported_audio(f)
        ]
        print(f"Found {len(files)} audio file(s) in {directory}")
        
        if files:
            # Show format breakdown
            format_counts = {}
            for f in files:
                ext = f.suffix.lower()
                format_counts[ext] = format_counts.get(ext, 0) + 1
            
            formats_str = ", ".join(f"{ext}({cnt})" for ext, cnt in sorted(format_counts.items()))
            print(f"  Formats: {formats_str}")
    
    return sorted(files)


def is_processed(audio_path: Path, output_dir: Path) -> bool:
    """Check if audio file has already been processed (md file exists)."""
    
    md_path = output_dir / f"{audio_path.stem}.md"
    return md_path.exists()


def get_pending_files(
    watch_dir: Path,
    output_dir: Path,
    extension: str = None
) -> List[Path]:
    """
    Get list of audio files that haven't been processed yet.
    
    Args:
        watch_dir: Directory to watch for audio files
        output_dir: Directory where output MD files are saved
        extension: Specific extension to filter (optional)
                  If None, scans for all supported audio formats
    """
    
    all_files = scan_directory(watch_dir, extension)
    pending = [f for f in all_files if not is_processed(f, output_dir)]
    
    skipped = len(all_files) - len(pending)
    if skipped > 0:
        print(f"Skipping {skipped} already processed file(s)")
    
    print(f"Pending files to process: {len(pending)}")
    return pending

