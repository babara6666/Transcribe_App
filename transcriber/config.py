"""Configuration management for the transcriber."""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""
    
    hf_token: str
    watch_dir: Path
    output_dir: Path
    model_size: str
    min_speakers: Optional[int]
    max_speakers: Optional[int]
    device: str
    compute_type: str
    enable_translation: bool = True  # Enable English to Chinese translation
    generate_pdf: bool = True  # Generate PDF alongside Markdown

    def __post_init__(self):
        # Ensure directories exist
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


def load_config(env_path: Optional[Path] = None) -> Config:
    """Load configuration from environment variables."""
    
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()
    
    hf_token = os.getenv("HF_TOKEN", "")
    if not hf_token:
        raise ValueError("HF_TOKEN environment variable is required. "
                        "Get your token at https://huggingface.co/settings/tokens")
    
    watch_dir = Path(os.getenv("WATCH_DIR", r"C:\Users\tnfsh\Downloads\zhanlu"))
    output_dir = Path(os.getenv("OUTPUT_DIR", str(watch_dir)))
    model_size = os.getenv("MODEL_SIZE", "large-v3")
    
    # Parse speaker settings
    min_speakers_str = os.getenv("MIN_SPEAKERS", "")
    max_speakers_str = os.getenv("MAX_SPEAKERS", "")
    min_speakers = int(min_speakers_str) if min_speakers_str else None
    max_speakers = int(max_speakers_str) if max_speakers_str else None
    
    # Auto-detect device and compute type
    device, compute_type = detect_device()
    
    # Translation and PDF settings
    enable_translation = os.getenv("ENABLE_TRANSLATION", "true").lower() in ("true", "1", "yes")
    generate_pdf = os.getenv("GENERATE_PDF", "true").lower() in ("true", "1", "yes")
    
    return Config(
        hf_token=hf_token,
        watch_dir=watch_dir,
        output_dir=output_dir,
        model_size=model_size,
        min_speakers=min_speakers,
        max_speakers=max_speakers,
        device=device,
        compute_type=compute_type,
        enable_translation=enable_translation,
        generate_pdf=generate_pdf,
    )


def detect_device() -> tuple[str, str]:
    """Detect available compute device and optimal compute type."""
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✓ GPU detected: {gpu_name}")
            print(f"  CUDA version: {torch.version.cuda}")
            return "cuda", "float16"
        else:
            print("⚠ No GPU detected, using CPU (this will be significantly slower)")
            return "cpu", "int8"
    except ImportError:
        print("⚠ PyTorch not installed, defaulting to CPU")
        return "cpu", "int8"
