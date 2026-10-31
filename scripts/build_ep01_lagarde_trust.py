#!/usr/bin/env python3
"""
Episode 01 Full Production Builder:
"Why Europe's Central Bank Chief Just Quit Early (And the Wild Conspiracy Hiding the Real Move)"
-----------------------------------------------------------------------------------------------
1. Acquires & normalizes 100% REAL video footage & archival photographs into public/episodes/ep01_lagarde/
2. Synthesizes dual-host US English neural narration (Cole + Maya) with frame-accurate timestamps
3. Mixes subtle dark investigative studio ambience under -16 LUFS broadcast master audio
4. Emits deterministic RealEpisodeManifest JSON -> src/realshow/ep01LagardeManifest.json
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_dual_host_audio import (  # noqa: E402
    find_ffmpeg,
    find_ffprobe,
    get_duration_sec,
    synthesize_dialogue_lines,
)
from research_real_media import (  # noqa: E402
    USER_AGENT,
    auto_trim_black_borders,
    fetch_and_normalize_video,
    fetch_and_verify_photo,
)

EP_PUBLIC = ROOT / "public" / "episodes" / "ep01_lagarde"
TMP_AUDIO = ROOT / ".tmp_ep01_audio"
MANIFEST_OUT = ROOT / "src" / "realshow" / "ep01LagardeManifest.json"
USER_MEME_SRC = Path(
    r"C:\Users\samet\.gemini\antigravity\brain\e57e62f5-9fc2-4891-8f31-a49a4304d4d5\.user_uploaded\media_1793442909997_bca94534.png"
)


def fetch_lagarde_vertical_video(url: str, out_mp4: Path, poster_jpg: Path) -> None:
    """Downloads Lagarde's Oct 29, 2026 9:16 announcement video and encodes 608x1080 30fps H.264."""
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = find_ffmpeg()

    if not out_mp4.exists():
        raw_tmp = out_mp4.with_suffix(".raw_dl.mp4")
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=90) as resp, open(raw_tmp, "wb") as f:
            while True:
                chunk = resp.read(1024 * 512)
                if not chunk:
                    break
                f.write(chunk)
        try:
            cmd = [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-i",
                str(raw_tmp),
                "-t",
                "32",
                "-vf",
                "scale=608:1080:force_original_aspect_ratio=decrease,format=yuv420p",
                "-r",
                "30",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "19",
                "-g",
                "15",
                "-movflags",
                "+faststart",
                str(out_mp4),
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if proc.returncode != 0:
                raise RuntimeError(f"Vertical encode failed:\n{proc.stderr}")
        finally:
            if raw_tmp.exists():
                raw_tmp.unlink()

    if not poster_jpg.exists():
        # Extract crisp frame showing Lagarde, facial bandage, lapel mic, and credenza owl
        raw_png = poster_jpg.with_suffix(".tmp.png")
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-ss",
                "4.2",
                "-i",
                str(out_mp4),
                "-frames:v",
                "1",
                str(raw_png),
            ],
            check=True,
            capture_output=True,
        )
        im = Image.open(raw_png).convert("RGB")
        # Crop upper-middle 4:3 region of 608x1080 so split-screen card frames her upper torso & background cleanly
        w, h = im.size
        crop_im = im.crop((0, int(h * 0.10), w, int(h * 0.72))).resize(
            (1200, 1220), Image.Resampling.LANCZOS
        )
        crop_im.save(poster_jpg, quality=94)
        raw_png.unlink()


def prepare_viral_claim_screenshot(out_jpg: Path) -> None:
    if out_jpg.exists() or not USER_MEME_SRC.exists():
        return
    im = Image.open(USER_MEME_SRC).convert("RGB")
    rgb = auto_trim_black_borders(np.asarray(im, dtype=np.uint8), lum_thresh=16.0)
    clean = Image.fromarray(rgb, mode="RGB")
    clean.save(out_jpg, quality=93)


