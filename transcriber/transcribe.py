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


def enhance_audio_array(audio: 'np.ndarray', sample_rate: int = 16000) -> 'np.ndarray':
    """
    Enhance audio array in-memory for better transcription quality.
    
    Args:
        audio: Audio array (numpy)
        sample_rate: Sample rate (default 16kHz for Whisper)
    
    Returns:
        Enhanced audio array
    """
    import numpy as np
    import noisereduce as nr
    from scipy import signal
    
    print("  Applying audio enhancement...")
    
    # Noise reduction using first 1 second as noise profile
    try:
        noise_sample = audio[:sample_rate]
        audio = nr.reduce_noise(
            y=audio,
            sr=sample_rate,
            y_noise=noise_sample,
            stationary=True,
            prop_decrease=0.7,  # Reduce noise by 70%
        )
        print("    ✓ Noise reduction")
    except Exception:
        pass
    
    # Normalize volume (peak normalization to -3dB)
    peak = np.abs(audio).max()
    if peak > 0:
        target_peak = 0.7
        audio = audio * (target_peak / peak)
        print("    ✓ Volume normalized")
    
    # High-pass filter to remove low-frequency rumble
    try:
        sos = signal.butter(4, 80, 'hp', fs=sample_rate, output='sos')
        audio = signal.sosfilt(sos, audio)
        print("    ✓ High-pass filter (80Hz)")
    except Exception:
        pass
    
    # Ensure float32 for WhisperX compatibility
    return audio.astype(np.float32)


def transcribe_audio(
    audio_path: Path, 
    config: Config,
    chunk_duration: int = 180,  # seconds per chunk (3 minutes)
    overlap_duration: int = 0,  # seconds overlap between chunks
    allowed_languages: tuple = ("zh", "en"),  # only allow these languages
    enhance_audio: bool = True,  # apply audio enhancement (default: on)
) -> TranscriptResult:
    """
    Transcribe audio file with speaker diarization.
    
    Args:
        audio_path: Path to audio file
        config: Configuration object
        chunk_duration: Duration of each chunk in seconds (default 60s)
        overlap_duration: Overlap between chunks in seconds (default 5s)
        allowed_languages: Tuple of allowed language codes (default: Chinese, English)
        enhance_audio: Apply noise reduction and normalization (default: False)
    
    Steps:
    0. (Optional) Enhance audio quality
    1. Load WhisperX model
    2. Transcribe in chunks with overlap
    3. Align timestamps at word level
    4. Run speaker diarization
    5. Assign speakers to segments
    """
    
    import whisperx
    import gc
    import numpy as np
    
    print(f"\n{'='*60}")
    print(f"Processing: {audio_path.name}")
    print(f"{'='*60}")
    
    # Step 1: Load model
    print(f"Loading WhisperX model ({config.model_size}) on {config.device}...")
    model = whisperx.load_model(
        config.model_size,
        config.device,
        compute_type=config.compute_type,
    )
    
    # Step 2: Load and optionally enhance audio
    print("Loading audio...")
    audio = whisperx.load_audio(str(audio_path))
    
    # Optional: apply audio enhancement in-memory
    if enhance_audio:
        try:
            audio = enhance_audio_array(audio, sample_rate=16000)
            print("✓ Audio enhancement applied")
        except Exception as e:
            print(f"⚠ Audio enhancement failed: {e}")
    sample_rate = 16000  # WhisperX uses 16kHz
    total_samples = len(audio)
    total_duration = total_samples / sample_rate
    
    batch_size = 4 if config.device == "cuda" else 8
    
    # Decide whether to use chunked transcription
    if total_duration > chunk_duration * 1.5:
        print(f"Using chunked transcription ({chunk_duration}s chunks, {overlap_duration}s overlap)...")
        result = transcribe_chunked(
            model, audio, sample_rate, 
            chunk_duration, overlap_duration, 
            batch_size, allowed_languages
        )
    else:
        print("Transcribing audio (single pass)...")
        result = model.transcribe(audio, batch_size=batch_size)
    
    detected_language = result.get("language", "unknown")
    
    # Filter language for single-pass mode
    if detected_language not in allowed_languages:
        detected_language = infer_language_from_text(result.get("segments", []), allowed_languages)
    
    print(f"Primary language: {detected_language}")
    
    # Free up memory from transcription model
    del model
    gc.collect()
    if config.device == "cuda":
        torch.cuda.empty_cache()
    
    # Step 3: Align timestamps
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
        print(f"⚠ Alignment failed: {e}")
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
        audio_path=audio_path,
        language=detected_language,
        segments=merged_segments,
    )


