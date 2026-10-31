#!/usr/bin/env python3
"""
Reusable Dual-Host US Documentary Audio Builder (Cole + Maya)
- Cole (Male Lead Investigator): en-US-AndrewMultilingualNeural
- Maya (Female Co-Host & Analyst): en-US-AvaMultilingualNeural
Generates per-line neural speech, measures exact frame-accurate timestamps,
mixes subtle studio room tone / documentary bed, and normalizes to -16 LUFS.
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path
import edge_tts

VOICE_MAP = {
    "cole": "en-US-AndrewMultilingualNeural",
    "maya": "en-US-AvaMultilingualNeural",
}

RATE_MAP = {
    "cole": "+3%",
    "maya": "+4%",
}


def find_ffmpeg() -> str:
    local_ffmpeg = Path(
        "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"
    )
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    return "ffmpeg"


def find_ffprobe() -> str:
    local_ffprobe = Path(
        "node_modules/@remotion/compositor-win32-x64-msvc/ffprobe.exe"
    )
    if local_ffprobe.exists():
        return str(local_ffprobe)
    return "ffprobe"


def get_duration_sec(path: Path) -> float:
    cmd = [
        find_ffprobe(),
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    return float(out)


async def synthesize_dialogue_lines(
    lines: list[dict],
    tmp_dir: Path,
    pause_sec: float = 0.22,
) -> tuple[list[dict], Path]:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = find_ffmpeg()

    cues_out: list[dict] = []
    concat_entries: list[str] = []
    cursor_sec = 0.35

    # Leading 0.35s studio breath silence
    lead_sil = tmp_dir / "lead_silence.wav"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=48000:cl=stereo",
            "-t",
            "0.35",
            str(lead_sil),
        ],
        check=True,
        capture_output=True,
    )
    concat_entries.append(f"file '{lead_sil.resolve().as_posix()}'")

    gap_wav = tmp_dir / "gap_pause.wav"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=48000:cl=stereo",
            "-t",
            str(pause_sec),
            str(gap_wav),
        ],
        check=True,
        capture_output=True,
    )

    for idx, item in enumerate(lines):
        speaker = item["speaker"]
        text = item["text"]
        mp3_path = tmp_dir / f"line_{idx:04d}_{speaker}.mp3"
        wav_path = tmp_dir / f"line_{idx:04d}_{speaker}.wav"

        if not mp3_path.exists():
            comm = edge_tts.Communicate(
                text=text,
                voice=VOICE_MAP[speaker],
                rate=RATE_MAP[speaker],
            )
            await comm.save(str(mp3_path))

        # Clean 48kHz stereo broadcast conversion (compatible with Remotion's minimal ffmpeg build)
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(mp3_path),
                "-af",
                "aresample=48000,pan=stereo|c0=c0|c1=c0",
                str(wav_path),
            ],
            check=True,
            capture_output=True,
        )

        dur = get_duration_sec(wav_path)
        start_sec = round(cursor_sec, 3)
        end_sec = round(cursor_sec + dur, 3)

        cues_out.append(
            {
                "id": item.get("id", f"cue_{idx + 1:03d}"),
                "speaker": speaker,
                "startSec": start_sec,
                "endSec": end_sec,
                "text": text,
                "expression": item.get("expression", "neutral"),
            }
        )

        concat_entries.append(f"file '{wav_path.resolve().as_posix()}'")
        concat_entries.append(f"file '{gap_wav.resolve().as_posix()}'")
        cursor_sec = end_sec + pause_sec

    concat_txt = tmp_dir / "concat_list.txt"
    concat_txt.write_text("\n".join(concat_entries), encoding="utf-8")

    master_vo = tmp_dir / "dual_hosts_vo_raw.wav"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_txt),
            "-c:a",
            "pcm_s16le",
            str(master_vo),
        ],
        check=True,
        capture_output=True,
    )
    return cues_out, master_vo


def normalize_broadcast_mp3(input_wav: Path, output_mp3: Path) -> float:
    output_mp3.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = find_ffmpeg()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(input_wav),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-b:a",
            "320k",
            str(output_mp3),
        ],
        check=True,
        capture_output=True,
    )
    return get_duration_sec(output_mp3)


if __name__ == "__main__":
    print(
        "Dual-Host Audio Engine ready (Cole: en-US-AndrewMultilingualNeural | Maya: en-US-AvaMultilingualNeural)."
    )
