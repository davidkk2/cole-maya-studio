import asyncio
import json
import math
import os
import subprocess
from pathlib import Path
import edge_tts
import numpy as np

STUDIO_DIR = Path(r"C:\Users\samet\.gemini\antigravity\scratch\stickman-us-studio")
TMP_VO_DIR = STUDIO_DIR / "out" / "vo_day04_tmp"
OUT_AUDIO = STUDIO_DIR / "public" / "audio" / "day04_master.mp3"
OUT_TIMELINE = STUDIO_DIR / "src" / "day4" / "day04Timeline.ts"

SR = 44100
FPS = 30
TOTAL_SECONDS = 504.0  # 08:24 (8m 24s = 15,120 frames -> unlocks US Mid-Roll Ads!)
TOTAL_FRAMES = int(TOTAL_SECONDS * FPS)

VOICES = {
    "narrator": ("en-US-ChristopherNeural", "-4%", "-2Hz"),
    "orange": ("en-US-BrianNeural", "+6%", "+3Hz"),
    "blue": ("en-US-AndrewNeural", "+3%", "+0Hz"),
    "ai": ("en-US-AriaNeural", "+4%", "+2Hz"),
    "agent": ("en-US-EricNeural", "-8%", "-6Hz"),
}

# 6-Act Cinematic Screenplay (~76 lines across 504s)
# Each tuple: (min_start_sec, act, speaker, text, sfx_tag)
SCRIPT = [
    # === ACT 1: THE RED SKY WARNING & THE BUDGET SPLIT (00:00 - 01:18) ===
    (0.8, 1, "narrator", "A quiet sunset over the city.", None),
    (3.8, 1, "narrator", "Two best friends. One rooftop table.", None),
    (7.4, 1, "narrator", "Then the clouds tear open.", "whoosh"),
    (10.8, 1, "ai", "Emergency alert. Extinction-class asteroid Apophis X detected. Impact in twenty-four hours.", "siren"),
    (18.5, 1, "narrator", "Every screen in the city turns blood red.", None),
    (22.2, 1, "narrator", "Blue checks his tech startup account.", None),
    (25.4, 1, "narrator", "One million dollars.", "chime"),
    (28.0, 1, "narrator", "Orange turns his hoodie pockets inside out.", None),
    (31.6, 1, "narrator", "A crumpled one-dollar bill... and a bent paperclip.", "ripple"),
    (36.2, 1, "blue", "Sorry, bro. My automated titanium bunker only has oxygen calibrated for one.", None),
    (42.5, 1, "narrator", "Blue walks away toward his hilltop plot without looking back.", None),
    (47.5, 1, "narrator", "Orange stares at the single dollar in his hand.", None),
    (51.5, 1, "orange", "One dollar? Twenty-four hours? Bet.", "ripple"),
    (56.5, 1, "narrator", "One million dollars of high-tech perfection... versus one dollar and pure street physics.", None),
    (64.2, 1, "narrator", "When the sky falls tonight... only one base will survive.", "boom"),

    # === ACT 2: HOUR 1 TO 24 — TITANIUM TECH VS $1 SCRAP PHYSICS (01:18 - 02:48) ===
    (78.5, 2, "narrator", "Hour one. Blue deploys a fleet of heavy construction drones.", None),
    (84.2, 2, "narrator", "Four hundred thousand dollars for three-meter solid titanium walls.", "weld"),
    (89.8, 2, "narrator", "Three hundred and fifty thousand for dual AI plasma turrets.", "laser"),
    (95.2, 2, "narrator", "And two hundred and fifty thousand for an electromagnetic forcefield dome.", "hum"),
    (101.2, 2, "blue", "Zero weak points. Let the rocks fall.", None),
    (106.0, 2, "narrator", "Across the road, Orange walks up to the abandoned city scrapyard.", None),
    (111.2, 2, "narrator", "Entry fee: one single dollar.", "chime"),
    (115.0, 2, "narrator", "Here is the rule nobody thinks about.", None),
    (118.4, 2, "narrator", "Height catches shockwaves. Depth absorbs them.", "ripple"),
    (123.5, 2, "narrator", "Instead of building up, Orange digs forty meters straight down into solid bedrock.", "weld"),
    (130.5, 2, "narrator", "Above the shaft, he welds rusted truck springs under an angled shipping container roof.", "boing"),
    (137.8, 2, "narrator", "Twelve broken microwave transformers wired to a scrap lightning rod.", "zap"),
    (143.8, 2, "narrator", "No computers. Hand-cranked steel locks. And one tiny street flower saved in a tin can.", None),
    (151.5, 2, "blue", "Wait... is he seriously using rusty car springs as a roof?", None),
    (157.0, 2, "orange", "Laugh now, genius. Physics is free.", None),
    (162.0, 2, "ai", "Warning. Atmospheric entry detected. Impact in three... two... one.", "siren"),

    # === ACT 3: WAVE 1 & 2 — METEOR HAIL & STALKER TITANS (02:48 - 04:18) ===
    (169.0, 3, "narrator", "Midnight. The sky turns violet.", "boom"),
    (173.2, 3, "narrator", "Wave one. Supersonic meteor fragments falling at three thousand kilometers an hour.", "whoosh"),
    (180.2, 3, "narrator", "Blue doesn't even stand up from his gaming chair.", None),
    (184.0, 3, "narrator", "His plasma turrets lock on and vaporize twenty meteors in ten seconds.", "laser"),
    (190.2, 3, "blue", "Too easy. Best million I ever spent.", None),
    (194.8, 3, "narrator", "Then a blazing boulder dives straight at Orange's scrap roof.", "whoosh"),
    (200.2, 3, "narrator", "Point zero five seconds.", "subdrop"),
    (203.2, 3, "narrator", "Instead of fighting the force... forty truck springs compress... and fire it right back.", "boing"),
    (210.8, 3, "narrator", "The ricochet smashes a second meteor mid-air.", "boom"),
    (215.2, 3, "blue", "What?! How did junkyard springs just bounce a meteor?!", None),
    (220.8, 3, "narrator", "Before Blue can process it, the smoking craters split open.", "boom"),
    (226.0, 3, "narrator", "Something rode inside the rock. Armored magma titans.", "siren"),
    (231.8, 3, "narrator", "Blue fires nonstop... until his turret barrels glow white-hot and jam.", "laser"),
    (238.0, 3, "ai", "Alert. Turret ammunition depleted. Relying on primary shield.", None),
    (243.5, 3, "narrator", "Three titans charge Orange's scrap pit.", None),
    (247.2, 3, "orange", "Step right into the puddle, fellas.", None),
    (250.8, 3, "narrator", "He pulls a bicycle chain. Twelve microwave coils discharge into the rainwater.", "zap"),
    (257.2, 3, "narrator", "Ten million volts drop all three titans in a single flash.", "boom"),

    # === ACT 4: THE FLAW OF RIGID PERFECTION — THE EMP TWIST (04:18 - 05:36) ===
    (263.5, 4, "narrator", "And then... the clouds part.", "subdrop"),
    (267.5, 4, "narrator", "The main asteroid core. Ten thousand tons of burning iron.", None),
    (273.2, 4, "narrator", "Before it even hits, its atmospheric shockwave unleashes a massive electromagnetic pulse.", "emp"),
    (280.8, 4, "narrator", "And here is the fatal flaw of a one-million-dollar smart bunker.", None),
    (286.0, 4, "narrator", "Everything runs on microchips.", None),
    (289.2, 4, "ai", "Critical failure. E M P detected. Forcefield offline. Electronic blast doors jammed.", "emp"),
    (297.2, 4, "narrator", "Blue's lights die.", None),
    (300.0, 4, "narrator", "Without the energy shield, shockwaves hammer bare titanium.", "boom"),
    (305.2, 4, "narrator", "Rigid metal doesn't bend. Under extreme pressure... it cracks.", "crack"),
    (311.5, 4, "blue", "Door override! Come on, open! Open!", None),
    (316.2, 4, "narrator", "The electronic keypad is fried. His million-dollar fortress just became a titanium trap.", "heartbeat"),
    (324.0, 4, "narrator", "Directly above his cracked glass roof... the main core locks into terminal descent.", "siren"),

    # === ACT 5: TWELVE SECONDS TO CHOOSE — THE CLIMAX (05:36 - 07:18) ===
    (336.5, 5, "narrator", "Forty meters underground, Orange's mechanical bunker doesn't even flicker.", None),
    (342.5, 5, "narrator", "No chips to fry. Solid bedrock overhead. He is one hundred percent safe.", None),
    (349.2, 5, "narrator", "Then Orange peers through his brass periscope.", None),
    (353.5, 5, "narrator", "Across the burning field, he sees Blue pounding on jammed glass.", "heartbeat"),
    (359.5, 5, "narrator", "Twelve seconds to impact.", "subdrop"),
    (362.5, 5, "narrator", "Down here, you survive guaranteed. Up there... neither of you might make it back.", "heartbeat"),
    (370.0, 5, "narrator", "Stay behind the steel hatch... or run into the fire.", None),
    (375.5, 5, "orange", "Hang on, idiot!", "ripple"),
    (378.5, 5, "narrator", "Orange grabs a solid iron crowbar, spins the manual wheel, and sprints into the firestorm.", "whoosh"),
    (386.0, 5, "narrator", "Eight seconds. Shockwaves rip the asphalt apart behind his heels.", "boom"),
    (392.2, 5, "narrator", "Five seconds. He leaps onto Blue's cracking titanium roof and jams the iron crowbar into the seam.", "weld"),
    (400.2, 5, "orange", "One... two... Pull!", "crack"),
    (403.8, 5, "narrator", "Pure leverage snaps the deadbolt.", "ripple"),
    (407.0, 5, "narrator", "Two seconds left. Orange grabs Blue by the jacket and dives headfirst down the scrapyard chute.", "whoosh"),
    (414.5, 5, "narrator", "Half a second. The manual hatch slams shut.", "subdrop"),
    (419.0, 5, "narrator", "Impact.", "megaboom"),
    (424.5, 5, "narrator", "Above them, the million-dollar fortress disappears in a blinding white wall.", None),
    (430.8, 5, "narrator", "Forty meters below... forty rusty truck springs groan... compress to the final millimeter...", "boing"),
    (437.8, 5, "narrator", "...and hold.", "chime"),

    # === ACT 6: GOLDEN DAWN, FIST-BUMP & THE ALIEN VAULT HOOK (07:18 - 08:24) ===
    (441.5, 6, "narrator", "Dust settles in a single warm shaft of light.", None),
    (446.0, 6, "narrator", "On the wooden crate, the tiny street flower doesn't even lose a petal.", None),
    (451.8, 6, "blue", "A million dollars... and you saved my life with a one-dollar crowbar.", None),
    (457.8, 6, "orange", "Hey. Told you. Best dollar I ever spent.", "ripple"),
    (463.0, 6, "narrator", "Two best friends climb out into a quiet golden sunrise.", None),
    (468.5, 6, "narrator", "The titanium fortress is gone. Only craters remain.", None),
    (473.5, 6, "narrator", "Until they look down into the center of the smoking pit.", "subdrop"),
    (478.2, 6, "narrator", "That wasn't just iron rock.", None),
    (481.2, 6, "narrator", "Half-buried in the crater sits a massive purple vault door... counting down from two.", "hum"),
    (488.2, 6, "agent", "Step away from the crater, boys. You have no idea what just landed.", None),
    (494.5, 6, "narrator", "So which base would you trust? Hit like, subscribe for Part Two, and drop your pick in the comments.", "chime"),
]