def transcribe_chunked(
    model,
    audio,
    sample_rate: int,
    chunk_duration: int,
    overlap_duration: int,
    batch_size: int,
    allowed_languages: tuple,
) -> dict:
    """
    Transcribe audio in chunks with overlap for better context.
    
    Args:
        model: WhisperX model
        audio: Audio array
        sample_rate: Sample rate (16000 for WhisperX)
        chunk_duration: Duration of each chunk in seconds
        overlap_duration: Overlap between chunks in seconds
        batch_size: Batch size for transcription
        allowed_languages: Allowed language codes
    
    Returns:
        dict with 'segments' and 'language'
    """
    import numpy as np
    from collections import Counter
    
    total_samples = len(audio)
    chunk_samples = chunk_duration * sample_rate
    overlap_samples = overlap_duration * sample_rate
    step_samples = chunk_samples - overlap_samples
    
    all_segments = []
    language_counter = Counter()
    
    # Calculate number of chunks
    num_chunks = max(1, int(np.ceil((total_samples - overlap_samples) / step_samples)))
    print(f"  Splitting into {num_chunks} chunks ({chunk_duration}s each, {overlap_duration}s overlap)...")
    
    for i in range(num_chunks):
        start_sample = i * step_samples
        end_sample = min(start_sample + chunk_samples, total_samples)
        chunk_audio = audio[start_sample:end_sample]
        
        start_time = start_sample / sample_rate
        end_time = end_sample / sample_rate
        
        print(f"  Chunk {i+1}/{num_chunks} [{format_time(start_time)} - {format_time(end_time)}]...")
        
        # Transcribe this chunk
        chunk_result = model.transcribe(chunk_audio, batch_size=batch_size)
        chunk_lang = chunk_result.get("language", "unknown")
        
        # Language filtering
        if chunk_lang not in allowed_languages:
            # Infer from text content
            chunk_lang = infer_language_from_text(
                chunk_result.get("segments", []), 
                allowed_languages
            )
            print(f"    Language: corrected to {chunk_lang}")
        else:
            print(f"    Language: {chunk_lang}")
        
        language_counter[chunk_lang] += 1
        
        # Adjust timestamps and filter overlap region
        for seg in chunk_result.get("segments", []):
            # Adjust to global timeline
            seg_start = seg["start"] + start_time
            seg_end = seg["end"] + start_time
            
            # Skip segments in overlap region (except first chunk)
            if i > 0 and seg_start < (start_time + overlap_duration):
                continue
            
            seg["start"] = seg_start
            seg["end"] = seg_end
            seg["language"] = chunk_lang
            all_segments.append(seg)
    
    # Determine primary language
    primary_language = language_counter.most_common(1)[0][0] if language_counter else "unknown"
    
    return {
        "segments": all_segments,
        "language": primary_language,
    }


def infer_language_from_text(segments: list, allowed_languages: tuple) -> str:
    """
    Infer language from transcribed text based on character analysis.
    
    Returns the most likely language from allowed_languages.
    """
    text = " ".join([seg.get("text", "") for seg in segments])
    
    if not text.strip():
        return allowed_languages[0] if allowed_languages else "unknown"
    
    # Count character types
    latin_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    cjk_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')  # CJK range
    total_alpha = latin_chars + cjk_chars
    
    if total_alpha == 0:
        return allowed_languages[0]
    
    # If mostly Latin → English, else Chinese
    if "en" in allowed_languages and latin_chars / total_alpha > 0.6:
        return "en"
    elif "zh" in allowed_languages:
        return "zh"
    else:
        return allowed_languages[0]


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