def acquire_all_real_media() -> None:
    EP_PUBLIC.mkdir(parents=True, exist_ok=True)
    print("[1/4] Acquiring & normalizing 100% REAL videos and archival photographs...")

    # 1. Lagarde Oct 29, 2026 Official Video + Poster
    fetch_lagarde_vertical_video(
        "https://video.twimg.com/amplify_video/2115746030067027968/vid/avc1/1080x1920/kOZt-5Q1prUFw---.mp4?tag=29",
        EP_PUBLIC / "lagarde_exit_2026_9x16.mp4",
        EP_PUBLIC / "lagarde_exit_poster.jpg",
    )
    print("  [ok] lagarde_exit_2026_9x16.mp4 + lagarde_exit_poster.jpg")

    # 2. Viral Red-Box Screenshot Exhibit
    prepare_viral_claim_screenshot(EP_PUBLIC / "viral_redbox_claim.jpg")
    print("  [ok] viral_redbox_claim.jpg")

    # 3. Real 1080p Frankfurt Financial Skyline Video (RED Epic Cinema Source)
    fk_vid = EP_PUBLIC / "frankfurt_skyline_1080p.mp4"
    if not fk_vid.exists():
        fetch_and_normalize_video(
            "https://upload.wikimedia.org/wikipedia/commons/3/38/5k-resolution_video_of_Frankfurt%2C_Germany_2014-02-02.webm",
            fk_vid,
            start_sec=2.0,
            duration_sec=14.0,
        )
    print("  [ok] frankfurt_skyline_1080p.mp4")

    # 4. Authentic Early Soviet Archival Film Reel (Dziga Vertov Public Domain)
    sov_vid = EP_PUBLIC / "soviet_1920s_reel_1080p.mp4"
    if not sov_vid.exists():
        fetch_and_normalize_video(
            "https://upload.wikimedia.org/wikipedia/commons/7/76/DJ_Spooky_presents_Vertov_Enthusiasm-_Sinfonia_Donbassa_%28beta%29.webm",
            sov_vid,
            start_sec=38.0,
            duration_sec=15.0,
        )
    print("  [ok] soviet_1920s_reel_1080p.mp4")

    # 5. Verified Archival & Official Photographs
    photos = [
        (
            "lagarde_eu_2025.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d6/Visit_of_Christine_Lagarde%2C_President_of_the_European_Central_Bank_%28ECB%29%2C_to_the_European_Commission_%28P-067330-00-01%29.jpg/1920px-Visit_of_Christine_Lagarde%2C_President_of_the_European_Central_Bank_%28ECB%29%2C_to_the_European_Commission_%28P-067330-00-01%29.jpg",
            900,
        ),
        (
            "ecb_frankfurt_hq.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/75/Europ%C3%A4ische_Zentralbank_Frankfurt.jpg/1920px-Europ%C3%A4ische_Zentralbank_Frankfurt.jpg",
            900,
        ),
        (
            "lagarde_parliament.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/2/22/Christine_Lagarde%2C_2023.jpg",
            800,
        ),
        (
            "athena_owl_coin.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/33/Silver_corithian_tetradrachm_with_owl_and_athena_%285431942080%29.jpg/1920px-Silver_corithian_tetradrachm_with_owl_and_athena_%285431942080%29.jpg",
            900,
        ),
        (
            "macron_eu_summit_2025.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/85/Emmanuel_Macron%2C_2025.03.06_%2803%29.jpg/1920px-Emmanuel_Macron%2C_2025.03.06_%2803%29.jpg",
            900,
        ),
        (
            "marine_le_pen_2026.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/53/Marine_Le_Pen_-.jpg/1920px-Marine_Le_Pen_-.jpg",
            800,
        ),
        (
            "dzerzhinsky_1926.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/74/Dzerzhinsky_0-263693.jpg/1920px-Dzerzhinsky_0-263693.jpg",
            900,
        ),
        (
            "lubyanka_hq_moscow.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e3/Lubyanka_Building.jpg/1920px-Lubyanka_Building.jpg",
            900,
        ),
        (
            "savinkov_trial_1924.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/fc/Boris_Savinkov_on_trial%2C_1924.jpg/1920px-Boris_Savinkov_on_trial%2C_1924.jpg",
            900,
        ),
        (
            "sidney_reilly_passport_1918.jpg",
            "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2f/Sidney_Reilly_German_Passport_September_1918.jpg/330px-Sidney_Reilly_German_Passport_September_1918.jpg",
            320,
        ),
    ]

    for fname, url, min_w in photos:
        dest = EP_PUBLIC / fname
        if not dest.exists():
            fetch_and_verify_photo(url, dest, min_width=min_w)
        print(f"  [ok] {fname}")