async def synth_one(idx: int, speaker: str, text: str, out_mp3: Path, sem: asyncio.Semaphore):
    voice, rate, pitch = VOICES[speaker]
    async with sem:
        for attempt in range(4):
            try:
                comm = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
                await comm.save(str(out_mp3))
                if out_mp3.exists() and out_mp3.stat().st_size > 200:
                    return
            except Exception as e:
                if attempt == 3:
                    raise e
                await asyncio.sleep(1.2 * (attempt + 1))


def decode_audio_stereo(path: Path) -> np.ndarray:
    cmd = [
        "ffmpeg", "-y", "-i", str(path),
        "-f", "f32le", "-acodec", "pcm_f32le",
        "-ac", "2", "-ar", str(SR), "-"
    ]
    res = subprocess.run(cmd, capture_output=True, check=True)
    arr = np.frombuffer(res.stdout, dtype=np.float32)
    return arr.reshape(-1, 2)


def make_note(freq: float, dur: float, amp: float = 0.12, kind: str = "piano") -> np.ndarray:
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False, dtype=np.float32)
    if kind == "piano":
        # Warm felt-piano tone: fundamental + soft 2nd/3rd harmonics + exponential decay
        env = np.minimum(1.0, t / 0.018) * np.exp(-t * 2.4)
        sig = (
            np.sin(2 * np.pi * freq * t)
            + 0.32 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t * 4.0)
            + 0.10 * np.sin(2 * np.pi * freq * 3.0 * t) * np.exp(-t * 6.0)
        ) * env * amp
    elif kind == "pad":
        env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7
        sigL = (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * (freq * 1.003) * t) + 0.25 * np.sin(2 * np.pi * freq * 0.5 * t)) * env * amp
        sigR = (np.sin(2 * np.pi * (freq * 0.997) * t) + 0.4 * np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 0.5 * t)) * env * amp
        return np.stack([sigL, sigR], axis=1).astype(np.float32)
    else:  # pulse bass
        env = np.minimum(1.0, t / 0.008) * np.exp(-t * 7.5)
        sig = np.tanh((np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2 * t)) * 1.8) * env * amp
    pan = 0.08 * math.sin(freq)
    return np.stack([sig * (1 - pan), sig * (1 + pan)], axis=1).astype(np.float32)


