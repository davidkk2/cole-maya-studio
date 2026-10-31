import asyncio
import inspect
import json
import math
import subprocess
from pathlib import Path
import edge_tts
import numpy as np

STUDIO_DIR = Path(r"C:\Users\samet\.gemini\antigravity\scratch\stickman-us-studio")
FFMPEG_BIN = STUDIO_DIR / "node_modules" / "@remotion" / "compositor-win32-x64-msvc" / "ffmpeg.exe"
FFMPEG = str(FFMPEG_BIN) if FFMPEG_BIN.exists() else "ffmpeg"

TMP_VO_DIR = STUDIO_DIR / "out" / "vo_alcatraz_pilot_tmp"
OUT_AUDIO = STUDIO_DIR / "public" / "audio" / "alcatraz_pilot_master.mp3"
OUT_TIMELINE = STUDIO_DIR / "src" / "ifnoir" / "alcatrazPilotTimeline.ts"

SR = 44100
FPS = 30

# Curious, warm, investigative US documentary narrator (per A6 Amber Noir standard)
VOICE_ID = "en-US-AndrewNeural"
VOICE_RATE = "+5%"
VOICE_PITCH = "-2Hz"

# 6 causally connected documentary shots starring Lead 1 (Orange) & Lead 2 (Blue)
SHOT_SCRIPT = [
    {
        "shotId": 1,
        "slug": "aerial_and_cellblock",
        "text": "June eleventh, nineteen sixty-two. Alcatraz was built to be inescapable, until two inmates broke out using cafeteria spoons.",
        "cues": [
            "JUNE 11, 1962",
            "ALCATRAZ WAS BUILT\nTO BE INESCAPABLE",
            "UNTIL TWO INMATES BROKE OUT\nUSING CAFETERIA SPOONS",
        ],
    },
    {
        "shotId": 2,
        "slug": "spoon_vent_macro",
        "text": "For six months, behind Cellblock B, they chipped through salt-damaged concrete around their tiny air vents.",
        "cues": [
            "FOR SIX MONTHS\nBEHIND CELLBLOCK B",
            "THEY CHIPPED THROUGH\nSALT-DAMAGED CONCRETE",
            "AROUND THEIR\nTINY AIR VENTS",
        ],
    },
    {
        "shotId": 3,
        "slug": "fbi_vent_archival",
        "text": "By day, they hid the eight-inch hole behind fake cardboard grilles painted with prison soap.",
        "cues": [
            "BY DAY, THEY HID\nTHE EIGHT-INCH HOLE",
            "BEHIND FAKE\nCARDBOARD GRILLES",
            "PAINTED WITH\nPRISON SOAP",
        ],
    },
    {
        "shotId": 4,
        "slug": "dummy_head_flashlight",
        "text": "To fool midnight bed checks, they sculpted lifelike dummy heads from toilet paper and real barbershop hair.",
        "cues": [
            "TO FOOL MIDNIGHT\nBED CHECKS",
            "THEY SCULPTED LIFELIKE\nDUMMY HEADS",
            "FROM TOILET PAPER AND\nREAL BARBERSHOP HAIR",
        ],
    },
    {
        "shotId": 5,
        "slug": "utility_shaft_raft",
        "text": "Then they climbed three stories up a service shaft, carrying a raft stitched from fifty stolen raincoats.",
        "cues": [
            "THEN THEY CLIMBED\nTHREE STORIES UP A SERVICE SHAFT",
            "CARRYING A RAFT",
            "STITCHED FROM FIFTY\nSTOLEN RAINCOATS",
        ],
    },
    {
        "shotId": 6,
        "slug": "foggy_bay_payoff",
        "text": "They vanished into freezing San Francisco Bay... and sixty years later, the FBI still hasn't found a single body.",
        "cues": [
            "THEY VANISHED INTO\nFREEZING SAN FRANCISCO BAY",
            "AND SIXTY YEARS LATER",
            "THE FBI STILL HASN'T FOUND\nA SINGLE BODY",
        ],
    },
]


