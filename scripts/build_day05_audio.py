import asyncio
import json
import math
import os
import subprocess
from pathlib import Path
import edge_tts
import numpy as np

STUDIO_DIR = Path(r"C:\Users\samet\.gemini\antigravity\scratch\stickman-us-studio")
TMP_VO_DIR = STUDIO_DIR / "out" / "vo_day05_tmp"
OUT_AUDIO = STUDIO_DIR / "public" / "audio" / "day05_master.mp3"
OUT_TIMELINE = STUDIO_DIR / "src" / "day5" / "day05Timeline.ts"

SR = 44100
FPS = 30
TOTAL_SECONDS = 604.0  # 10:04 (10m 04s = 18,120 frames -> Full 10-Min US Mid-Roll Movie!)
TOTAL_FRAMES = int(TOTAL_SECONDS * FPS)

# FAST, URGENT HOLLYWOOD DELIVERY (Zero slow documentary narrator! +28% to +35% crisp speed!)
VOICES = {
    "orange": ("en-US-BrianNeural", "+30%", "+2Hz"),
    "blue_weapon": ("en-US-ChristopherNeural", "+28%", "-8Hz"),  # Cold Winter-Soldier masked cadence
    "blue_real": ("en-US-AndrewNeural", "+26%", "+0Hz"),         # Real Blue breaking through
    "handler": ("en-US-EricNeural", "+32%", "-6Hz"),             # Cold Syndicate Tactical Comms
    "hud": ("en-US-AriaNeural", "+36%", "+4Hz"),                 # Crisp tactical visor HUD
}

# Tight, breathless, razor-sharp movie lines ONLY (no narrator!)
# Tuple: (target_sec, act, speaker, text, radio_fx)
DIALOGUE_SCRIPT = [
    # === ACT 1: HIGHWAY AMBUSH — KRAV MAGA & KNIFE DISARMS (00:00 - 01:35) ===
    (1.2, 1, "handler", "Convoy intercepted on Overpass Nine. Release Asset Zero.", True),
    (5.8, 1, "hud", "Neural override locked. Target: Orange. Terminate.", True),
    (11.5, 1, "orange", "Wait— that jacket... Blue?! Bro, where have you been?!", False),
    (16.2, 1, "blue_weapon", "Target confirmed.", True),
    (25.5, 1, "orange", "Whoa—! Watch the blade! Blue, snap out of it, it's me!", False),
    (38.0, 1, "orange", "Titanium arm?! What did they do to you?!", False),
    (52.0, 1, "handler", "Don't let him breathe. Break his guard.", True),
    (66.5, 1, "orange", "Alright... you want hands?! Lose the knife!", False),
    (83.0, 1, "blue_weapon", "Rerouting combat protocol.", True),
    (89.5, 1, "orange", "Hold tight— glass below!", False),

    # === ACT 2: SUBWAY TUNNEL — BOXING VS WING CHUN (01:35 - 03:20) ===
    (98.5, 2, "hud", "Subterranean transit level. Switching to heavy strike mode.", True),
    (110.0, 2, "orange", "Ripped my favorite hoodie... Now I'm mad.", False),
    (126.0, 2, "orange", "Heavy boxing, huh? Too wide— centerline's mine!", False),
    (148.5, 2, "blue_weapon", "Strike velocity... adapting.", True),
    (166.0, 2, "handler", "He's trapping your reach! Drive him through the wall!", True),
    (184.0, 2, "orange", "Train track! Move!", False),
    (194.5, 2, "orange", "Through the warehouse door—!", False),

    # === ACT 3: CARGO WAREHOUSE — JACKIE CHAN PROP COMBAT & FIRST EXHAUSTION (03:20 - 05:10) ===
    (203.5, 3, "orange", "Okay, metal arm hurts. Need leverage... Chair!", False),
    (222.0, 3, "orange", "Sit down! ...Okay, don't sit down!", False),
    (240.0, 3, "hud", "Warning. Improvised obstacle interference.", True),
    (246.5, 3, "orange", "Eight-foot ladder, baby! Try punching through rungs!", False),
    (268.0, 3, "orange", "Hoodie wrap— spin!", False),
    # First Heavy Exhaustion / Catching Breath Tension Beat (280s - 309s)
    (283.5, 3, "orange", "Hah... hah... Damn, bro... you don't even blink, do you?", False),
    (292.0, 3, "handler", "Asset Zero, pain suppressors failing. Boosting adrenaline two hundred percent.", True),
    (301.5, 3, "blue_weapon", "Compliance... active.", True),
    (306.5, 3, "orange", "Oh, come on— he just got faster?!", False),

    # === ACT 4: PENTHOUSE DOJO — KYOKUSHIN KARATE, JUDO THROWS & GRAPPLING (05:10 - 06:55) ===
    (315.0, 4, "orange", "Penthouse dojo?! Fine— old school!", False),
    (336.0, 4, "hud", "Impact force critical. Bone density threshold exceeded.", True),
    (355.0, 4, "orange", "Your metal arm's heavy— use your own weight! Hup—!", False),
    (376.0, 4, "blue_weapon", "Choke hold... locked.", True),
    (386.5, 4, "orange", "Nngh— not... blacking... out!", False),
    (405.0, 4, "orange", "Out the window— brace!", False),

    # === ACT 5: STORM HELIPAD — ULTIMATE EXHAUSTION, RISING TENSION & ALL-OUT BRAWL (06:55 - 08:45) ===
    # Suffocating 30s Shepard-Tone Standoff (415s - 445s)
    (418.0, 5, "orange", "Hah... hah... Eighty floors up. Nowhere left to run.", False),
    (426.5, 5, "hud", "Error. Memory fragment leak detected. Suppressing.", True),
    (432.5, 5, "blue_real", "Nngh... Or...ange...?", False),
    (436.5, 5, "handler", "Wipe his cortex NOW! Kill him!", True),
    (441.5, 5, "orange", "I'm not giving up on you! Bring it!", False),
    # Desperate Brutal Brawl (445s - 525s)
    (468.0, 5, "orange", "Remember the rooftop?! One-dollar bunker?! That was US!", False),
    (492.0, 5, "blue_weapon", "Stop... talking!", True),
    (512.0, 5, "hud", "Target pinned. Executing fatal strike.", True),
    (520.0, 5, "orange", "Look me in the eyes, brother!", False),

    # === ACT 6: SHATTERING THE MASK — BROTHERHOOD & 5-VISOR CLIFFHANGER (08:45 - 10:04) ===
    (531.0, 6, "orange", "I'm aiming for the mask... NOT YOU! HAAAH!", False),
    (544.5, 6, "hud", "Neural link... severed. System... offline.", True),
    (554.0, 6, "blue_real", "Hah... Orange...? My hands... what did I do?!", False),
    (563.5, 6, "orange", "Easy, bro... breathe. Welcome back. You hit like a freight train.", False),
    (573.0, 6, "blue_real", "You stayed... even when I tried to kill you.", False),
    (580.5, 6, "orange", "Always. Best friends don't fold.", False),
    # Cliffhanger (585s - 604s)
    (586.5, 6, "handler", "impressive. Asset Zero-One broken... Activate Squad Two through Six.", True),
    (595.0, 6, "blue_real", "Orange... look at the next roof.", False),
    (599.2, 6, "orange", "Five more?! ...Let 'em come.", False),
]