# ============================================================================
# EPISODE 01 SCRIPT — 34 CRISP INVESTIGATIVE DIALOGUE CUES (COLE & MAYA)
# ============================================================================
DIALOGUE_SCRIPT: list[dict[str, Any]] = [
    # --- ACT I: THE 15-MILLION-VIEW EXIT VIDEO ---
    {
        "id": "c01",
        "speaker": "cole",
        "expression": "serious",
        "text": "On October twenty-ninth, one of the most powerful central bankers on Earth posted a forty-five-second video that stopped global markets cold.",
    },
    {
        "id": "c02",
        "speaker": "maya",
        "expression": "curious",
        "text": "European Central Bank President Christine Lagarde announced she is stepping down on February seventh, twenty twenty-seven — nearly nine months before her term actually ends.",
    },
    {
        "id": "c03",
        "speaker": "cole",
        "expression": "emphatic",
        "text": "Almost fifteen million people watched that clip within forty-eight hours. Not because of monetary policy — because of how it looked.",
    },
    {
        "id": "c04",
        "speaker": "maya",
        "expression": "skeptical",
        "text": "Surgical bandages across her left cheek. A wired lapel mic hanging outside her collar. And a tiny owl figurine sitting on the cabinet behind her.",
    },
    {
        "id": "c05",
        "speaker": "cole",
        "expression": "serious",
        "text": "Within hours, viral threads were calling it a coded hostage video — claiming secret operatives had seized Europe's central bank from the inside.",
    },
    {
        "id": "c06",
        "speaker": "maya",
        "expression": "emphatic",
        "text": "Except when we pulled the primary records, we found two completely different stories: a viral fantasy that falls apart in sixty seconds, and a real political power play hiding in plain sight.",
    },
    # --- ACT II: FORENSICS ON THE VIRAL CLAIMS ---
    {
        "id": "c07",
        "speaker": "cole",
        "expression": "curious",
        "text": "Let's start with the viral screenshot itself — nearly eight hundred thousand views on a single post dissecting every pixel behind Lagarde's shoulder.",
    },
    {
        "id": "c08",
        "speaker": "maya",
        "expression": "skeptical",
        "text": "Online code-hunters counted seventeen pearls on her necklace, drew red boxes around clouds in her painting, and claimed the bandages were proof of forced submission.",
    },
    {
        "id": "c09",
        "speaker": "cole",
        "expression": "serious",
        "text": "What none of those viral screenshots included was the timestamped reply Lagarde posted literally thirty-two seconds after her video went live.",
    },
    {
        "id": "c10",
        "speaker": "maya",
        "expression": "neutral",
        "text": "At ten-oh-three UTC, she wrote directly that the plasters came from a minor skin-cancer removal earlier that week, joking to staff she hadn't been kickboxing in Thailand.",
    },
    {
        "id": "c11",
        "speaker": "cole",
        "expression": "curious",
        "text": "Okay, fair enough on the bandage. What about that owl statue on her credenza that threads linked to secret California rituals?",
    },
    {
        "id": "c12",
        "speaker": "maya",
        "expression": "emphatic",
        "text": "That's the funniest part. When Lagarde took over the European Central Bank in twenty nineteen, reporters asked if she was an inflation hawk or a stimulus dove.",
    },
    {
        "id": "c13",
        "speaker": "cole",
        "expression": "shocked",
        "text": "And she told the entire press corps on camera: 'I am neither a hawk nor a dove — I am an owl,' referencing Athena's ancient symbol of wisdom.",
    },
    {
        "id": "c14",
        "speaker": "maya",
        "expression": "skeptical",
        "text": "Visiting diplomats have gifted her ceramic owls for seven straight years. It wasn't a hidden hostage prop — it's literally her public nickname.",
    },
    # --- ACT III: THE REAL 2027 FRENCH ELECTION CHESS MOVE ---
    {
        "id": "c15",
        "speaker": "cole",
        "expression": "emphatic",
        "text": "Which brings us to the real question nobody counting pearls bothered to ask: why resign on February seventh, twenty twenty-seven instead of October?",
    },
    {
        "id": "c16",
        "speaker": "maya",
        "expression": "serious",
        "text": "Pull up the European political calendar, and those nine months change who controls the world's second-largest reserve currency for the next eight years.",
    },
    {
        "id": "c17",
        "speaker": "cole",
        "expression": "serious",
        "text": "In April twenty twenty-seven — just eight weeks after Lagarde's new exit date — France holds its next presidential election.",
    },
    {
        "id": "c18",
        "speaker": "maya",
        "expression": "curious",
        "text": "President Emmanuel Macron is constitutionally barred from running for a third consecutive term, and nationalist challenger Marine Le Pen has led national polling.",
    },
    {
        "id": "c19",
        "speaker": "cole",
        "expression": "emphatic",
        "text": "Under European Union treaties, the next Central Bank President is chosen by eurozone heads of state for a non-renewable eight-year mandate.",
    },
    {
        "id": "c20",
        "speaker": "maya",
        "expression": "serious",
        "text": "If Lagarde waited until October twenty twenty-seven, Paris could have a eurosceptic president sitting at the summit table with veto leverage over her replacement.",
    },
    {
        "id": "c21",
        "speaker": "cole",
        "expression": "neutral",
        "text": "By stepping aside in February, Macron and Berlin get to lock in the next central bank chief through twenty thirty-five before a single French ballot is cast.",
    },
    {
        "id": "c22",
        "speaker": "maya",
        "expression": "emphatic",
        "text": "No secret blackouts. No hidden morse code. Just hard institutional chess played out in broad daylight.",
    },
    # --- ACT IV: THE 1921 SOVIET SPY PARALLEL (OPERATION TRUST) ---
    {
        "id": "c23",
        "speaker": "cole",
        "expression": "curious",
        "text": "And yet hundreds of thousands of people preferred the hostage myth — the comforting idea that secret insiders are quietly fixing everything behind the curtain.",
    },
    {
        "id": "c24",
        "speaker": "maya",
        "expression": "serious",
        "text": "Intelligence historians actually have a name for that exact psychological trap. Because in nineteen twenty-one, Moscow built an entire spy operation around it.",
    },
    {
        "id": "c25",
        "speaker": "cole",
        "expression": "serious",
        "text": "After the Russian Civil War, Soviet secret police chief Felix Dzerzhinsky faced thousands of anti-Bolshevik exiles in Paris, Berlin, and London plotting to topple his regime.",
    },
    {
        "id": "c26",
        "speaker": "maya",
        "expression": "emphatic",
        "text": "Instead of hunting them abroad, Dzerzhinsky's counterintelligence headquarters at Lubyanka invented a fake patriotic underground inside Russia — code-named Operation Trust.",
    },
    {
        "id": "c27",
        "speaker": "cole",
        "expression": "curious",
        "text": "Soviet double agents traveled to Western capitals whispering one seductive message to dissidents and British intelligence: stand down and trust the plan.",
    },
    {
        "id": "c28",
        "speaker": "maya",
        "expression": "skeptical",
        "text": "They claimed secret patriots had already infiltrated Moscow's ministries, so any real resistance from the outside would only ruin the operation.",
    },
    {
        "id": "c29",
        "speaker": "cole",
        "expression": "shocked",
        "text": "It worked with devastating precision. In nineteen twenty-four, exiled resistance leader Boris Savinkov was lured back into Moscow by Trust operatives and arrested on arrival.",
    },
    {
        "id": "c30",
        "speaker": "maya",
        "expression": "serious",
        "text": "A year later, legendary British MI6 spy Sidney Reilly crossed the border to meet the fake underground council — walking straight into a Lubyanka cell.",
    },
    {
        "id": "c31",
        "speaker": "cole",
        "expression": "emphatic",
        "text": "By the time a defector exposed Operation Trust in nineteen twenty-seven, six years had passed, real opposition was paralyzed, and state power was cemented.",
    },
    {
        "id": "c32",
        "speaker": "maya",
        "expression": "skeptical",
        "text": "A century later, you don't even need an intelligence agency to run that playbook. Viral algorithms generate the exact same lullaby for clicks.",
    },
    {
        "id": "c33",
        "speaker": "cole",
        "expression": "serious",
        "text": "Every time a rumor promises ten days of darkness or secret saviors behind a pearl necklace, it trains millions of citizens to watch shadows instead of treaties.",
    },
    {
        "id": "c34",
        "speaker": "maya",
        "expression": "emphatic",
        "text": "Because in the real world, power doesn't hide in cloud paintings. It moves on February seventh, right on the official calendar. See you on the next investigation.",
    },
]


