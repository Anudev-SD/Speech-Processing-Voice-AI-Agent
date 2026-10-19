"""Audio utilities for the Speech Interfaces & TTS practical.

What this module does
----------------------
Provides four things the rest of the package depends on:

1. ensure_parent_dir()  — creates the directory for any output file
2. measure_call()       — wraps any function call and records elapsed time
3. create_tone_wav()    — writes a simple sine-wave WAV (used by mock providers)
4. create_mock_speech_wav() — writes a sample input WAV for the demo pipeline
5. record_microphone_wav()  — optional: captures live mic input
6. play_audio_file()        — optional: plays a WAV/MP3 locally

Why audio_utils is a separate module
--------------------------------------
Every provider (STT, TTS, mock) and the voice agent itself needs file I/O and
timing. Centralising these helpers keeps the provider files focused on the
API call logic only.

How to run
-----------
These functions are never called directly. They are imported by other modules.
The smoke test (smoke_test.py) exercises them end-to-end.
"""

from __future__ import annotations

import math
import os
import struct
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar

import numpy as np


T = TypeVar("T")


@dataclass
class TimedResult:
    """Wraps a function's return value with elapsed time in milliseconds.

    Used throughout the pipeline to measure latency at each stage:
        timed = measure_call(stt_provider.transcribe, audio_path)
        print(f"STT took {timed.elapsed_ms:.0f} ms")
        transcript = timed.value
    """

    value: object
    elapsed_ms: float


