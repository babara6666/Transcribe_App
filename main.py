#!/usr/bin/env python3
"""
Auto-Transcriber with Speaker Diarization

自動化會議錄音轉錄系統
使用 WhisperX + Pyannote.audio 實現語音轉文字與講者區分
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from transcriber import (
    load_config,
    get_pending_files,
    transcribe_audio,
    save_markdown,
)


def main():
    parser = argparse.ArgumentParser(
        description="自動化會議錄音轉錄系統 (Auto-Transcriber with Diarization)"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        help="Override watch directory from .env",
    )
    parser.add_argument(
        "--model",
        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
        help="Override Whisper model size",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Process a single file instead of scanning directory",
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("Auto-Transcriber with Speaker Diarization")
    print("=" * 60)
    print()
    
    # Load configuration
    try:
        config = load_config()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Apply CLI overrides
    if args.dir:
        config.watch_dir = args.dir
        config.output_dir = args.dir
    if args.model:
        config.model_size = args.model
    
    print(f"Watch directory: {config.watch_dir}")
    print(f"Model: {config.model_size}")
    print(f"Device: {config.device} ({config.compute_type})")
    print()
    
    # Get files to process
    if args.file:
        if not args.file.exists():
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        pending_files = [args.file]
    else:
        pending_files = get_pending_files(
            config.watch_dir,
            config.output_dir,
        )
    
    if not pending_files:
        print("No files to process.")
        return
    
    # Process each file
    success_count = 0
    error_count = 0
    
    for audio_path in pending_files:
        try:
            timestamp = datetime.now()
            result = transcribe_audio(audio_path, config)
            save_markdown(result, config.output_dir, timestamp)
            success_count += 1
        except Exception as e:
            print(f"❌ Error processing {audio_path.name}: {e}")
            error_count += 1
    
    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✓ Successfully processed: {success_count}")
    if error_count > 0:
        print(f"✗ Errors: {error_count}")


if __name__ == "__main__":
    main()