def mix_episode_master_audio(vo_wav: Path, out_mp3: Path) -> float:
    """Mixes subtle dark broadcast room ambience under Cole & Maya and normalizes to -16 LUFS."""
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = find_ffmpeg()
    vo_dur = get_duration_sec(vo_wav)
    total_dur = round(vo_dur + 0.9, 2)

    # Generate subtle dark 55Hz + 110Hz studio documentary drone bed via enabled 'sine' + 'volume' + 'amix' filters
    bed_wav = TMP_AUDIO / "doc_ambient_bed.wav"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=55:sample_rate=48000:duration={total_dur}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=82.4:sample_rate=48000:duration={total_dur}",
            "-filter_complex",
            "[0:a]volume=0.014[a0];[1:a]volume=0.008[a1];[a0][a1]amix=inputs=2:duration=longest,aformat=channel_layouts=stereo",
            str(bed_wav),
        ],
        check=True,
        capture_output=True,
    )

    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-i",
            str(vo_wav),
            "-i",
            str(bed_wav),
            "-filter_complex",
            "[0:a]apad=pad_dur=0.9[vo];[vo][1:a]amix=inputs=2:duration=first:weights=1 0.35,loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-b:a",
            "320k",
            str(out_mp3),
        ],
        check=True,
        capture_output=True,
    )
    return get_duration_sec(out_mp3)