def add_clip(buf: np.ndarray, clip: np.ndarray, start_sec: float, gain: float = 1.0):
    i0 = max(0, int(start_sec * SR))
    if i0 >= buf.shape[0]:
        return
    i1 = min(buf.shape[0], i0 + clip.shape[0])
    buf[i0:i1] += clip[: i1 - i0] * gain


def synth_sfx(tag: str) -> np.ndarray:
    rng = np.random.default_rng(abs(hash(tag)) % 10000)
    if tag == "subdrop":
        dur = 1.8
        t = np.linspace(0, dur, int(dur * SR), endpoint=False, dtype=np.float32)
        f = 95.0 * np.exp(-t * 1.5) + 28.0
        phase = 2 * np.pi * np.cumsum(f) / SR
        sig = np.sin(phase) * np.exp(-t * 1.4) * 0.48
        return np.stack([sig, sig], axis=1)
    if tag == "boom" or tag == "megaboom":
        dur = 2.6 if tag == "megaboom" else 1.5
        amp = 0.62 if tag == "megaboom" else 0.38
        t = np.linspace(0, dur, int(dur * SR), endpoint=False, dtype=np.float32)
        f = 120.0 * np.exp(-t * 2.2) + 26.0
        phase = 2 * np.pi * np.cumsum(f) / SR
        noise = rng.normal(0, 1, t.shape[0]).astype(np.float32)
        # simple lowpass moving average on noise
        noise = np.convolve(noise, np.ones(32, dtype=np.float32) / 32.0, mode="same")
        sig = (np.sin(phase) * 0.75 + noise * 0.55) * np.exp(-t * (1.3 if tag == "megaboom" else 2.2)) * amp
        return np.stack([sig, sig * 0.96], axis=1)
    if tag == "whoosh":
        dur = 0.75
        t = np.linspace(0, dur, int(dur * SR), endpoint=False, dtype=np.float32)
        noise = rng.normal(0, 1, t.shape[0]).astype(np.float32)
        noise = np.convolve(noise, np.ones(14, dtype=np.float32) / 14.0, mode="same")
        env = np.sin(np.pi * (t / dur)) ** 1.8
        return np.stack([noise * env * 0.22 * (1 - t / dur), noise * env * 0.22 * (t / dur + 0.3)], axis=1)
    if tag == "ripple" or tag == "chime":
        dur = 1.1
        t = np.linspace(0, dur, int(dur * SR), endpoint=False, dtype=np.float32)
        f1 = 880.0 if tag == "chime" else 660.0
        sig = (np.sin(2 * np.pi * f1 * t) + 0.5 * np.sin(2 * np.pi * f1 * 1.5 * t)) * np.exp(-t * 4.2) * 0.18
        return np.stack([sig, sig], axis=1)
    if tag == "siren":
        dur = 1.6
        t = np.linspace(0, dur, int(dur * SR), endpoint=False, dtype=np.float32)
        mod = 680.0 + 180.0 * np.sin(2 * np.pi * 2.5 * t)
        phase = 2 * np.pi * np.cumsum(mod) / SR
        sig = np.sin(phase) * np.sin(np.pi * t / dur) * 0.13
        return np.stack([sig, sig], axis=1)
    if tag == "laser" or tag == "zap" or tag == "emp":
        dur = 1.3 if tag == "emp" else 0.65
        t = np.linspace(0, dur, int(dur * SR), endpoint=False, dtype=np.float32)
        f0 = 1400.0 if tag != "emp" else 900.0
        f = f0 * np.exp(-t * (3.5 if tag == "emp" else 7.0)) + 55.0
        phase = 2 * np.pi * np.cumsum(f) / SR
        buzz = np.sign(np.sin(phase * 1.5)) * 0.25 + np.sin(phase) * 0.75
        sig = buzz * np.exp(-t * (2.2 if tag == "emp" else 4.8)) * 0.24
        return np.stack([sig, sig], axis=1).astype(np.float32)
    if tag == "boing":
        dur = 0.9
        t = np.linspace(0, dur, int(dur * SR), endpoint=False, dtype=np.float32)
        f = 135.0 + 210.0 * (t / dur) + 35.0 * np.sin(2 * np.pi * 16 * t)
        phase = 2 * np.pi * np.cumsum(f) / SR
        sig = np.sin(phase) * np.exp(-t * 3.2) * 0.30
        return np.stack([sig, sig], axis=1).astype(np.float32)
    if tag == "heartbeat":
        dur = 1.8
        t = np.linspace(0, dur, int(dur * SR), endpoint=False, dtype=np.float32)
        sig = np.zeros_like(t)
        for off in [0.0, 0.28, 0.95, 1.23]:
            dt = np.maximum(0.0, t - off)
            mask = (t >= off).astype(np.float32)
            sig += mask * np.sin(2 * np.pi * 52.0 * dt) * np.exp(-dt * 14.0) * 0.42
        return np.stack([sig, sig], axis=1)
    # weld / crack / hum fallback
    dur = 0.8
    t = np.linspace(0, dur, int(dur * SR), endpoint=False, dtype=np.float32)
    noise = rng.normal(0, 1, t.shape[0]).astype(np.float32) * np.exp(-t * 5.0) * 0.18
    return np.stack([noise, noise], axis=1)


