"""Core transcription logic using WhisperX with speaker diarization."""

from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import warnings
import os

# Suppress some noisy warnings
warnings.filterwarnings("ignore", message=".*torchaudio.*")
warnings.filterwarnings("ignore", message=".*torch.load.*")
warnings.filterwarnings("ignore", message=".*weights_only.*")
warnings.filterwarnings("ignore", category=FutureWarning)

# Fix for PyTorch 2.6+ weights_only=True breaking pyannote model loading
# This must be done BEFORE importing whisperx
import torch

# Monkey-patch torch.load to force weights_only=False
# This is necessary because pyannote models use omegaconf which isn't in the safe list
_original_torch_load = torch.load

def _patched_torch_load(*args, **kwargs):
    # Force weights_only=False for compatibility with pyannote/omegaconf
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)

torch.load = _patched_torch_load

from .config import Config


@dataclass
class Segment:
    """A single transcription segment with speaker info."""
    
    speaker: str
    start: float
    end: float
    text: str


@dataclass
class TranscriptResult:
    """Complete transcription result."""
    
    audio_path: Path
    language: str
    segments: List[Segment]


def format_time(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def transcribe_audio(audio_path: Path, config: Config) -> TranscriptResult:
    """
    Transcribe audio file with speaker diarization.
    
    Steps:
    0. Convert to M4A if needed (auto-detect format)
    1. Load WhisperX model
    2. Transcribe and detect language
    3. Align timestamps at word level
    4. Run speaker diarization
    5. Assign speakers to segments
    """
    
    import whisperx
    import gc
    from .audio_converter import convert_to_m4a, is_supported_audio
    
    print(f"\n{'='*60}")
    print(f"Processing: {audio_path.name}")
    print(f"{'='*60}")
    
    # Step 0: Convert to M4A if needed
    original_path = audio_path
    if audio_path.suffix.lower() != ".m4a":
        if not is_supported_audio(audio_path):
            raise ValueError(f"Unsupported audio format: {audio_path.suffix}")
        
        try:
            # Convert to M4A (will be saved in the same directory)
            audio_path = convert_to_m4a(
                audio_path,
                keep_original=True  # Keep original file
            )
        except Exception as e:
            print(f"❌ Audio conversion failed: {e}")
            raise
    
    # Step 1: Load model
    print(f"Loading WhisperX model ({config.model_size}) on {config.device}...")
    model = whisperx.load_model(
        config.model_size,
        config.device,
        compute_type=config.compute_type,
    )
    
    # Step 2: Transcribe (reduced batch_size for memory efficiency)
    print("Transcribing audio...")
    audio = whisperx.load_audio(str(audio_path))
    # Use smaller batch_size to avoid OOM on laptops
    batch_size = 4 if config.device == "cuda" else 8
    result = model.transcribe(audio, batch_size=batch_size)
    
    detected_language = result.get("language", "unknown")
    print(f"Detected language: {detected_language}")
    
    # Free up memory from transcription model
    del model
    gc.collect()
    if config.device == "cuda":
        torch.cuda.empty_cache()
    
    # Step 3: Align timestamps (optional, may fail for some languages)
    print("Aligning timestamps...")
    try:
        model_a, metadata = whisperx.load_align_model(
            language_code=detected_language,
            device=config.device,
        )
        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            config.device,
            return_char_alignments=False,
        )
        # Free up memory from alignment model
        del model_a
        gc.collect()
        if config.device == "cuda":
            torch.cuda.empty_cache()
    except Exception as e:
        print(f"⚠ Alignment skipped (model not available): {e}")
        print("  Continuing without word-level alignment...")
    
    # Step 4: Speaker diarization
    print("Running speaker diarization...")
    from whisperx.diarize import DiarizationPipeline
    diarize_model = DiarizationPipeline(
        use_auth_token=config.hf_token,
        device=config.device,
    )
    
    diarize_kwargs = {}
    if config.min_speakers is not None:
        diarize_kwargs["min_speakers"] = config.min_speakers
    if config.max_speakers is not None:
        diarize_kwargs["max_speakers"] = config.max_speakers
    
    diarize_segments = diarize_model(audio, **diarize_kwargs)
    
    # Free up memory from diarization model
    del diarize_model
    gc.collect()
    if config.device == "cuda":
        torch.cuda.empty_cache()
    
    # Step 5: Assign speakers
    print("Assigning speakers to segments...")
    result = whisperx.assign_word_speakers(diarize_segments, result)
    
    # Convert to our format
    segments = []
    for seg in result["segments"]:
        speaker = seg.get("speaker", "UNKNOWN")
        segments.append(Segment(
            speaker=speaker,
            start=seg["start"],
            end=seg["end"],
            text=seg["text"].strip(),
        ))
    
    # Merge consecutive segments from same speaker
    merged_segments = merge_speaker_segments(segments)
    
    print(f"✓ Transcription complete: {len(merged_segments)} segments")
    
    return TranscriptResult(
        audio_path=original_path,  # Use original path for output filename
        language=detected_language,
        segments=merged_segments,
    )


def merge_speaker_segments(segments: List[Segment]) -> List[Segment]:
    """Merge consecutive segments from the same speaker."""
    
    if not segments:
        return []
    
    merged = []
    current = segments[0]
    
    for seg in segments[1:]:
        if seg.speaker == current.speaker:
            # Merge with current
            current = Segment(
                speaker=current.speaker,
                start=current.start,
                end=seg.end,
                text=f"{current.text} {seg.text}",
            )
        else:
            merged.append(current)
            current = seg
    
    merged.append(current)
    return merged