def clean_token(w: str) -> str:
    return "".join(ch for ch in w.upper() if ch.isalnum() or ch == "'")


def find_trim_bounds(samples: np.ndarray, thresh: float = 0.014, pad_ms: int = 30) -> tuple[int, int]:
    if len(samples) == 0:
        return 0, 0
    idx = np.where(np.abs(samples) > thresh)[0]
    if len(idx) == 0:
        return 0, min(len(samples), int(0.1 * SR))
    pad = int((pad_ms / 1000.0) * SR)
    start = max(0, int(idx[0]) - pad)
    end = min(len(samples), int(idx[-1]) + pad)
    return start, end


async def synth_shot(shot: dict) -> dict:
    TMP_VO_DIR.mkdir(parents=True, exist_ok=True)
    sid = shot["shotId"]
    mp3_path = TMP_VO_DIR / f"shot_{sid:02d}.mp3"
    meta_path = TMP_VO_DIR / f"shot_{sid:02d}_words.json"

    sig = inspect.signature(edge_tts.Communicate.__init__)
    kwargs = {"voice": VOICE_ID, "rate": VOICE_RATE, "pitch": VOICE_PITCH}
    if "boundary" in sig.parameters:
        kwargs["boundary"] = "WordBoundary"

    word_events = []
    audio_bytes = bytearray()

    for attempt in range(4):
        try:
            word_events.clear()
            audio_bytes.clear()
            comm = edge_tts.Communicate(shot["text"], **kwargs)
            async for chunk in comm.stream():
                ctype = chunk.get("type")
                if ctype == "audio":
                    audio_bytes.extend(chunk["data"])
                elif ctype == "WordBoundary":
                    # offset and duration are in 100-nanosecond ticks (1e7 ticks = 1 sec)
                    offset_s = float(chunk["offset"]) / 1e7
                    dur_s = max(0.06, float(chunk["duration"]) / 1e7)
                    word_events.append(
                        {
                            "word": str(chunk["text"]),
                            "startRel": offset_s,
                            "endRel": offset_s + dur_s,
                        }
                    )
            if len(audio_bytes) > 500:
                mp3_path.write_bytes(bytes(audio_bytes))
                meta_path.write_text(json.dumps(word_events, indent=2), encoding="utf-8")
                break
        except Exception as exc:
            if attempt == 3:
                raise exc
            await asyncio.sleep(1.0 * (attempt + 1))

    wav_tmp = TMP_VO_DIR / f"shot_{sid:02d}_dec.wav"
    subprocess.run(
        [
            FFMPEG, "-y", "-i", str(mp3_path),
            "-acodec", "pcm_s16le",
            "-ac", "1", "-ar", str(SR), str(wav_tmp),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    import wave
    with wave.open(str(wav_tmp), "rb") as wf:
        pcm_bytes = wf.readframes(wf.getnframes())
    wav_tmp.unlink(missing_ok=True)
    full_samples = (np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0).copy()
    s0, s1 = find_trim_bounds(full_samples, thresh=0.014, pad_ms=28)
    trim_offset_s = s0 / SR
    samples = full_samples[s0:s1]
    clip_dur_s = len(samples) / SR

    mx = float(np.max(np.abs(samples))) if len(samples) else 0.0
    if mx > 1e-4:
        samples = samples / mx
    # Warm broadcast studio gentle saturation (natural dynamics, zero harsh clipping)
    samples = (np.tanh(samples * 1.25) * 0.88).astype(np.float32)

    # Shift word events by trim_offset_s
    adjusted_words = []
    for we in word_events:
        ws = max(0.0, we["startRel"] - trim_offset_s)
        we_end = min(clip_dur_s, max(ws + 0.05, we["endRel"] - trim_offset_s))
        adjusted_words.append({"word": we["word"], "startRel": ws, "endRel": we_end})

    return {
        "shot": shot,
        "samples": samples,
        "durationSec": clip_dur_s,
        "wordsRel": adjusted_words,
    }


def align_cues_and_words(shot: dict, shot_voice_start: float, clip_dur_s: float, words_rel: list[dict]):
    """
    Map cue display tokens to exact spoken WordBoundary timestamps so every displayed ALL-CAPS
    word highlights on the exact frame it is spoken (including numbers like 11 / 1962).
    """
    # Build flat list of cue display words
    cue_specs = []
    all_cue_tokens = []
    for cue_idx, cue_text in enumerate(shot["cues"]):
        lines = cue_text.split("\n")
        tokens = []
        for ln in lines:
            for tok in ln.strip().split():
                if tok:
                    tokens.append(tok)
                    all_cue_tokens.append((cue_idx, tok))
        cue_specs.append({"cueIdx": cue_idx, "text": cue_text, "tokens": tokens})

    n_disp = len(all_cue_tokens)
    if len(words_rel) >= 2 and n_disp > 0:
        n_sp = len(words_rel)
        sp_norm = [clean_token(w["word"]) for w in words_rel]
        aliases = {
            "11": ["ELEVENTH", "11", "ELEVEN"],
            "1962": ["NINETEEN", "SIXTYTWO", "SIXTY", "TWO", "1962"],
        }
        mapped_words = []
        cursor_sp = 0
        for i, (cue_idx, disp_tok) in enumerate(all_cue_tokens):
            d_clean = clean_token(disp_tok)
            matched_indices = []
            if d_clean in aliases:
                targets = aliases[d_clean]
                scan = cursor_sp
                while scan < min(n_sp, cursor_sp + 4) and sp_norm[scan] in targets:
                    matched_indices.append(scan)
                    scan += 1
            else:
                for look in range(cursor_sp, min(n_sp, cursor_sp + 4)):
                    if (
                        sp_norm[look] == d_clean
                        or d_clean.startswith(sp_norm[look])
                        or sp_norm[look].startswith(d_clean)
                    ):
                        matched_indices.append(look)
                        if "-" in disp_tok and look + 1 < n_sp:
                            part2 = clean_token(disp_tok.split("-", 1)[1])
                            if part2 and sp_norm[look + 1] == part2:
                                matched_indices.append(look + 1)
                        break

            if matched_indices:
                sp_i = matched_indices[0]
                sp_next = matched_indices[-1]
                cursor_sp = min(n_sp - 1, sp_next + 1)
            else:
                sp_i = min(n_sp - 1, cursor_sp)
                sp_next = sp_i
                cursor_sp = min(n_sp - 1, cursor_sp + 1)

            ws = shot_voice_start + words_rel[sp_i]["startRel"]
            we = shot_voice_start + words_rel[sp_next]["endRel"]
            if i > 0 and ws < mapped_words[-1]["endSec"]:
                ws = mapped_words[-1]["endSec"]
            if we <= ws + 0.05:
                we = ws + 0.08
            mapped_words.append(
                {
                    "cueIndex": cue_idx,
                    "word": disp_tok,
                    "startSec": round(ws, 3),
                    "endSec": round(we, 3),
                    "startFrame": int(round(ws * FPS)),
                    "endFrame": int(round(we * FPS)),
                }
            )
    else:
        # Proportional fallback weighted by character length
        weights = [max(2, len(t[1])) for t in all_cue_tokens]
        tot_w = sum(weights) or 1
        cur = shot_voice_start
        mapped_words = []
        for (cue_idx, disp_tok), w in zip(all_cue_tokens, weights):
            dt = clip_dur_s * (w / tot_w)
            ws = cur
            we = cur + dt
            cur = we
            mapped_words.append(
                {
                    "cueIndex": cue_idx,
                    "word": disp_tok,
                    "startSec": round(ws, 3),
                    "endSec": round(we, 3),
                    "startFrame": int(round(ws * FPS)),
                    "endFrame": int(round(we * FPS)),
                }
            )

    # Group into non-overlapping phrase cues with brief natural reading hold (+0.18s)
    cues_out = []
    for cs in cue_specs:
        c_idx = cs["cueIdx"]
        cw = [mw for mw in mapped_words if mw["cueIndex"] == c_idx]
        if not cw:
            continue
        cs_sec = cw[0]["startSec"]
        ce_sec = cw[-1]["endSec"] + 0.16
        cues_out.append(
            {
                "text": cs["text"],
                "startSec": round(cs_sec, 3),
                "endSec": round(ce_sec, 3),
                "startFrame": int(round(cs_sec * FPS)),
                "endFrame": int(round(ce_sec * FPS)),
                "words": [
                    {
                        "word": w["word"],
                        "startFrame": w["startFrame"],
                        "endFrame": w["endFrame"],
                    }
                    for w in cw
                ],
            }
        )

    # Clamp non-overlapping cue endFrames
    for i in range(len(cues_out) - 1):
        if cues_out[i]["endFrame"] > cues_out[i + 1]["startFrame"]:
            cues_out[i]["endFrame"] = cues_out[i + 1]["startFrame"]
            cues_out[i]["endSec"] = round(cues_out[i]["endFrame"] / FPS, 3)

    return cues_out


def lowpass_noise(rng: np.random.Generator, n: int, taps: int = 14) -> np.ndarray:
    raw = rng.standard_normal(n).astype(np.float32)
    kernel = np.hanning(taps + 2)[1:-1].astype(np.float32)
    kernel /= np.sum(kernel)
    return np.convolve(raw, kernel, mode="same")


def build_docu_sfx_kit(rng: np.random.Generator) -> dict[str, np.ndarray]:
    """Synthesize subtle, cinema-grade documentary foley & motion-graphics SFX."""
    kit: dict[str, np.ndarray] = {}

    # 1. Soft cinematic transition whoosh (plays 3 frames BEFORE shot cuts)
    n = int(0.36 * SR)
    t = np.linspace(0, 0.36, n, endpoint=False, dtype=np.float32)
    env = np.sin(np.pi * (t / 0.36) ** 0.78) ** 2
    air = lowpass_noise(rng, n, taps=22)
    kit["whoosh"] = (air * env * 0.48).astype(np.float32)

    # 2. Reverberant Alcatraz iron cell bar clang
    n = int(1.15 * SR)
    t = np.linspace(0, 1.15, n, endpoint=False, dtype=np.float32)
    clang = (
        np.sin(2 * np.pi * 218 * t) * np.exp(-t * 4.5) * 0.55
        + np.sin(2 * np.pi * 467 * t) * np.exp(-t * 6.8) * 0.38
        + np.sin(2 * np.pi * 912 * t) * np.exp(-t * 11.0) * 0.22
        + lowpass_noise(rng, n, taps=6) * np.exp(-t * 36.0) * 0.65
    )
    kit["iron_clang"] = (np.tanh(clang * 1.3) * 0.52).astype(np.float32)

    # 3. Metallic spoon scraping salt-damaged concrete
    n = int(0.22 * SR)
    t = np.linspace(0, 0.22, n, endpoint=False, dtype=np.float32)
    grit = np.diff(lowpass_noise(rng, n, taps=5), prepend=0.0)
    ring = np.sin(2 * np.pi * (1420 + 280 * t) * t) * np.exp(-t * 28.0) * 0.22
    scrape_env = np.sin(np.pi * (t / 0.22)) ** 1.3
    kit["spoon_scrape"] = (np.tanh((grit * 1.4 + ring) * 1.4) * scrape_env * 0.46).astype(np.float32)

    # 4. Archival camera shutter click + paper slide
    n = int(0.18 * SR)
    t = np.linspace(0, 0.18, n, endpoint=False, dtype=np.float32)
    click1 = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 95.0) * 0.75
    click2 = rng.standard_normal(n).astype(np.float32) * np.exp(-np.maximum(0, t - 0.045) * 110.0) * (t >= 0.045) * 0.55
    kit["shutter"] = (np.clip(click1 + click2, -0.9, 0.9) * 0.48).astype(np.float32)

    # 5. Subtle HUD telemetry tick
    n = int(0.045 * SR)
    t = np.linspace(0, 0.045, n, endpoint=False, dtype=np.float32)
    kit["ui_tick"] = (np.sin(2 * np.pi * 1650 * t) * np.exp(-t * 65.0) * 0.24).astype(np.float32)

    # 6. Heavy FBI dossier stamp thud
    n = int(0.38 * SR)
    t = np.linspace(0, 0.38, n, endpoint=False, dtype=np.float32)
    sub = np.sin(2 * np.pi * (76 * np.exp(-t * 12.0) + 32) * t) * np.exp(-t * 8.5)
    paper = lowpass_noise(rng, n, taps=8) * np.exp(-t * 32.0) * 0.65
    kit["stamp"] = (np.tanh((sub + paper) * 1.4) * 0.58).astype(np.float32)

    # 7. Distant San Francisco Bay nocturnal foghorn
    n = int(2.4 * SR)
    t = np.linspace(0, 2.4, n, endpoint=False, dtype=np.float32)
    f_env = np.minimum(1.0, t / 0.35) * np.minimum(1.0, (2.4 - t) / 0.75)
    horn = (
        np.sin(2 * np.pi * 65.41 * t) * 0.65
        + np.sin(2 * np.pi * 130.81 * t) * 0.38
        + np.sin(2 * np.pi * 196.00 * t) * 0.18
    )
    kit["foghorn"] = (np.tanh(horn * 1.35) * f_env * 0.34).astype(np.float32)

    return kit


def synthesize_amber_noir_bed(total_sec: float, rng: np.random.Generator) -> np.ndarray:
    """Warm, moody D-minor Amber Noir documentary cello/pad underscore + bay wind."""
    n = int(total_sec * SR)
    t = np.linspace(0, total_sec, n, endpoint=False, dtype=np.float32)

    # Slow dark documentary harmonic progression (D2 - A2 - F3 / Bb1 - F2 - D3 / G1 - D2 - Bb2 / A1 - E2 - C#3)
    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)

    chords = [
        (73.42, 110.00, 174.61, 220.00),
        (58.27, 116.54, 174.61, 261.63),
        (49.00, 98.00, 146.83, 233.08),
        (55.00, 110.00, 164.81, 207.65),
    ]
    seg_dur = total_sec / 4.0
    for idx, freqs in enumerate(chords):
        c0 = idx * seg_dur
        c1 = (idx + 1) * seg_dur
        # Smooth crossfade window
        w = np.clip((t - (c0 - 0.8)) / 1.2, 0.0, 1.0) * np.clip(((c1 + 0.8) - t) / 1.2, 0.0, 1.0)
        for f_i, f in enumerate(freqs):
            amp = 0.055 if f_i == 0 else 0.032
            left += (np.sin(2 * np.pi * f * t) * w * amp).astype(np.float32)
            right += (np.sin(2 * np.pi * (f * 1.0016) * t) * w * amp).astype(np.float32)

    # Subtle rhythmic mystery pulse (72 BPM soft muted sub-heartbeat)
    pulse_phase = (t * (72.0 / 60.0)) % 1.0
    pulse = np.sin(2 * np.pi * 52.0 * (pulse_phase / 1.2)) * np.minimum(1.0, pulse_phase * 28.0) * np.exp(-pulse_phase * 9.5) * 0.09

    # Soft bay wind air texture
    wind_L = lowpass_noise(rng, n, taps=32) * 0.018
    wind_R = lowpass_noise(rng, n, taps=32) * 0.018

    fade_in = np.minimum(1.0, t / 0.6)
    fade_out = np.minimum(1.0, (total_sec - t) / 1.1)
    master_env = (fade_in * fade_out).astype(np.float32)

    L = (left + pulse + wind_L) * master_env
    R = (right + pulse + wind_R) * master_env
    return np.stack([L, R], axis=1)


