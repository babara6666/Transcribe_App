"""File scanner for detecting unprocessed audio files."""

from pathlib import Path
from typing import List
from collections import Counter

# Supported audio formats
AUDIO_EXTENSIONS = (".m4a", ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".webm")


def scan_directory(directory: Path, extensions: tuple = AUDIO_EXTENSIONS) -> List[Path]:
    """Scan directory for audio files with specified extensions."""
    
    if not directory.exists():
        print(f"⚠ Watch directory does not exist: {directory}")
        return []
    
    files = []
    for ext in extensions:
        files.extend(directory.glob(f"*{ext}"))
    
    # Count by extension
    ext_counts = Counter(f.suffix.lower() for f in files)
    ext_summary = ", ".join(f"{ext}({count})" for ext, count in ext_counts.items())
    
    print(f"Found {len(files)} audio file(s) in {directory}")
    if ext_summary:
        print(f"  Formats: {ext_summary}")
    
    return sorted(files)


def is_processed(audio_path: Path, output_dir: Path) -> bool:
    """Check if audio file has already been processed (md file exists)."""
    
    md_path = output_dir / f"{audio_path.stem}.md"
    return md_path.exists()


def get_pending_files(
    watch_dir: Path,
    output_dir: Path,
    extensions: tuple = AUDIO_EXTENSIONS
) -> List[Path]:
    """Get list of audio files that haven't been processed yet."""
    
    all_files = scan_directory(watch_dir, extensions)
    pending = [f for f in all_files if not is_processed(f, output_dir)]
    
    skipped = len(all_files) - len(pending)
    if skipped > 0:
        print(f"Skipping {skipped} already processed file(s)")
    
    print(f"Pending files to process: {len(pending)}")
    return pending
