"""Audio format conversion utilities."""

from pathlib import Path
import subprocess
import shutil


def convert_to_m4a(audio_path: Path, output_path: Path = None) -> Path:
    """
    Convert audio file to M4A format using FFmpeg.
    
    Args:
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
