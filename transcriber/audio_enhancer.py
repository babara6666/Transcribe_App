"""Audio enhancement utilities for improving transcription quality."""

from pathlib import Path
import numpy as np
import soundfile as sf


def enhance_audio(
    audio_path: Path,
    output_path: Path = None,
    reduce_noise: bool = True,
    normalize: bool = True,
    sample_rate: int = 16000,
) -> Path:
    """
    Enhance audio file for better transcription quality.
    
    Args:
        audio_path: Input audio file path
        output_path: Output path (if None, creates temp file)
        reduce_noise: Apply noise reduction
        normalize: Normalize audio volume
        sample_rate: Target sample rate (16kHz for Whisper)
    
    Returns:
        Path to enhanced audio file
    """
    import noisereduce as nr
    from scipy import signal
    
    print(f"Enhancing audio: {audio_path.name}")
    
    # Load audio
    audio, sr = sf.read(str(audio_path))
    
    # Convert stereo to mono if needed
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
        print("  ✓ Converted stereo to mono")
    
    # Resample if needed
    if sr != sample_rate:
        num_samples = int(len(audio) * sample_rate / sr)
        audio = signal.resample(audio, num_samples)
        sr = sample_rate
        print(f"  ✓ Resampled to {sample_rate}Hz")
    
    # Noise reduction
    if reduce_noise:
        try:
            # Use first 1 second as noise profile
            noise_sample = audio[:sr]
            audio = nr.reduce_noise(
                y=audio,
                sr=sr,
                y_noise=noise_sample,
                stationary=True,
                prop_decrease=0.8,  # Reduce noise by 80%
            )
            print("  ✓ Noise reduction applied")
        except Exception as e:
            print(f"  ⚠ Noise reduction failed: {e}")
    
    # Normalize volume
    if normalize:
        # Peak normalization to -3dB
        peak = np.abs(audio).max()
        if peak > 0:
            target_peak = 0.7  # -3dB
            audio = audio * (target_peak / peak)
            print("  ✓ Volume normalized")
    
    # Apply high-pass filter to remove low-frequency rumble
    try:
        sos = signal.butter(4, 80, 'hp', fs=sr, output='sos')
        audio = signal.sosfilt(sos, audio)
        print("  ✓ High-pass filter applied (80Hz)")
    except Exception as e:
        print(f"  ⚠ Filter failed: {e}")
    
    # Save enhanced audio
    if output_path is None:
        output_path = audio_path.parent / f"{audio_path.stem}_enhanced.wav"
    
    sf.write(str(output_path), audio, sr)
    print(f"  ✓ Enhanced audio saved: {output_path.name}")
    
    return output_path


def quick_enhance(audio_path: Path) -> Path:
    """
    Quick enhancement with default settings.
    Creates a temporary enhanced file in the same directory.
    """
    return enhance_audio(
        audio_path,
        reduce_noise=True,
        normalize=True,
    )