def trim_silence(samples: np.ndarray, thresh: float = 0.015, pad_ms: int = 25) -> np.ndarray:
    """Strip ALL leading and trailing dead air from TTS so speech is razor-snappy!"""
    if len(samples) == 0:
        return samples
    abs_s = np.abs(samples)
    idx = np.where(abs_s > thresh)[0]
    if len(idx) == 0:
        return samples[: int(0.1 * SR)]
    pad = int((pad_ms / 1000.0) * SR)
    start = max(0, idx[0] - pad)
    end = min(len(samples), idx[-1] + pad)
    return samples[start:end]


def apply_radio_filter(samples: np.ndarray) -> np.ndarray:
    """Crisp Winter-Soldier tactical comms / mask distortion."""
    if len(samples) < 16:
        return samples
    # High-pass + subtle overdrive saturation
    diff = np.diff(samples, prepend=samples[0]) * 2.1
    driven = np.tanh(diff * 2.4) * 0.78 + samples * 0.32
    return np.clip(driven, -0.98, 0.98).astype(np.float32)


async def synth_one_clip(idx: int, t_sec: float, act: int, speaker: str, text: str, radio_fx: bool, sem: asyncio.Semaphore):
    mp3_path = TMP_VO_DIR / f"d5_line_{idx:03d}.mp3"
    voice, rate, pitch = VOICES[speaker]
    async with sem:
        if not mp3_path.exists() or mp3_path.stat().st_size < 200:
            for attempt in range(4):
                try:
                    comm = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
                    await comm.save(str(mp3_path))
                    if mp3_path.exists() and mp3_path.stat().st_size > 200:
                        break
                except Exception as e:
                    if attempt == 3:
                        raise e
                    await asyncio.sleep(1.0 * (attempt + 1))

    raw = subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(mp3_path),
            "-f", "f32le", "-acodec", "pcm_f32le",
            "-ac", "1", "-ar", str(SR), "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=True,
    ).stdout
    samples = np.frombuffer(raw, dtype=np.float32).copy()
    samples = trim_silence(samples, thresh=0.018, pad_ms=18)
    mx = np.max(np.abs(samples))
    if mx > 1e-4:
        samples = samples / mx
    # Crisp movie dialogue punch compression
    samples = np.tanh(samples * 1.45) * 0.92
    if radio_fx:
        samples = apply_radio_filter(samples)
    return (idx, t_sec, act, speaker, text, radio_fx, samples.astype(np.float32))


async def generate_tts_clips():
    TMP_VO_DIR.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(6)
    tasks = [
        synth_one_clip(idx, t_sec, act, speaker, text, radio_fx, sem)
        for idx, (t_sec, act, speaker, text, radio_fx) in enumerate(DIALOGUE_SCRIPT)
    ]
    results = await asyncio.gather(*tasks)
    return sorted(results, key=lambda x: x[0])


def lowpass_noise(rng: np.random.Generator, n: int, taps: int = 12) -> np.ndarray:
    raw = rng.standard_normal(n).astype(np.float32)
    kernel = np.hanning(taps + 2)[1:-1].astype(np.float32)
    kernel /= np.sum(kernel)
    return np.convolve(raw, kernel, mode="same")