async def main():
    print("[Alcatraz Pilot] Synthesizing US documentary voiceover + WordBoundary alignment...")
    shot_results = []
    for shot in SHOT_SCRIPT:
        res = await synth_shot(shot)
        shot_results.append(res)

    # Build shot timeline with clean visual breathing room around voice
    cursor_sec = 0.0
    shots_timeline = []
    all_cues = []

    for idx, res in enumerate(shot_results):
        lead_pad = 0.35 if idx == 0 else 0.22
        tail_pad = 0.34 if idx < len(shot_results) - 1 else 0.85
        shot_start_sec = cursor_sec
        voice_start_sec = shot_start_sec + lead_pad
        shot_end_sec = voice_start_sec + res["durationSec"] + tail_pad

        # Snap shot boundaries to exact frames
        start_frame = int(round(shot_start_sec * FPS))
        end_frame = int(round(shot_end_sec * FPS))
        shot_start_sec = start_frame / FPS
        shot_end_sec = end_frame / FPS
        voice_start_sec = shot_start_sec + lead_pad
        cursor_sec = shot_end_sec

        cues = align_cues_and_words(res["shot"], voice_start_sec, res["durationSec"], res["wordsRel"])
        all_cues.extend(cues)

        shots_timeline.append(
            {
                "shotId": res["shot"]["shotId"],
                "slug": res["shot"]["slug"],
                "startFrame": start_frame,
                "endFrame": end_frame,
                "durationInFrames": end_frame - start_frame,
                "voiceStartSec": round(voice_start_sec, 3),
                "samples": res["samples"],
            }
        )

    total_frames = shots_timeline[-1]["endFrame"]
    total_sec = total_frames / FPS
    print(f"[Alcatraz Pilot] Total duration: {total_sec:.2f}s ({total_frames} frames @ {FPS}fps)")

    rng = np.random.default_rng(19620611)
    sfx = build_docu_sfx_kit(rng)
    bed = synthesize_amber_noir_bed(total_sec, rng)
    n_total = bed.shape[0]

    vo_L = np.zeros(n_total, dtype=np.float32)
    vo_R = np.zeros(n_total, dtype=np.float32)
    duck = np.ones(n_total, dtype=np.float32)

    for st in shots_timeline:
        s_i = int(st["voiceStartSec"] * SR)
        samp = st["samples"]
        e_i = min(n_total, s_i + len(samp))
        if e_i > s_i:
            vo_L[s_i:e_i] += samp[: e_i - s_i]
            vo_R[s_i:e_i] += samp[: e_i - s_i]
            d0 = max(0, s_i - int(0.08 * SR))
            d1 = min(n_total, e_i + int(0.10 * SR))
            duck[d0:d1] = np.minimum(duck[d0:d1], 0.42)

    smooth_k = np.ones(int(0.05 * SR), dtype=np.float32) / int(0.05 * SR)
    duck_s = np.convolve(duck, smooth_k, mode="same")
    bed[:, 0] *= duck_s
    bed[:, 1] *= duck_s

    # Schedule motivated foley & transition SFX (whooshes 3 frames BEFORE shot cuts!)
    sfx_events: list[tuple[float, str, float]] = []
    for i, st in enumerate(shots_timeline):
        cut_s = st["startFrame"] / FPS
        if i > 0:
            sfx_events.append((max(0.0, cut_s - 3.0 / FPS), "whoosh", 0.72))

        sid = st["shotId"]
        if sid == 1:
            sfx_events.append((0.08, "foghorn", 0.55))
            sfx_events.append((1.85, "iron_clang", 0.68))
        elif sid == 2:
            # Synced with Orange's spoon-chipping strokes (every 24 frames = 0.8s inside Shot 2)
            t_sp = cut_s + 0.45
            while t_sp < (st["endFrame"] / FPS) - 0.35:
                sfx_events.append((round(t_sp, 3), "spoon_scrape", 0.62))
                t_sp += 0.80
        elif sid == 3:
            sfx_events.append((cut_s + 0.12, "shutter", 0.75))
            for k in range(4):
                sfx_events.append((cut_s + 0.55 + k * 0.22, "ui_tick", 0.55))
        elif sid == 4:
            sfx_events.append((cut_s + 1.85, "shutter", 0.70))
            sfx_events.append((cut_s + 1.92, "stamp", 0.65))
        elif sid == 5:
            sfx_events.append((cut_s + 0.35, "iron_clang", 0.42))
        elif sid == 6:
            sfx_events.append((cut_s + 0.25, "foghorn", 0.62))
            sfx_events.append((cut_s + 2.40, "stamp", 0.78))

    for ev_sec, kind, gain in sfx_events:
        clip = sfx[kind]
        s_i = int(ev_sec * SR)
        e_i = min(n_total, s_i + len(clip))
        if e_i > s_i:
            bed[s_i:e_i, 0] += clip[: e_i - s_i] * gain
            bed[s_i:e_i, 1] += clip[: e_i - s_i] * gain * 0.96

    # Foreground crisp narration + clean true-peak ceiling (~ -16 LUFS, <= -1.2 dBTP)
    mix = np.zeros_like(bed)
    mix[:, 0] = bed[:, 0] * 0.78 + vo_L * 0.96
    mix[:, 1] = bed[:, 1] * 0.78 + vo_R * 0.96
    mix = np.tanh(mix * 0.95) * 0.86

    OUT_AUDIO.parent.mkdir(parents=True, exist_ok=True)
    wav_master = STUDIO_DIR / "out" / "alcatraz_pilot_tmp.wav"
    import wave
    pcm16 = np.clip(np.round(mix * 32767.0), -32768, 32767).astype(np.int16)
    with wave.open(str(wav_master), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

    # Encode via FFmpeg loudnorm targeting -16 LUFS & -1.5 dBTP per A6 standard
    subprocess.run(
        [
            FFMPEG, "-y",
            "-i", str(wav_master),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=9",
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(OUT_AUDIO),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    wav_master.unlink(missing_ok=True)

    # Export clean TypeScript timeline for Remotion
    shots_export = [
        {
            "shotId": s["shotId"],
            "slug": s["slug"],
            "startFrame": s["startFrame"],
            "endFrame": s["endFrame"],
            "durationInFrames": s["durationInFrames"],
        }
        for s in shots_timeline
    ]

    OUT_TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    ts_content = f"""// Auto-generated by scripts/build_alcatraz_pilot_audio.py
export interface CaptionWordTiming {{
  readonly word: string;
  readonly startFrame: number;
  readonly endFrame: number;
}}

export interface CaptionCue {{
  readonly text: string;
  readonly startSec: number;
  readonly endSec: number;
  readonly startFrame: number;
  readonly endFrame: number;
  readonly words: readonly CaptionWordTiming[];
}}

export interface PilotShotTiming {{
  readonly shotId: number;
  readonly slug: string;
  readonly startFrame: number;
  readonly endFrame: number;
  readonly durationInFrames: number;
}}

export const PILOT_FPS = {FPS};
export const PILOT_TOTAL_FRAMES = {total_frames};
export const PILOT_DURATION_SEC = {round(total_sec, 3)};

export const PILOT_TITLE: readonly [string, string] = [
  "JUNE 11, 1962",
  "THE SPOON ESCAPE",
];

export const PILOT_SHOTS: readonly PilotShotTiming[] = {json.dumps(shots_export, indent=2)} as const;

export const PILOT_CUES: readonly CaptionCue[] = {json.dumps(all_cues, indent=2)} as const;
"""
    OUT_TIMELINE.write_text(ts_content, encoding="utf-8")
    print(f"[Alcatraz Pilot] Exported {OUT_AUDIO} and {OUT_TIMELINE} ({len(all_cues)} caption cues).")


if __name__ == "__main__":
    asyncio.run(main())
