<<<<<<< HEAD
"""Audio format conversion utilities."""

from pathlib import Path
import subprocess
import shutil


def convert_to_m4a(audio_path: Path, output_path: Path = None) -> Path:
=======
"""Audio file format converter using FFmpeg."""

from pathlib import Path
from typing import Optional
import subprocess
import tempfile
import shutil


# Supported audio formats
SUPPORTED_FORMATS = {
    ".m4a", ".mp3", ".wav", ".flac", ".aac", 
    ".ogg", ".wma", ".opus", ".m4b", ".aiff", 
    ".ape", ".webm", ".mp4", ".avi", ".mkv"
}


def is_supported_audio(file_path: Path) -> bool:
    """Check if file is a supported audio format."""
    return file_path.suffix.lower() in SUPPORTED_FORMATS


def check_ffmpeg() -> bool:
    """Check if FFmpeg is available."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def convert_to_m4a(
    input_path: Path,
    output_path: Optional[Path] = None,
    bitrate: str = "128k",
    keep_original: bool = True
) -> Path:
>>>>>>> 05d4f8ccc35e2d4e2a3b9325c6763060b2110c3b
    """
    Convert audio file to M4A format using FFmpeg.
    
    Args:
<<<<<<< HEAD
        audio_path: Input audio file path
        output_path: Output M4A path (if None, creates in same directory)
    
    Returns:
        Path to M4A file
    """
    if audio_path.suffix.lower() == ".m4a":
        return audio_path
    
    if output_path is None:
        output_path = audio_path.with_suffix(".m4a")
    
    # Check if FFmpeg is available
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
    
    print(f"Converting {audio_path.name} to M4A...")
    
    # FFmpeg command
    cmd = [
        ffmpeg_path,
        "-i", str(audio_path),
        "-c:a", "aac",
        "-b:a", "192k",
        "-y",  # Overwrite output
        str(output_path)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {result.stderr}")
        
        print(f"  ✓ Converted to: {output_path.name}")
        return output_path
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg conversion timed out")


def ensure_m4a(audio_path: Path) -> Path:
    """
    Ensure audio is in M4A format, converting if necessary.
    
    Args:
        audio_path: Input audio file
        
    Returns:
        Path to M4A file (original or converted)
    """
    if audio_path.suffix.lower() == ".m4a":
        return audio_path
    
    return convert_to_m4a(audio_path)
=======
        input_path: Input audio file path
        output_path: Output M4A file path (optional, auto-generated if None)
        bitrate: Audio bitrate for conversion (default: 128k)
        keep_original: Whether to keep the original file (default: True)
    
    Returns:
        Path to the converted M4A file
        
    Raises:
        RuntimeError: If FFmpeg is not available or conversion fails
    """
    
    if not check_ffmpeg():
        raise RuntimeError(
            "FFmpeg not found. Please install FFmpeg and add it to PATH.\n"
            "Download: https://ffmpeg.org/download.html"
        )
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # If already M4A, return as-is
    if input_path.suffix.lower() == ".m4a":
        return input_path
    
    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.with_suffix(".m4a")
    
    # If output already exists and is newer than input, skip conversion
    if output_path.exists():
        if output_path.stat().st_mtime >= input_path.stat().st_mtime:
            print(f"✓ M4A already exists: {output_path.name}")
            return output_path
    
    print(f"Converting {input_path.suffix} → M4A: {input_path.name}")
    
    # Use temporary file to avoid partial writes
    with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
    
    try:
        # FFmpeg conversion command
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-vn",  # No video
            "-c:a", "aac",  # AAC codec
            "-b:a", bitrate,  # Bitrate
            "-movflags", "+faststart",  # Optimize for streaming
            "-y",  # Overwrite output
            str(tmp_path)
        ]
        
        # Run conversion (suppress output)
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='ignore')
            raise RuntimeError(f"FFmpeg conversion failed:\n{stderr}")
        
        # Move temp file to final destination
        shutil.move(str(tmp_path), str(output_path))
        
        print(f"✓ Converted successfully: {output_path.name}")
        
        # Optionally delete original file
        if not keep_original:
            input_path.unlink()
            print(f"  Deleted original: {input_path.name}")
        
        return output_path
        
    except Exception as e:
        # Clean up temp file on error
        if tmp_path.exists():
            tmp_path.unlink()
        raise e


def batch_convert_to_m4a(
    input_files: list[Path],
    output_dir: Optional[Path] = None,
    bitrate: str = "128k",
    keep_original: bool = True
) -> list[Path]:
    """
    Batch convert multiple audio files to M4A.
    
    Args:
        input_files: List of input audio files
        output_dir: Output directory (optional, uses input directory if None)
        bitrate: Audio bitrate for conversion
        keep_original: Whether to keep original files
    
    Returns:
        List of converted M4A file paths
    """
    
    converted_files = []
    
    for input_path in input_files:
        try:
            if output_dir:
                output_path = output_dir / f"{input_path.stem}.m4a"
            else:
                output_path = None
            
            m4a_path = convert_to_m4a(
                input_path,
                output_path=output_path,
                bitrate=bitrate,
                keep_original=keep_original
            )
            converted_files.append(m4a_path)
            
        except Exception as e:
            print(f"❌ Failed to convert {input_path.name}: {e}")
    
    return converted_files
>>>>>>> 05d4f8ccc35e2d4e2a3b9325c6763060b2110c3b