def make_combat_sfx(rng: np.random.Generator):
    """Synthesize dark, gritty, realistic Hollywood flesh/bone/leather/metal foley (ZERO sine beeps!)."""
    lib = {}

    def env_exp(n, decay):
        t = np.linspace(0, n / SR, n, endpoint=False, dtype=np.float32)
        return t, np.exp(-t * decay)

    # 1. Snappy Leather Jab / Wing Chun Palm-Knuckle Snap
    n = int(0.095 * SR)
    t, e = env_exp(n, 46.0)
    leather = lowpass_noise(rng, n, taps=6) * 0.9
    thud = np.sin(2 * np.pi * (135 * np.exp(-t * 32)) * t) * 0.95
    lib["jab"] = (np.tanh((thud + leather) * 1.5) * e * 0.78).astype(np.float32)

    # 2. Heavy Boxing / Kyokushin Bone & Liver Impact
    n = int(0.24 * SR)
    t, e = env_exp(n, 19.0)
    leather = lowpass_noise(rng, n, taps=8) * 0.85
    sub = np.sin(2 * np.pi * (86 * np.exp(-t * 16) + 32) * t) * 1.35
    snap = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 68.0) * 0.55
    lib["heavy_hit"] = (np.tanh((sub + leather + snap) * 1.5) * e * 0.94).astype(np.float32)

    # 3. Wing Chun 8-Hit Chain Punch Flurry (rapid machine-gun leather/chest thuds!)
    n_flurry = int(0.68 * SR)
    flurry = np.zeros(n_flurry, dtype=np.float32)
    for k in range(8):
        pos = int((k * 0.078) * SR)
        seg = lib["jab"]
        end = min(n_flurry, pos + len(seg))
        flurry[pos:end] += seg[: end - pos] * (0.76 + 0.03 * k)
    lib["wing_chun_flurry"] = np.clip(flurry, -0.95, 0.95)

    # 4. Fast Whip Kick / Coat Air Whoosh
    n = int(0.16 * SR)
    t = np.linspace(0, 0.16, n, endpoint=False, dtype=np.float32)
    bell = np.sin(np.pi * (t / 0.16)) ** 1.8
    air = lowpass_noise(rng, n, taps=16)
    lib["whoosh"] = (air * bell * 0.82).astype(np.float32)

    # 5. Krav Maga Knife Parry / Steel Scrape (Crisp 55ms metallic transient, NO pure sine beep!)
    n = int(0.12 * SR)
    t, e = env_exp(n, 38.0)
    hiss = np.diff(rng.standard_normal(n).astype(np.float32), prepend=0.0) * 0.65
    steel_thud = np.sin(2 * np.pi * (180 * np.exp(-t * 25)) * t) * 0.6
    shimmer = np.sin(2 * np.pi * 1680 * t + np.sin(2 * np.pi * 410 * t) * 3.5) * np.exp(-t * 58.0) * 0.28
    lib["knife_spark"] = (np.tanh((hiss + steel_thud + shimmer) * 1.3) * e * 0.72).astype(np.float32)

    # 6. Winter Soldier Bionic Gauntlet Heavy Mechanical Thud (Low hydraulic growl + steel click!)
    n = int(0.20 * SR)
    t, e = env_exp(n, 22.0)
    growl = np.tanh(np.sin(2 * np.pi * (92 + 35 * np.exp(-t * 18)) * t) * 2.4) * 0.65
    click = np.diff(lowpass_noise(rng, n, taps=4), prepend=0.0) * np.exp(-t * 52.0) * 0.9
    lib["bionic"] = ((growl + click) * e * 0.78).astype(np.float32)

    # 7. Jackie Chan Folding Chair / Aluminum Ladder Hollow Impact
    n = int(0.24 * SR)
    t, e = env_exp(n, 20.0)
    hollow = (
        np.sin(2 * np.pi * (240 * np.exp(-t * 8)) * t) * 0.6
        + np.sin(2 * np.pi * 590 * t + np.sin(2 * np.pi * 190 * t) * 2.5) * np.exp(-t * 32.0) * 0.35
        + lowpass_noise(rng, n, taps=5) * np.exp(-t * 36.0) * 0.75
    )
    lib["metal_prop"] = (np.tanh(hollow * 1.5) * e * 0.84).astype(np.float32)

    # 8. Clothing Rip (Fibrous fabric tear!)
    n = int(0.28 * SR)
    t = np.linspace(0, 0.28, n, endpoint=False, dtype=np.float32)
    rip_env = np.sin(np.pi * (t / 0.28)) * (0.6 + 0.4 * np.sin(2 * np.pi * 62 * t))
    diff_n = np.diff(lowpass_noise(rng, n, taps=3), prepend=0.0)
    lib["cloth_rip"] = np.clip(diff_n * rip_env * 0.85, -0.9, 0.9).astype(np.float32)

    # 9. Judo Throw / Body Slam + Crate Smash
    n = int(0.46 * SR)
    t, e = env_exp(n, 9.0)
    boom = np.sin(2 * np.pi * (68 * np.exp(-t * 8.0) + 28) * t) * 1.35
    debris = lowpass_noise(rng, n, taps=7) * np.exp(-t * 13.0) * 0.95
    lib["body_slam"] = (np.tanh((boom + debris) * 1.45) * e * 0.95).astype(np.float32)

    # 10. Glass Skylight / Mask Shatter
    n = int(0.52 * SR)
    t, e = env_exp(n, 9.5)
    shards = np.diff(rng.standard_normal(n).astype(np.float32), prepend=0.0) * 0.85
    sub_hit = np.sin(2 * np.pi * (82 * np.exp(-t * 11) + 30) * t) * 0.95
    lib["glass_shatter"] = (np.tanh((shards + sub_hit) * 1.35) * e * 0.92).astype(np.float32)

    # 11. Heavy Exhausted Breath Cycle (Inhale + Exhale)
    n_b = int(0.85 * SR)
    tb = np.linspace(0, 0.85, n_b, endpoint=False, dtype=np.float32)
    inhale = np.exp(-((tb - 0.18) ** 2) / 0.009) * 0.58
    exhale = np.exp(-((tb - 0.56) ** 2) / 0.018) * 0.88
    air = lowpass_noise(rng, n_b, taps=18)
    lib["pant"] = (air * (inhale + exhale) * 0.72).astype(np.float32)

    # 12. Deep Heartbeat Lub-Dub
    n_hb = int(0.38 * SR)
    th = np.linspace(0, 0.38, n_hb, endpoint=False, dtype=np.float32)
    lub = np.sin(2 * np.pi * 46 * th) * np.exp(-((th - 0.05) ** 2) / 0.0014)
    dub = np.sin(2 * np.pi * 54 * th) * np.exp(-((th - 0.21) ** 2) / 0.0016) * 0.84
    lib["heartbeat"] = ((lub + dub) * 0.92).astype(np.float32)

    # 13. Dark Zimmer Low-Brass BRAAM
    n_br = int(1.65 * SR)
    tbr = np.linspace(0, 1.65, n_br, endpoint=False, dtype=np.float32)
    ebr = np.minimum(1.0, tbr * 18.0) * np.exp(-tbr * 2.1)
    saw = (
        np.sin(2 * np.pi * 43.65 * tbr)
        + 0.7 * np.tanh(np.sin(2 * np.pi * 87.31 * tbr) * 2.6)
        + 0.45 * np.tanh(np.sin(2 * np.pi * 130.81 * tbr) * 2.2)
    )
    lib["braam"] = (np.tanh(saw * 1.8) * ebr * 0.92).astype(np.float32)

    return lib