def build_cinematic_music() -> np.ndarray:
    total_samples = int(TOTAL_SECONDS * SR)
    music = np.zeros((total_samples, 2), dtype=np.float32)

    # Chord roots (D minor cinematic progression: Dm - Bb - F - C / Gm - Dm - A - Dm)
    prog_calm = [
        (146.83, [293.66, 349.23, 440.00, 587.33]),  # Dm
        (116.54, [233.08, 293.66, 349.23, 466.16]),  # Bb
        (174.61, [261.63, 349.23, 440.00, 523.25]),  # F
        (130.81, [261.63, 329.63, 392.00, 523.25]),  # C
    ]
    prog_heroic = [
        (116.54, [233.08, 349.23, 466.16, 587.33]),  # Bb maj7
        (130.81, [261.63, 392.00, 523.25, 659.25]),  # C
        (146.83, [293.66, 440.00, 587.33, 698.46]),  # Dm
        (174.61, [349.23, 440.00, 523.25, 698.46]),  # F
    ]

    t_cursor = 0.0
    bar_idx = 0
    while t_cursor < TOTAL_SECONDS:
        # Silence dramatic window right at Impact (419.5s .. 423.8s)!
        if 419.2 <= t_cursor <= 423.5:
            t_cursor += 0.5
            continue

        is_build_or_action = (78.0 <= t_cursor < 263.0) or (375.0 <= t_cursor < 419.0)
        is_tense = 263.0 <= t_cursor < 375.0
        is_dawn = t_cursor >= 440.0

        prog = prog_heroic if (t_cursor >= 375.0) else prog_calm
        root, arp = prog[bar_idx % 4]
        bar_dur = 3.2 if not is_build_or_action else 2.4

        # Warm stereo cinema pad
        pad_gain = 0.075 if not is_tense else 0.055
        add_clip(music, make_note(root, bar_dur * 1.15, amp=pad_gain, kind="pad"), t_cursor)

        if is_build_or_action:
            # Driving Stranger-Things / Dark-Knight 8th-note synth bass pulse + top arpeggio
            step = bar_dur / 8.0
            for s in range(8):
                add_clip(music, make_note(root * 0.5, step * 0.9, amp=0.11, kind="pulse"), t_cursor + s * step)
                if s % 2 == 0:
                    add_clip(music, make_note(arp[(s // 2) % 4], step * 1.8, amp=0.065, kind="piano"), t_cursor + s * step)
        elif is_tense:
            # Ticking sparse high piano + deep sub pulse
            add_clip(music, make_note(root * 0.5, bar_dur, amp=0.08, kind="pad"), t_cursor)
            add_clip(music, make_note(arp[0] * 1.5, 1.4, amp=0.055, kind="piano"), t_cursor + 0.2)
            add_clip(music, make_note(arp[1] * 1.5, 1.4, amp=0.045, kind="piano"), t_cursor + bar_dur * 0.55)
        else:
            # @IfverseTales signature felt-piano arpeggio (Act 1 & Act 6 Golden Dawn)
            step = bar_dur / 4.0
            for s in range(4):
                freq = arp[s] * (1.0 if not is_dawn else 1.0)
                add_clip(music, make_note(freq, step * 2.2, amp=0.085, kind="piano"), t_cursor + s * step)

        t_cursor += bar_dur
        bar_idx += 1

    return music


async def main():
    TMP_VO_DIR.mkdir(parents=True, exist_ok=True)
    OUT_AUDIO.parent.mkdir(parents=True, exist_ok=True)
    OUT_TIMELINE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Synthesizing {len(SCRIPT)} multi-voice US English lines via Edge Neural TTS...")
    sem = asyncio.Semaphore(6)
    tasks = []
    for i, (_, _, speaker, text, _) in enumerate(SCRIPT):
        mp3_path = TMP_VO_DIR / f"line_{i:03d}.mp3"
        tasks.append(synth_one(i, speaker, text, mp3_path, sem))
    await asyncio.gather(*tasks)
    print("All TTS clips generated! Decoding & assembling studio timeline...")

    total_samples = int(TOTAL_SECONDS * SR)
    vo_bus = np.zeros((total_samples, 2), dtype=np.float32)
    sfx_bus = np.zeros((total_samples, 2), dtype=np.float32)

    timeline_entries = []
    next_min_sec = 0.5

    for i, (target_sec, act, speaker, text, sfx_tag) in enumerate(SCRIPT):
        mp3_path = TMP_VO_DIR / f"line_{i:03d}.mp3"
        clip = decode_audio_stereo(mp3_path)
        # Trim leading/trailing digital silence (> 0.004 threshold)
        mono = np.abs(clip).mean(axis=1)
        nz = np.where(mono > 0.004)[0]
        if nz.size > 10:
            i_start = max(0, int(nz[0]) - int(0.03 * SR))
            i_end = min(clip.shape[0], int(nz[-1]) + int(0.06 * SR))
            clip = clip[i_start:i_end]

        # Normalize per-clip peak cleanly
        pk = float(np.max(np.abs(clip))) if clip.size else 1.0
        if pk > 0.01:
            clip = clip * (0.82 / pk)

        actual_start = max(target_sec, next_min_sec)
        dur_sec = clip.shape[0] / SR
        actual_end = actual_start + dur_sec

        add_clip(vo_bus, clip, actual_start, gain=1.0)
        if sfx_tag:
            sfx_clip = synth_sfx(sfx_tag)
            sfx_offset = actual_start - 0.12 if sfx_tag in ("boom", "megaboom", "subdrop", "emp") else actual_start + dur_sec * 0.35
            add_clip(sfx_bus, sfx_clip, max(0.0, sfx_offset), gain=0.85)

        timeline_entries.append({
            "id": i,
            "act": act,
            "speaker": speaker,
            "text": text,
            "startSec": round(actual_start, 3),
            "endSec": round(actual_end, 3),
            "startFrame": int(round(actual_start * FPS)),
            "endFrame": int(round(actual_end * FPS)),
            "sfx": sfx_tag,
        })
        next_min_sec = actual_end + 0.38

    print(f"Final spoken line ends at {next_min_sec:.2f}s / {TOTAL_SECONDS}s")

    print("Synthesizing 6-act @IfverseTales cinematic score & sidechain ducking...")
    music_bus = build_cinematic_music()

    # Smooth sidechain ducking envelope from VO energy (window ~150ms)
    vo_env = np.max(np.abs(vo_bus), axis=1)
    win = int(0.18 * SR)
    kernel = np.ones(win, dtype=np.float32) / win
    vo_smooth = np.convolve(vo_env, kernel, mode="same")
    duck_gain = np.clip(1.0 - np.minimum(1.0, vo_smooth * 5.0) * 0.62, 0.36, 1.0)[:, None]

    master = vo_bus * 1.05 + music_bus * duck_gain + sfx_bus * 0.90
    # Soft broadcast limiter
    master = np.tanh(master * 1.15) * 0.92

    # Fade out final 2.5 seconds cleanly
    fade_n = int(2.5 * SR)
    master[-fade_n:] *= np.linspace(1.0, 0.0, fade_n, dtype=np.float32)[:, None]

    # Encode MP3 via ffmpeg stdin
    cmd = [
        "ffmpeg", "-y",
        "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(OUT_AUDIO)
    ]
    proc = subprocess.run(cmd, input=master.astype(np.float32).tobytes(), capture_output=True, check=True)
    print(f"Saved studio master audio -> {OUT_AUDIO} ({OUT_AUDIO.stat().st_size / 1e6:.2f} MB)")

    ts_code = (
        "// Auto-generated by scripts/build_day04_audio.py — Frame-accurate VO & Beat Timeline\n"
        "export type SpeakerId = 'narrator' | 'orange' | 'blue' | 'ai' | 'agent';\n\n"
        "export interface CineLine {\n"
        "  readonly id: number;\n"
        "  readonly act: number;\n"
        "  readonly speaker: SpeakerId;\n"
        "  readonly text: string;\n"
        "  readonly startSec: number;\n"
        "  readonly endSec: number;\n"
        "  readonly startFrame: number;\n"
        "  readonly endFrame: number;\n"
        "  readonly sfx: string | null;\n"
        "}\n\n"
        f"export const DAY04_TOTAL_FRAMES = {TOTAL_FRAMES}; // {TOTAL_SECONDS}s = 08:24 @ 30fps\n\n"
        f"export const DAY04_LINES: readonly CineLine[] = {json.dumps(timeline_entries, indent=2)} as const;\n\n"
        "export function getActiveLine(frame: number): CineLine | null {\n"
        "  for (const l of DAY04_LINES) {\n"
        "    if (frame >= l.startFrame && frame <= l.endFrame) return l;\n"
        "  }\n"
        "  return null;\n"
        "}\n\n"
        "export function isSpeakerTalking(frame: number, speaker: SpeakerId): boolean {\n"
        "  const l = getActiveLine(frame);\n"
        "  return l !== null && l.speaker === speaker;\n"
        "}\n"
    )
    OUT_TIMELINE.write_text(ts_code, encoding="utf-8")
    print(f"Saved TypeScript timeline -> {OUT_TIMELINE} ({len(timeline_entries)} lines)")


if __name__ == "__main__":
    asyncio.run(main())