def ensure_parent_dir(path: str | Path) -> Path:
    """Create the parent directory for a file path if it does not exist.

    All output files (TTS audio, rubric CSVs, logs) go into the outputs/
    folder. This function creates that folder automatically so callers do
    not need to mkdir before writing.

    Args:
        path: File path whose parent should exist.

    Returns:
        The resolved Path object, ready to be written to.
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path


def measure_call(func: Callable[..., T], *args, **kwargs) -> TimedResult:
    """Run a function and capture elapsed wall-clock time in milliseconds.

    Uses time.perf_counter() rather than time.time(). perf_counter() is
    the highest-resolution timer available on the platform and is not
    affected by system clock adjustments.

    Args:
        func:    Function to execute.
        *args:   Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        TimedResult with the original return value and elapsed milliseconds.

    Example:
        timed = measure_call(openai_tts.synthesize, text, output_path)
        print(f"TTS latency: {timed.elapsed_ms:.0f} ms")
        result = timed.value   # the TTSResult object
    """
    start = time.perf_counter()
    value = func(*args, **kwargs)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return TimedResult(value=value, elapsed_ms=elapsed_ms)


def audio_duration_seconds(path: str | Path) -> float:
    """Return the duration of a WAV file in seconds.

    Args:
        path: Path to a WAV file.

    Returns:
        Duration in seconds, calculated as frames / frame_rate.

    Raises:
        ValueError: If the file is not a readable WAV file.
    """
    with wave.open(str(path), "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        return frames / float(rate)


def create_tone_wav(
    output_path: str | Path,
    duration_seconds: float = 1.2,
    frequency_hz: float = 440.0,
    sample_rate: int = 16000,
) -> Path:
    """Write a pure sine-wave WAV file.

    Why this exists: mock TTS providers need to write a valid audio file so the
    pipeline can run end-to-end without any API keys. This function produces a
    playable WAV that proves the file path contract without spending money.

    The WAV format written:
        channels:    1 (mono)
        sample width: 2 bytes (16-bit PCM, signed little-endian)
        frame rate:  sample_rate (default 16000 Hz)

    Amplitude of 12000 out of a maximum of 32767 (16-bit) — audible but not
    clipping when played through most speakers.

    Args:
        output_path:      Destination WAV path.
        duration_seconds: Tone duration in seconds.
        frequency_hz:     Sine wave frequency (440 Hz = concert A).
        sample_rate:      Audio sample rate in Hz.

    Returns:
        Path to the generated WAV file.
    """
    output = ensure_parent_dir(output_path)
    amplitude = 12000
    with wave.open(str(output), "w") as wav_file:
        wav_file.setnchannels(1)     # mono
        wav_file.setsampwidth(2)     # 16-bit
        wav_file.setframerate(sample_rate)
        for i in range(int(duration_seconds * sample_rate)):
            # sin(2π × frequency × sample_index / sample_rate)
            # gives one full cycle of the sine wave per 1/frequency seconds
            sample = int(amplitude * math.sin(2 * math.pi * frequency_hz * i / sample_rate))
            # struct.pack("<h", sample) encodes as signed 16-bit little-endian
            wav_file.writeframes(struct.pack("<h", sample))
    return output


def create_mock_speech_wav(output_path: str | Path, text: str | None = None) -> Path:
    """Create a sample speech WAV for the practical.

    Tries to use the eSpeak text-to-speech engine if it is installed on the
    system. eSpeak is a lightweight offline synthesiser available on most
    Linux distributions and many macOS installs via Homebrew.

    If eSpeak is not found, falls back to create_tone_wav() so the demo
    can still run without any speech synthesis tool.

    This function is called by smoke_test.py and by app.py when the
    --input file does not yet exist.

    Args:
        output_path: Destination WAV path.
        text:        Sentence to synthesise. Defaults to a classroom-friendly question.

    Returns:
        Path to the sample audio file.
    """
    output = ensure_parent_dir(output_path)
    sentence = text or (
        "Can you explain in simple words how text to speech works for an AI assistant?"
    )

    import shutil
    import subprocess

    if shutil.which("espeak"):
        # espeak -w <output> <text> writes a WAV file of the spoken text.
        # This produces real speech, not a tone — useful for STT testing.
        subprocess.run(["espeak", "-w", str(output), sentence], check=True)
        return output

    # espeak not available — write a tone so the demo can still proceed.
    return create_tone_wav(output)


def record_microphone_wav(
    output_path: str | Path,
    duration_seconds: float = 5.0,
    sample_rate: int = 16000,
) -> Path:
    """Record live microphone audio into a WAV file.

    This is an optional classroom feature. In live demos, OS microphone
    permissions and browser/OS conflicts often prevent this from working
    reliably. Always have the sample_voice_question.wav fallback ready.

    Requires:
        pip install sounddevice soundfile  (included in requirements.txt)
        OS microphone permissions granted to Python/Terminal

    Args:
        output_path:      Destination WAV path.
        duration_seconds: Number of seconds to record.
        sample_rate:      Audio sample rate (16000 Hz is standard for STT).

    Returns:
        Path to recorded audio.

    Raises:
        RuntimeError: If sounddevice or soundfile is not available, or if
                      no input device is accessible.
    """
    output = ensure_parent_dir(output_path)

    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "Microphone recording requires sounddevice and soundfile. "
            "Both are in requirements.txt. Also check OS microphone permissions."
        ) from exc

    print(f"Recording for {duration_seconds:.1f} seconds. Speak now...")
    # sd.rec() starts a non-blocking recording. sd.wait() blocks until done.
    audio = sd.rec(
        int(duration_seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,       # mono — STT models expect a single clean channel
        dtype="float32",  # float32 internal, sf.write converts to WAV format
    )
    sd.wait()
    sf.write(str(output), audio, sample_rate)
    print(f"Saved recording to {output}")
    return output


def play_audio_file(path: str | Path) -> None:
    """Play an audio file through the system speakers.

    In Jupyter notebooks, use IPython.display.Audio instead — it works
    in any environment including remote servers and cloud notebooks.

    This function is for local script demos where a notebook display is
    not available.

    Args:
        path: Path to a WAV or MP3 file. WAV is most reliable.

    Raises:
        RuntimeError: If sounddevice/soundfile are unavailable or no
                      output device is accessible.
    """
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "Local playback requires sounddevice and soundfile. "
            "In notebooks, use IPython.display.Audio instead."
        ) from exc

    data, sample_rate = sf.read(str(path), dtype="float32")
    sd.play(data, sample_rate)
    sd.wait()