def build_choreography_impacts(rng: np.random.Generator):
    """
    Generate dense, rhythmic martial-arts impact & foley timeline across all 6 Acts!
    Returns list of (sec, kind, intensity) used BOTH for audio mixing AND Remotion camera shake/sparks!
    """
    events = []

    def add_flurry(start_s, end_s, step_s, kinds, base_int=0.75):
        t = start_s
        i = 0
        while t < end_s:
            k = kinds[i % len(kinds)]
            events.append((round(t, 3), k, round(base_int + (i % 3) * 0.08, 2)))
            t += step_s * (0.82 + 0.36 * ((i * 7) % 5) / 4.0)
            i += 1

    # ACT 1: Highway Krav Maga & Knife Disarms (0 - 95s)
    events.append((0.3, "braam", 0.9))
    events.append((3.4, "body_slam", 0.85))  # Van crash!
    events.append((7.8, "bionic", 0.8))
    add_flurry(17.2, 25.0, 0.42, ["whoosh", "knife_spark", "jab", "knife_spark", "heavy_hit"], 0.8)
    add_flurry(28.0, 37.5, 0.38, ["knife_spark", "bionic", "jab", "whoosh", "heavy_hit"], 0.82)
    events.append((36.4, "cloth_rip", 0.95))  # Stage 1 Chest Slash Rip!
    add_flurry(40.5, 51.5, 0.36, ["whoosh", "jab", "knife_spark", "heavy_hit", "bionic"], 0.85)
    add_flurry(54.5, 66.0, 0.34, ["knife_spark", "jab", "jab", "heavy_hit", "body_slam"], 0.86)
    add_flurry(69.0, 82.5, 0.35, ["bionic", "knife_spark", "heavy_hit", "whoosh", "jab"], 0.88)
    events.append((74.2, "knife_spark", 1.0))  # Disarm kick!
    add_flurry(85.0, 91.5, 0.40, ["heavy_hit", "bionic", "body_slam"], 0.9)
    events.append((92.0, "glass_shatter", 1.0))  # Crash through skylight into Subway!

    # ACT 2: Subway Boxing vs Wing Chun (95 - 200s)
    events.append((95.2, "body_slam", 0.92))
    events.append((108.5, "cloth_rip", 0.9))  # Knuckle wrap rip!
    add_flurry(113.0, 125.5, 0.44, ["whoosh", "heavy_hit", "heavy_hit", "bionic"], 0.85)  # Heavy Boxing!
    # Wing Chun Chain Punches + Boxing Exchanges
    for w_t in [129.0, 134.5, 141.0, 152.5, 160.0, 173.5]:
        events.append((w_t, "wing_chun_flurry", 0.92))
        events.append((w_t + 0.82, "heavy_hit", 0.95))
    add_flurry(130.2, 165.0, 0.46, ["jab", "whoosh", "bionic", "heavy_hit"], 0.80)
    events.append((156.8, "cloth_rip", 0.95))  # Stage 2 Sleeve Torn Off!
    add_flurry(169.0, 193.5, 0.36, ["jab", "heavy_hit", "bionic", "whoosh", "body_slam"], 0.88)
    events.append((196.2, "body_slam", 1.0))  # Smash through warehouse doors!

    # ACT 3: Warehouse Jackie Chan Prop-Fu + Exhaustion Beat (200 - 310s)
    add_flurry(206.5, 221.5, 0.40, ["metal_prop", "whoosh", "jab", "metal_prop", "heavy_hit"], 0.85)  # Folding Chair!
    add_flurry(225.0, 239.5, 0.38, ["metal_prop", "bionic", "metal_prop", "body_slam"], 0.86)
    add_flurry(249.5, 267.0, 0.36, ["metal_prop", "whoosh", "metal_prop", "jab", "heavy_hit"], 0.88)  # 8-ft Ladder!
    events.append((269.2, "cloth_rip", 0.95))  # Jacket-Fu whip!
    add_flurry(270.0, 279.0, 0.38, ["whoosh", "jab", "heavy_hit", "body_slam"], 0.92)
    events.append((279.5, "body_slam", 1.0))  # Double crate explosion crash!
    # 280s - 306s: First Exhaustion / Panting & Heartbeat Tension Beat!
    for bt in np.arange(280.8, 305.5, 1.05):
        events.append((round(float(bt), 3), "pant", 0.78))
    for hbt in np.arange(281.5, 306.0, 0.72):
        events.append((round(float(hbt), 3), "heartbeat", 0.75))
    events.append((300.2, "bionic", 0.95))
    events.append((308.5, "glass_shatter", 1.0))  # Launched up into Penthouse Dojo!

    # ACT 4: Penthouse Dojo — Kyokushin Karate, Judo Throws & Grappling (310 - 415s)
    add_flurry(318.0, 335.5, 0.38, ["whoosh", "heavy_hit", "jab", "heavy_hit", "bionic"], 0.88)
    add_flurry(339.0, 354.5, 0.36, ["whoosh", "jab", "heavy_hit", "cloth_rip", "heavy_hit"], 0.90)
    # Huge Judo Seoi-Nage Shoulder Throw!
    events.append((358.2, "whoosh", 0.95))
    events.append((359.0, "body_slam", 1.0))
    events.append((359.2, "braam", 0.78))
    add_flurry(362.5, 375.5, 0.42, ["heavy_hit", "bionic", "jab", "body_slam"], 0.88)
    # Ground Choke Struggle (Heartbeat + Bionic strain)
    for hbt in np.arange(377.0, 389.0, 0.55):
        events.append((round(float(hbt), 3), "heartbeat", 0.90))
    events.append((389.8, "heavy_hit", 1.0))  # Escape kick!
    add_flurry(391.5, 404.5, 0.34, ["whoosh", "heavy_hit", "wing_chun_flurry", "bionic"], 0.92)
    events.append((407.2, "glass_shatter", 1.0))  # Crash out onto Storm Helipad!
    events.append((408.0, "body_slam", 0.95))

    # ACT 5: Storm Helipad — 30s Suffocating Shepard-Tone Standoff + Desperate Brawl (415 - 525s)
    for bt in np.arange(415.0, 443.5, 0.95):
        events.append((round(float(bt), 3), "pant", 0.88))
    # Accelerating Heartbeat (70 BPM -> 175 BPM!)
    hb_t = 415.0
    hb_dt = 0.82
    while hb_t < 444.5:
        events.append((round(hb_t, 3), "heartbeat", round(min(1.0, 0.7 + (445 - hb_t) * -0.008 + 0.3), 2)))
        hb_t += hb_dt
        hb_dt = max(0.33, hb_dt * 0.968)
    events.append((444.8, "braam", 0.95))  # THE CHARGE!
    add_flurry(445.5, 467.5, 0.31, ["heavy_hit", "bionic", "jab", "heavy_hit", "whoosh", "cloth_rip"], 0.94)
    add_flurry(471.5, 491.5, 0.29, ["wing_chun_flurry", "heavy_hit", "bionic", "body_slam", "heavy_hit"], 0.96)
    add_flurry(494.5, 511.5, 0.32, ["heavy_hit", "bionic", "heavy_hit", "body_slam"], 0.98)
    # Pinned Concrete Smashes beside Orange's head!
    for p_t in [514.5, 516.8, 519.0]:
        events.append((p_t, "bionic", 0.95))
        events.append((p_t + 0.22, "body_slam", 1.0))

    # ACT 6: Catching the Bionic Fist, Shattering the Mask & 5-Visor Cliffhanger (525 - 604s)
    events.append((525.8, "bionic", 1.0))
    events.append((526.2, "heavy_hit", 1.0))  # Bare-handed catch shockwave!
    for hbt in np.arange(526.8, 533.5, 0.40):
        events.append((round(float(hbt), 3), "heartbeat", 0.95))
    events.append((534.2, "whoosh", 1.0))
    events.append((534.5, "glass_shatter", 1.0))  # MASK SHATTERS!
    events.append((534.6, "braam", 1.0))
    # Exhausted relief breaths
    for bt in np.arange(546.0, 560.0, 1.25):
        events.append((round(float(bt), 3), "pant", 0.65))
    # Cliffhanger 5-Visor Ignition!
    for v_i, v_t in enumerate([591.5, 592.3, 593.0, 593.6, 594.1]):
        events.append((v_t, "bionic", 0.85 + v_i * 0.03))
    events.append((600.8, "braam", 1.0))

    events.sort(key=lambda x: x[0])
    return events


