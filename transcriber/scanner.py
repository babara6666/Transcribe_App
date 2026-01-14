"""File scanner for detecting unprocessed audio files."""

from pathlib import Path
from typing import List


def scan_directory(directory: Path, extension: str = ".m4a") -> List[Path]:
    """Scan directory for audio files with specified extension."""
    
    if not directory.exists():
        print(f"⚠ Watch directory does not exist: {directory}")
        return []
    
    files = list(directory.glob(f"*{extension}"))
    print(f"Found {len(files)} {extension} file(s) in {directory}")
    return sorted(files)


def is_processed(audio_path: Path, output_dir: Path) -> bool:
    """Check if audio file has already been processed (md file exists)."""
    
    md_path = output_dir / f"{audio_path.stem}.md"
    return md_path.exists()


def get_pending_files(
    watch_dir: Path,
    output_dir: Path,
    extension: str = ".m4a"
) -> List[Path]:
    """Get list of audio files that haven't been processed yet."""
    
    all_files = scan_directory(watch_dir, extension)
    pending = [f for f in all_files if not is_processed(f, output_dir)]
    
    skipped = len(all_files) - len(pending)
    if skipped > 0:
        print(f"Skipping {skipped} already processed file(s)")
    
    print(f"Pending files to process: {len(pending)}")
    return pending