def build_manifest(cues: list[dict[str, Any]], total_dur: float) -> dict[str, Any]:
    """Maps measured cue timestamps to 21 dynamic studio + 100% real-media broadcast shots."""
    by_id = {c["id"]: c for c in cues}

    def span(first_id: str, last_id: str, is_first: bool = False, is_last: bool = False) -> tuple[float, float]:
        s = 0.0 if is_first else round(by_id[first_id]["startSec"] - 0.11, 3)
        e = round(total_dur, 3) if is_last else round(by_id[last_id]["endSec"] + 0.11, 3)
        return s, e

    # Ensure contiguous gapless shot timeline from 0.0 -> total_dur
    shot_defs: list[tuple[str, str, dict[str, Any]]] = [
        (
            "c01",
            "c01",
            {
                "id": "s01_studio_cold_open",
                "layout": "studio_dual",
                "monitorMediaPath": "episodes/ep01_lagarde/lagarde_exit_poster.jpg",
                "locationDate": "FRANKFURT · OCT 29, 2026",
                "headline": "SURPRISE EARLY EXIT AT EUROPE'S CENTRAL BANK",
            },
        ),
        (
            "c02",
            "c03",
            {
                "id": "s02_lagarde_real_video",
                "layout": "real_video_pip",
                "mediaPath": "episodes/ep01_lagarde/lagarde_exit_2026_9x16.mp4",
                "verticalSocialVideo": True,
                "videoTrimStartSec": 0.5,
                "pipHost": "maya",
                "sourceTag": "OFFICIAL STATEMENT · @LAGARDE",
                "locationDate": "OCT 29, 2026 · 14.7M VIEWS",
                "headline": "STEPPING DOWN FEB 7, 2027 (9 MONTHS EARLY)",
            },
        ),
        (
            "c04",
            "c04",
            {
                "id": "s03_lagarde_video_closeup",
                "layout": "real_video_pip",
                "mediaPath": "episodes/ep01_lagarde/lagarde_exit_2026_9x16.mp4",
                "verticalSocialVideo": True,
                "videoTrimStartSec": 11.0,
                "pipHost": "maya",
                "sourceTag": "PRIMARY VIDEO RECORD · ECB",
                "locationDate": "FRANKFURT AM MAIN",
                "headline": "BANDAGES, EXPOSED MIC CORD & DESK OWL",
            },
        ),
        (
            "c05",
            "c06",
            {
                "id": "s04_studio_thesis",
                "layout": "studio_dual",
                "monitorMediaPath": "episodes/ep01_lagarde/ecb_frankfurt_hq.jpg",
                "locationDate": "MANHATTAN STUDIO · INVESTIGATION",
                "headline": "VIRAL FANTASY VS. REAL CENTRAL BANK CHESS",
            },
        ),
        (
            "c07",
            "c08",
            {
                "id": "s05_viral_redbox_split",
                "layout": "real_split_evidence",
                "mediaPath": "episodes/ep01_lagarde/viral_redbox_claim.jpg",
                "pipHost": "cole",
                "sourceTag": "VIRAL THREAD · OCT 30, 2026 (783K VIEWS)",
                "headline": "THE VIRAL 'CODED HOSTAGE VIDEO' CLAIMS",
                "facts": [
                    {
                        "label": "VIRAL CLAIM #1",
                        "value": "Facial Bandage & '17 Pearls' = Secret Arrest Signal",
                        "accent": "red",
                    },
                    {
                        "label": "VIRAL CLAIM #2",
                        "value": "Desk Owl & Cloud Painting = Hidden Ritual Message",
                        "accent": "amber",
                    },
                ],
                "notes": [
                    "Within 24 hours, posts across Europe and the U.S. framed a central bank resignation as a covert military takeover.",
                ],
            },
        ),
        (
            "c09",
            "c10",
            {
                "id": "s06_surgery_receipt_split",
                "layout": "real_split_evidence",
                "mediaPath": "episodes/ep01_lagarde/lagarde_exit_poster.jpg",
                "pipHost": "maya",
                "sourceTag": "TIMESTAMPED REPLY · +32 SECONDS",
                "headline": "FACT CHECK #1: THE 32-SECOND MEDICAL RECEIPT",
                "facts": [
                    {
                        "label": "VIDEO POSTED (UTC)",
                        "value": "Oct 29, 2026 · 10:03:07 AM (@Lagarde)",
                        "accent": "cyan",
                    },
                    {
                        "label": "MEDICAL NOTE POSTED",
                        "value": "10:03:39 AM — Minor Skin-Cancer Procedure",
                        "accent": "amber",
                    },
                ],
                "notes": [
                    "Lagarde publicly explained the surgical plasters half a minute after posting — urging viewers to get regular skin checks.",
                ],
            },
        ),
        (
            "c11",
            "c11",
            {
                "id": "s07_studio_cole_owl_question",
                "layout": "studio_solo_cole",
                "monitorMediaPath": "episodes/ep01_lagarde/athena_owl_coin.jpg",
                "locationDate": "EVIDENCE CHECK · SYMBOLISM",
                "headline": "WHY IS THERE AN OWL ON HER CREDENZA?",
            },
        ),
        (
            "c12",
            "c14",
            {
                "id": "s08_athena_owl_split",
                "layout": "real_split_evidence",
                "mediaPath": "episodes/ep01_lagarde/athena_owl_coin.jpg",
                "pipHost": "maya",
                "sourceTag": "ATHENIAN TETRADRACHM · SYMBOL OF WISDOM",
                "headline": "FACT CHECK #2: LAGARDE'S 2019 'OWL' DOCTRINE",
                "facts": [
                    {
                        "label": "OFFICIAL ECB QUOTE (2019)",
                        "value": "\"I'm neither a hawk nor a dove — I'm an owl.\"",
                        "accent": "cyan",
                    },
                    {
                        "label": "SEVEN-YEAR PUBLIC HABIT",
                        "value": "Diplomats & Staff Gift Owls for Her Frankfurt Desk",
                        "accent": "amber",
                    },
                ],
                "notes": [
                    "Central bankers use 'hawks' and 'doves' for rate policy; Lagarde publicly adopted Athena's owl on day one in 2019.",
                ],
            },
        ),
        (
            "c15",
            "c15",
            {
                "id": "s09_studio_real_question",
                "layout": "studio_dual",
                "monitorMediaPath": "episodes/ep01_lagarde/lagarde_eu_2025.jpg",
                "locationDate": "ACT III · FOLLOW THE CALENDAR",
                "headline": "WHY FEBRUARY 7, 2027 INSTEAD OF OCTOBER?",
            },
        ),
        (
            "c16",
            "c16",
            {
                "id": "s10_frankfurt_skyline_video",
                "layout": "real_video_pip",
                "mediaPath": "episodes/ep01_lagarde/frankfurt_skyline_1080p.mp4",
                "videoTrimStartSec": 0.5,
                "pipHost": "maya",
                "sourceTag": "REAL 5K CINEMA FOOTAGE · CC BY-SA 3.0",
                "locationDate": "FRANKFURT FINANCIAL DISTRICT · EUROZONE",
                "headline": "CONTROLLING THE WORLD'S #2 RESERVE CURRENCY",
            },
        ),
        (
            "c17",
            "c18",
            {
                "id": "s11_macron_summit_photo",
                "layout": "real_photo_pip",
                "mediaPath": "episodes/ep01_lagarde/macron_eu_summit_2025.jpg",
                "pipHost": "cole",
                "sourceTag": "EUROPEAN COUNCIL ARCHIVE · BRUSSELS",
                "locationDate": "FRANCE PRESIDENTIAL VOTE · APRIL 2027",
                "headline": "MACRON IS TERM-LIMITED EIGHT WEEKS LATER",
            },
        ),
        (
            "c19",
            "c20",
            {
                "id": "s12_le_pen_veto_split",
                "layout": "real_split_evidence",
                "mediaPath": "episodes/ep01_lagarde/marine_le_pen_2026.jpg",
                "pipHost": "maya",
                "sourceTag": "FRENCH ELECTORAL CALENDAR · 2027",
                "headline": "THE 8-YEAR SUCCESSION WINDOW (2027–2035)",
                "facts": [
                    {
                        "label": "ORIGINAL EXIT (OCT 2027)",
                        "value": "After French Election — Risk of Eurosceptic Veto",
                        "accent": "red",
                    },
                    {
                        "label": "NEW EXIT (FEB 7, 2027)",
                        "value": "Before Election — Macron & EU Leaders Pick Successor",
                        "accent": "cyan",
                    },
                ],
                "notes": [
                    "Under EU treaties, the ECB presidency is a non-renewable 8-year seat negotiated directly among eurozone leaders.",
                ],
            },
        ),
        (
            "c21",
            "c22",
            {
                "id": "s13_ecb_tower_photo",
                "layout": "real_photo_pip",
                "mediaPath": "episodes/ep01_lagarde/ecb_frankfurt_hq.jpg",
                "pipHost": "cole",
                "sourceTag": "EUROPEAN CENTRAL BANK · FRANKFURT",
                "locationDate": "MANDATE LOCKED THROUGH 2035",
                "headline": "INSTITUTIONAL POWER PLAY IN BROAD DAYLIGHT",
            },
        ),
        (
            "c23",
            "c24",
            {
                "id": "s14_studio_pivot_1921",
                "layout": "studio_dual",
                "monitorMediaPath": "episodes/ep01_lagarde/dzerzhinsky_1926.jpg",
                "locationDate": "MOSCOW · 1921 COUNTERINTELLIGENCE FILE",
                "headline": "THE PSYCHOLOGY OF 'SIT BACK & TRUST THE PLAN'",
            },
        ),
        (
            "c25",
            "c25",
            {
                "id": "s15_dzerzhinsky_archive",
                "layout": "real_photo_pip",
                "mediaPath": "episodes/ep01_lagarde/dzerzhinsky_1926.jpg",
                "pipHost": "cole",
                "sourceTag": "STATE MILITARY ARCHIVE · PUBLIC DOMAIN (1926)",
                "locationDate": "FELIX DZERZHINSKY · CHEKA / OGPU CHIEF",
                "headline": "ARCHITECT OF SOVIET DECEPTION OPERATIONS",
            },
        ),
        (
            "c26",
            "c28",
            {
                "id": "s16_lubyanka_operation_trust",
                "layout": "real_split_evidence",
                "mediaPath": "episodes/ep01_lagarde/lubyanka_hq_moscow.jpg",
                "pipHost": "maya",
                "sourceTag": "LUBYANKA HEADQUARTERS · MOSCOW",
                "headline": "OPERATION TRUST (1921–1926): THE FAKE PATRIOTS",
                "facts": [
                    {
                        "label": "COVER ORGANIZATION",
                        "value": "'Monarchist Union of Central Russia' (Built by OGPU)",
                        "accent": "amber",
                    },
                    {
                        "label": "CORE DECEPTION MESSAGE",
                        "value": "\"Patriots Control the Inside — Take No Action\"",
                        "accent": "red",
                    },
                ],
                "notes": [
                    "Soviet intelligence fabricated an entire internal resistance movement to pacify real exiles and Western spy agencies.",
                ],
            },
        ),
        (
            "c29",
            "c29",
            {
                "id": "s17_savinkov_trial_1924",
                "layout": "real_photo_pip",
                "mediaPath": "episodes/ep01_lagarde/savinkov_trial_1924.jpg",
                "pipHost": "cole",
                "sourceTag": "MOSCOW SUPREME TRIBUNAL · AUGUST 1924",
                "locationDate": "BORIS SAVINKOV CAPTURED",
                "headline": "LURED ACROSS THE BORDER BY FAKE 'TRUST' AGENTS",
            },
        ),
        (
            "c30",
            "c30",
            {
                "id": "s18_sidney_reilly_passport",
                "layout": "real_split_evidence",
                "mediaPath": "episodes/ep01_lagarde/sidney_reilly_passport_1918.jpg",
                "pipHost": "maya",
                "sourceTag": "ARCHIVAL PASSPORT EXHIBIT · SIDNEY REILLY",
                "headline": "1925: BRITAIN'S 'ACE OF SPIES' WALKS INTO THE TRAP",
                "facts": [
                    {
                        "label": "TARGET CAPTURED",
                        "value": "Sidney Reilly (British MI6 Master Operative)",
                        "accent": "red",
                    },
                    {
                        "label": "STRATEGIC OUTCOME (1927)",
                        "value": "6 Years of Opposition Paralyzed Without Firing a Shot",
                        "accent": "cyan",
                    },
                ],
                "notes": [
                    "Convinced that secret insiders were ready to topple Moscow, Reilly crossed into the USSR in 1925 and never returned.",
                ],
            },
        ),
        (
            "c31",
            "c32",
            {
                "id": "s19_soviet_archival_film",
                "layout": "real_video_pip",
                "mediaPath": "episodes/ep01_lagarde/soviet_1920s_reel_1080p.mp4",
                "videoTrimStartSec": 1.0,
                "pipHost": "cole",
                "sourceTag": "PUBLIC DOMAIN ARCHIVAL FILM · 1930",
                "locationDate": "EARLY SOVIET NEWSREEL ARCHIVE",
                "headline": "FROM 1921 STATE SPYING TO 2026 VIRAL ALGORITHMS",
            },
        ),
        (
            "c33",
            "c33",
            {
                "id": "s20_lagarde_eu_wide_closing",
                "layout": "real_photo_pip",
                "mediaPath": "episodes/ep01_lagarde/lagarde_eu_2025.jpg",
                "pipHost": "cole",
                "sourceTag": "EUROPEAN COMMISSION ARCHIVE · CC BY 4.0",
                "locationDate": "BRUSSELS / FRANKFURT",
                "headline": "DISTRACTION MYTHS VS. REAL TREATY POWER",
            },
        ),
        (
            "c34",
            "c34",
            {
                "id": "s21_studio_signoff",
                "layout": "studio_dual",
                "monitorMediaPath": "episodes/ep01_lagarde/ecb_frankfurt_hq.jpg",
                "locationDate": "COLE & MAYA · FINAL VERDICT",
                "headline": "FEB 7, 2027: REAL POWER MOVES ON THE PUBLIC CALENDAR",
            },
        ),
    ]

    shots: list[dict[str, Any]] = []
    cursor = 0.0
    for idx, (first_id, last_id, spec) in enumerate(shot_defs):
        is_last = idx == len(shot_defs) - 1
        if is_last:
            end_t = round(total_dur, 3)
        else:
            next_first_id = shot_defs[idx + 1][0]
            end_t = round(
                (by_id[last_id]["endSec"] + by_id[next_first_id]["startSec"]) / 2.0,
                3,
            )
        shot_obj = {"startSec": cursor, "endSec": end_t, **spec}
        shots.append(shot_obj)
        cursor = end_t

    chapters = [
        {
            "index": "01",
            "title": "The 45-Second Exit Video",
            "subtitle": "FRANKFURT · OCT 29, 2026",
            "startSec": round(by_id["c02"]["startSec"], 2),
        },
        {
            "index": "02",
            "title": "Bandages, Pearls & Athena's Owl",
            "subtitle": "PRIMARY SOURCE FACT-CHECK",
            "startSec": round(by_id["c07"]["startSec"], 2),
        },
        {
            "index": "03",
            "title": "The Spring 2027 French Election Window",
            "subtitle": "REAL CENTRAL BANK CHESS",
            "startSec": round(by_id["c15"]["startSec"], 2),
        },
        {
            "index": "04",
            "title": "1921 Moscow: Operation Trust",
            "subtitle": "DECLASSIFIED ESPIONAGE PARALLEL",
            "startSec": round(by_id["c24"]["startSec"], 2),
        },
    ]

    return {
        "episodeTitle": "WHY EUROPE'S CENTRAL BANK CHIEF QUIT EARLY",
        "categoryTag": "INVESTIGATION",
        "masterAudioPath": "episodes/ep01_lagarde/master_audio.mp3",
        "totalDurationSec": round(total_dur, 2),
        "cues": cues,
        "shots": shots,
        "chapters": chapters,
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    acquire_all_real_media()

    print("[2/4] Synthesizing dual-host neural narration (Cole + Maya)...")
    cues, raw_vo_wav = asyncio.run(
        synthesize_dialogue_lines(DIALOGUE_SCRIPT, TMP_AUDIO, pause_sec=0.26)
    )
    print(f"  [ok] Synthesized {len(cues)} cues ({raw_vo_wav})")

    print("[3/4] Mixing -16 LUFS broadcast master MP3...")
    master_mp3 = EP_PUBLIC / "master_audio.mp3"
    total_dur = mix_episode_master_audio(raw_vo_wav, master_mp3)
    print(f"  [ok] Master audio ready: {master_mp3} ({total_dur:.2f}s / {total_dur/60:.2f} min)")

    print("[4/4] Writing frame-accurate episode manifest JSON...")
    manifest = build_manifest(cues, total_dur)
    MANIFEST_OUT.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  [ok] Saved {MANIFEST_OUT} ({len(manifest['shots'])} shots, {total_dur:.2f}s)")


if __name__ == "__main__":
    main()