def synthesize_hollywood_score(rng: np.random.Generator) -> np.ndarray:
    """
    Synthesize a 604-second stereo Hollywood Action & Rising Shepard-Tone Thriller Score!
    """
    n_total = int(TOTAL_SECONDS * SR)
    left = np.zeros(n_total, dtype=np.float32)
    right = np.zeros(n_total, dtype=np.float32)
    smooth_rain_k = np.ones(18, dtype=np.float32) / 18.0
    smooth_hat_k = np.array([1.0, -0.85], dtype=np.float32)

    chunk_sec = 4.0
    n_chunk = int(chunk_sec * SR)

    for start_idx in range(0, n_total, n_chunk):
        end_idx = min(n_total, start_idx + n_chunk)
        m = end_idx - start_idx
        t = np.linspace(start_idx / SR, end_idx / SR, m, endpoint=False, dtype=np.float32)
        t_mid = float(t[m // 2])

        # Determine musical intensity, BPM, and Shepard-Tone gain per section
        if t_mid < 95.0:  # Act 1 Highway
            bpm = 140.0
            drive = 0.78
            shepard_gain = 0.22 + 0.25 * (t_mid / 95.0)
            root_hz = 55.0  # A1
        elif t_mid < 200.0:  # Act 2 Subway
            bpm = 148.0
            drive = 0.84
            shepard_gain = 0.30 + 0.25 * ((t_mid - 95.0) / 105.0)
            root_hz = 58.27  # Bb1
        elif t_mid < 280.0:  # Act 3 Warehouse Prop-Fu
            bpm = 156.0
            drive = 0.88
            shepard_gain = 0.28
            root_hz = 61.74  # B1
        elif t_mid < 310.0:  # Act 3 First Exhaustion Standoff (Suffocating Shepard Riser!)
            prog = (t_mid - 280.0) / 30.0
            bpm = 120.0 + 40.0 * prog
            drive = 0.25 + 0.55 * (prog ** 2)
            shepard_gain = 0.45 + 0.50 * prog
            root_hz = 55.0
        elif t_mid < 415.0:  # Act 4 Penthouse Dojo
            bpm = 160.0
            drive = 0.90
            shepard_gain = 0.42
            root_hz = 65.41  # C2
        elif t_mid < 445.0:  # Act 5 ULTIMATE 30s HELIPAD TENSION RISER!
            prog = (t_mid - 415.0) / 30.0
            bpm = 110.0 + 66.0 * prog
            drive = 0.20 + 0.78 * (prog ** 2.2)
            shepard_gain = 0.55 + 0.45 * prog
            root_hz = 55.0 + 18.0 * prog
        elif t_mid < 534.5:  # Act 5-6 All-Out Climax Brawl & Fist Catch!
            bpm = 172.0
            drive = 0.98
            shepard_gain = 0.72
            root_hz = 73.42  # D2
        elif t_mid < 585.0:  # Act 6 Brotherhood Emotional Aftermath
            bpm = 90.0
            drive = 0.18
            shepard_gain = 0.0
            root_hz = 55.0
        else:  # 5-Visor Cliffhanger!
            prog = (t_mid - 585.0) / 19.0
            bpm = 144.0
            drive = 0.55 + 0.40 * prog
            shepard_gain = 0.68
            root_hz = 51.91  # Ab1

        # 1. Deep Warm Dark-Knight / Winter-Soldier Sub-Bass Pulse (Smooth attack -> ZERO clicks!)
        beat_hz = bpm / 60.0
        eighth = (t * beat_hz * 2.0) % 1.0
        plk_env = np.minimum(1.0, eighth * 24.0) * np.exp(-eighth * 4.8) * drive
        bass = (
            np.sin(2 * np.pi * root_hz * t) * 0.85
            + np.sin(2 * np.pi * root_hz * 2.0 * t) * 0.32
        ) * plk_env * 0.28

        # Heavy Taiko / Cinema Sub-Drum Downbeat every beat
        beat_phase = (t * beat_hz) % 1.0
        kick_t = beat_phase / beat_hz
        kick_env = np.minimum(1.0, beat_phase * 40.0) * np.exp(-beat_phase * 11.0) * drive
        kick = np.sin(2 * np.pi * (48.0 * kick_t + 3.2 * (1.0 - np.exp(-kick_t * 22.0)))) * kick_env * 0.30

        # Real Stochastic Brushed Percussion Shaker on 8th notes (NO FM sine bells!)
        raw_hat = np.convolve(rng.standard_normal(m).astype(np.float32), smooth_hat_k, mode="same")
        hat_env = np.minimum(1.0, eighth * 35.0) * np.exp(-eighth * 22.0)
        tick = raw_hat * hat_env * (0.028 * drive + 0.038 * shepard_gain)

        # 2. DARK HANS ZIMMER / CELLO-REGISTER SHEPARD-TONE INFINITE TENSION RISER (44Hz - 240Hz!)
        shep_L = np.zeros(m, dtype=np.float32)
        shep_R = np.zeros(m, dtype=np.float32)
        if shepard_gain > 0.01:
            glide_speed = 0.065 + 0.045 * shepard_gain
            for oct_k in range(4):
                oct_pos = (oct_k + t * glide_speed) % 4.0
                bell = np.exp(-0.5 * ((oct_pos - 1.65) / 0.72) ** 2)
                phase = 2.0 * np.pi * (41.2 / (glide_speed * math.log(2.0))) * (2.0 ** oct_pos)
                wave = np.sin(phase) + 0.30 * np.sin(phase * 2.0)
                pan = 0.44 + 0.20 * ((oct_k % 2) * 2 - 1)
                shep_L += (wave * bell * pan).astype(np.float32)
                shep_R += (wave * bell * (1.0 - pan * 0.45)).astype(np.float32)
            shep_L *= shepard_gain * 0.11
            shep_R *= shepard_gain * 0.11

        # 3. Emotional Brotherhood Warm Pad (534.5s - 585s)
        pad_L = np.zeros(m, dtype=np.float32)
        pad_R = np.zeros(m, dtype=np.float32)
        if 534.5 <= t_mid < 585.5:
            bar = int((t_mid - 534.5) / 4.5) % 4
            chords = [
                (110.0, 164.81, 220.0, 261.63),
                (87.31, 130.81, 174.61, 220.0),
                (130.81, 196.00, 261.63, 329.63),
                (98.00, 146.83, 196.00, 246.94),
            ][bar]
            for cf in chords:
                w1 = np.sin(2 * np.pi * cf * t)
                w2 = np.sin(2 * np.pi * (cf * 1.002) * t)
                pad_L += (w1 * 0.055).astype(np.float32)
                pad_R += (w2 * 0.055).astype(np.float32)

        # 4. Real Stochastic Filtered Rain Storm Ambience in Outdoor Acts
        rain_L = np.zeros(m, dtype=np.float32)
        rain_R = np.zeros(m, dtype=np.float32)
        if t_mid < 95.0 or t_mid >= 407.0:
            rain_amp = 0.022 if t_mid < 95.0 else (0.036 if t_mid < 535.0 else 0.018)
            rain_L = np.convolve(rng.standard_normal(m).astype(np.float32), smooth_rain_k, mode="same") * rain_amp
            rain_R = np.convolve(rng.standard_normal(m).astype(np.float32), smooth_rain_k, mode="same") * rain_amp

        left[start_idx:end_idx] = bass + kick + tick + shep_L + pad_L + rain_L
        right[start_idx:end_idx] = bass * 0.96 + kick + tick * 0.9 + shep_R + pad_R + rain_R

    return np.stack([left, right], axis=1)


async def main():
    print("[Day05 Audio] Generating snappy, silence-trimmed Hollywood dialogue clips...")
    vo_clips = await generate_tts_clips()
    rng = np.random.default_rng(202605)
    sfx_lib = make_combat_sfx(rng)
    impacts = build_choreography_impacts(rng)

    print("[Day05 Audio] Synthesizing 10:04 stereo Shepard-Tone + Winter-Soldier score...")
    stereo = synthesize_hollywood_score(rng)
    n_total = stereo.shape[0]

    # Sidechain envelope for crystal-clear dialogue punch
    duck_env = np.ones(n_total, dtype=np.float32)
    vo_track_L = np.zeros(n_total, dtype=np.float32)
    vo_track_R = np.zeros(n_total, dtype=np.float32)

    dialogue_meta = []
    cursor_sec = 0.0

    for idx, target_sec, act, speaker, text, radio_fx, samples in vo_clips:
        start_sec = max(target_sec, cursor_sec + 0.12)
        start_i = int(start_sec * SR)
        end_i = min(n_total, start_i + len(samples))
        seg_len = end_i - start_i
        if seg_len <= 0:
            continue
        end_sec = end_i / SR
        cursor_sec = end_sec

        # Slight stereo placement per character
        pan_L, pan_R = (1.0, 0.94) if speaker == "orange" else ((0.94, 1.0) if "blue" in speaker else (0.97, 0.97))
        vo_track_L[start_i:end_i] += samples[:seg_len] * pan_L
        vo_track_R[start_i:end_i] += samples[:seg_len] * pan_R

        # Sidechain duck music during speech (tight 60ms attack/release!)
        pad = int(0.06 * SR)
        d0 = max(0, start_i - pad)
        d1 = min(n_total, end_i + pad)
        duck_env[d0:d1] = np.minimum(duck_env[d0:d1], 0.34)

        dialogue_meta.append(
            {
                "id": idx,
                "act": act,
                "speaker": speaker,
                "text": text,
                "startSec": round(start_sec, 3),
                "endSec": round(end_sec, 3),
                "startFrame": int(round(start_sec * FPS)),
                "endFrame": int(round(end_sec * FPS)),
            }
        )

    # Apply smooth sidechain ducking to music
    smooth_win = np.ones(int(0.04 * SR), dtype=np.float32) / int(0.04 * SR)
    duck_smooth = np.convolve(duck_env, smooth_win, mode="same")
    stereo[:, 0] *= duck_smooth
    stereo[:, 1] *= duck_smooth

    # Layer all frame-accurate Martial Arts Foley & Impacts!
    print(f"[Day05 Audio] Mixing {len(impacts)} martial-arts foley & breathing/heartbeat events...")
    impact_meta = []
    for sec, kind, intensity in impacts:
        if kind not in sfx_lib:
            continue
        clip = sfx_lib[kind]
        s_i = int(sec * SR)
        e_i = min(n_total, s_i + len(clip))
        if e_i <= s_i:
            continue
        # Duck foley slightly if dialogue is speaking simultaneously, except major story shatters/rips
        vol = intensity * (0.55 if duck_smooth[min(n_total - 1, s_i)] < 0.5 and kind not in ("glass_shatter", "cloth_rip", "braam") else 0.92)
        pan_jit = 0.88 + 0.24 * ((s_i % 7) / 6.0)
        stereo[s_i:e_i, 0] += clip[: e_i - s_i] * vol * pan_jit
        stereo[s_i:e_i, 1] += clip[: e_i - s_i] * vol * (1.96 - pan_jit)

        # Export visual impact shakes/flashes for combat hits (skip pant/heartbeat in visual impact list)
        if kind not in ("pant", "heartbeat"):
            impact_meta.append(
                {
                    "frame": int(round(sec * FPS)),
                    "kind": kind,
                    "intensity": intensity,
                }
            )

    # Sum dialogue + master limiter
    stereo[:, 0] += vo_track_L * 1.12
    stereo[:, 1] += vo_track_R * 1.12
    stereo = np.tanh(stereo * 1.08) * 0.94

    OUT_AUDIO.parent.mkdir(parents=True, exist_ok=True)
    raw_pcm = STUDIO_DIR / "out" / "day05_master_tmp.f32le"
    stereo.astype(np.float32).tofile(str(raw_pcm))

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", str(raw_pcm),
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(OUT_AUDIO),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    raw_pcm.unlink(missing_ok=True)

    # Export TypeScript timeline for Remotion choreography, lip-sync, camera cuts & impact flashes!
    OUT_TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    ts_code = f"""// Auto-generated by scripts/build_day05_audio.py
export interface Day05DialogueLine {{
  readonly id: number;
  readonly act: number;
  readonly speaker: "orange" | "blue_weapon" | "blue_real" | "handler" | "hud";
  readonly text: string;
  readonly startSec: number;
  readonly endSec: number;
  readonly startFrame: number;
  readonly endFrame: number;
}}

export interface Day05ImpactEvent {{
  readonly frame: number;
  readonly kind: string;
  readonly intensity: number;
}}

export const DAY05_FPS = {FPS};
export const DAY05_DURATION_SECONDS = {TOTAL_SECONDS};
export const DAY05_TOTAL_FRAMES = {TOTAL_FRAMES};

export const DAY05_DIALOGUE: readonly Day05DialogueLine[] = {json.dumps(dialogue_meta, indent=2)} as const;

export const DAY05_IMPACTS: readonly Day05ImpactEvent[] = {json.dumps(impact_meta, indent=2)} as const;

export function getActiveDialogue(globalFrame: number): Day05DialogueLine | null {{
  for (let i = 0; i < DAY05_DIALOGUE.length; i++) {{
    const d = DAY05_DIALOGUE[i];
    if (globalFrame >= d.startFrame && globalFrame <= d.endFrame) return d;
  }}
  return null;
}}

export function isFighterSpeaking(globalFrame: number, who: "orange" | "blue"): boolean {{
  const d = getActiveDialogue(globalFrame);
  if (!d) return false;
  if (who === "orange") return d.speaker === "orange";
  return d.speaker === "blue_weapon" || d.speaker === "blue_real";
}}

export function getImpactPulse(globalFrame: number): {{ shake: number; flash: boolean; spark: boolean; kind: string }} {{
  let maxShake = 0;
  let flash = false;
  let spark = false;
  let hitKind = "";
  for (let i = 0; i < DAY05_IMPACTS.length; i++) {{
    const ev = DAY05_IMPACTS[i];
    const df = globalFrame - ev.frame;
    if (df >= 0 && df <= 7) {{
      const decay = 1 - df / 7;
      const mult =
        ev.kind === "glass_shatter" || ev.kind === "body_slam" || ev.kind === "braam"
          ? 24
          : ev.kind === "heavy_hit" || ev.kind === "wing_chun_flurry"
            ? 14
            : 7;
      const s = mult * ev.intensity * decay;
      if (s > maxShake) {{
        maxShake = s;
        hitKind = ev.kind;
      }}
      if (df <= 1 && (ev.kind === "glass_shatter" || ev.kind === "body_slam" || (ev.kind === "heavy_hit" && ev.intensity >= 0.94))) {{
        flash = true;
      }}
      if (df <= 4 && (ev.kind === "knife_spark" || ev.kind === "bionic" || ev.kind === "metal_prop" || ev.kind === "heavy_hit")) {{
        spark = true;
      }}
    }}
  }}
  return {{ shake: maxShake, flash, spark, kind: hitKind }};
}}
"""
    OUT_TIMELINE.write_text(ts_code, encoding="utf-8")
    print(f"[Day05 Audio] DONE! Exported {OUT_AUDIO} ({OUT_AUDIO.stat().st_size / 1e6:.2f} MB) & {OUT_TIMELINE} ({len(dialogue_meta)} lines, {len(impact_meta)} visual impacts).")


if __name__ == "__main__":
    asyncio.run(main())
