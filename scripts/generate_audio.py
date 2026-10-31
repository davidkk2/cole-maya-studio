import math
import os
import random
import struct
import wave

SAMPLE_RATE = 44100
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "audio")
os.makedirs(OUT_DIR, exist_ok=True)


def save_wav(filename: str, samples: list[float]) -> None:
    path = os.path.join(OUT_DIR, filename)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        buf = bytearray()
        for s in samples:
            clamped = max(-0.98, min(0.98, s))
            buf.extend(struct.pack("<h", int(clamped * 32767)))
        wf.writeframes(bytes(buf))
    print(f"Generated {filename} ({len(samples)/SAMPLE_RATE:.2f}s)")


def gen_boing() -> None:
    dur = 0.55
    n = int(SAMPLE_RATE * dur)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 5.5)
        freq = 160 + 260 * math.sin(t * 28.0) * math.exp(-t * 3.0) + t * 220
        phase += 2 * math.pi * freq / SAMPLE_RATE
        val = (0.75 * math.sin(phase) + 0.25 * math.sin(2 * phase)) * env
        out.append(val * 0.8)
    save_wav("boing.wav", out)


def gen_whoosh() -> None:
    dur = 0.38
    n = int(SAMPLE_RATE * dur)
    out = []
    rng = random.Random(42)
    lp = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / dur)) ** 1.6
        cutoff = 0.04 + 0.28 * math.sin(math.pi * (t / dur))
        noise = rng.uniform(-1, 1)
        lp = lp + cutoff * (noise - lp)
        swoosh_tone = 0.25 * math.sin(2 * math.pi * (220 + 480 * (t / dur)) * t)
        out.append((lp * 1.4 + swoosh_tone) * env * 0.75)
    save_wav("whoosh.wav", out)


def gen_bonk() -> None:
    dur = 0.35
    n = int(SAMPLE_RATE * dur)
    out = []
    rng = random.Random(7)
    phase = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 14.0)
        freq = 420 * math.exp(-t * 18.0) + 110
        phase += 2 * math.pi * freq / SAMPLE_RATE
        click = rng.uniform(-1, 1) * math.exp(-t * 60.0) * 0.5
        hollow = math.sin(phase) + 0.45 * math.sin(phase * 2.4)
        out.append((hollow * env + click) * 0.85)
    save_wav("bonk.wav", out)


def gen_munch() -> None:
    dur = 0.9
    n = int(SAMPLE_RATE * dur)
    out = []
    rng = random.Random(99)
    lp = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        bite_idx = (t * 4.5) % 1.0
        bite_env = math.exp(-bite_idx * 9.0)
        noise = rng.uniform(-1, 1)
        lp = lp + 0.18 * (noise - lp)
        crunch = lp * bite_env * 1.2 + 0.2 * math.sin(2 * math.pi * 190 * t) * bite_env
        out.append(crunch * 0.75)
    save_wav("munch.wav", out)


def gen_rumble() -> None:
    dur = 1.6
    n = int(SAMPLE_RATE * dur)
    out = []
    rng = random.Random(13)
    lp = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * min(1.0, t / dur)) ** 0.7
        noise = rng.uniform(-1, 1)
        lp = lp + 0.025 * (noise - lp)
        sub = 0.5 * math.sin(2 * math.pi * (48 + 8 * math.sin(t * 12)) * t)
        out.append((lp * 2.2 + sub) * env * 0.85)
    save_wav("rumble.wav", out)


def gen_pop_idea() -> None:
    dur = 0.45
    n = int(SAMPLE_RATE * dur)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 7.5)
        val = (
            0.6 * math.sin(2 * math.pi * 1046.5 * t)
            + 0.35 * math.sin(2 * math.pi * 1567.98 * t)
            + 0.2 * math.sin(2 * math.pi * 2093.0 * t)
        ) * env
        out.append(val * 0.75)
    save_wav("idea-ding.wav", out)


def gen_sizzle_rocket() -> None:
    dur = 2.2
    n = int(SAMPLE_RATE * dur)
    out = []
    rng = random.Random(21)
    phase = 0.0
    hp_prev = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        if t < 0.8:
            # Steam whistle + sizzle buildup
            env = min(1.0, t / 0.15)
            freq = 650 + 900 * (t / 0.8) ** 1.5
            phase += 2 * math.pi * freq / SAMPLE_RATE
            nval = rng.uniform(-1, 1)
            sizzle = (nval - hp_prev) * 0.25
            hp_prev = nval
            out.append((0.55 * math.sin(phase) + sizzle) * env * 0.75)
        else:
            # Rocket launch whistle fading into sky
            rt = t - 0.8
            env = math.exp(-rt * 1.9)
            freq = 1550 - 950 * (rt / 1.4)
            phase += 2 * math.pi * max(180, freq) / SAMPLE_RATE
            thrust = rng.uniform(-1, 1) * 0.35
            out.append((0.5 * math.sin(phase) + thrust) * env * 0.85)
    save_wav("spicy-launch.wav", out)


def gen_cliffhanger_boom() -> None:
    dur = 1.1
    n = int(SAMPLE_RATE * dur)
    out = []
    phase = 0.0
    rng = random.Random(55)
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 3.8)
        freq = 130 * math.exp(-t * 5.0) + 42
        phase += 2 * math.pi * freq / SAMPLE_RATE
        punch = rng.uniform(-1, 1) * math.exp(-t * 35.0) * 0.6
        bass = math.tanh(2.2 * math.sin(phase)) * env
        out.append((bass + punch) * 0.85)
    save_wav("dramatic-boom.wav", out)


def gen_bgm_slapstick() -> None:
    # 16-second loopable quirky cartoon marimba + bouncy pizzicato bass @ 135 BPM
    bpm = 135.0
    beat_sec = 60.0 / bpm
    total_beats = 36  # 16 seconds cleanly
    dur = total_beats * beat_sec
    n = int(SAMPLE_RATE * dur)
    out = [0.0] * n

    def midi_to_hz(m: int) -> float:
        return 440.0 * (2.0 ** ((m - 69) / 12.0))

    # Playful C-major / A-minor cartoon sneaky-slapstick motif
    bass_notes = [
        48, 55, 52, 55,  48, 55, 52, 55,
        53, 60, 57, 60,  55, 62, 59, 55,
        48, 55, 52, 55,  45, 52, 48, 52,
        50, 57, 55, 59,  48, 55, 48, 0,
        48, 55, 52, 55,
    ]

    melody_events = [
        (0.0, 72, 0.35), (0.5, 76, 0.35), (1.0, 79, 0.35), (1.5, 76, 0.35),
        (2.0, 81, 0.5), (3.0, 79, 0.6),
        (4.0, 76, 0.35), (4.5, 72, 0.35), (5.0, 74, 0.35), (5.5, 75, 0.35),
        (6.0, 76, 0.7), (7.0, 72, 0.5),
        (8.0, 77, 0.35), (8.5, 81, 0.35), (9.0, 84, 0.5), (10.0, 81, 0.5),
        (11.0, 79, 0.35), (11.5, 77, 0.35), (12.0, 74, 0.5), (13.0, 79, 0.5),
        (14.0, 72, 0.35), (14.5, 76, 0.35), (15.0, 79, 0.35), (15.5, 84, 0.35),
        (16.0, 81, 0.4), (17.0, 79, 0.4), (18.0, 76, 0.6), (19.5, 72, 0.35),
        (20.0, 69, 0.35), (20.5, 72, 0.35), (21.0, 76, 0.5), (22.0, 81, 0.6),
        (24.0, 74, 0.35), (24.5, 77, 0.35), (25.0, 79, 0.5), (26.0, 83, 0.5),
        (27.0, 84, 0.9), (29.0, 79, 0.4), (30.0, 76, 0.4), (31.0, 72, 0.6),
        (32.0, 72, 0.35), (32.5, 76, 0.35), (33.0, 79, 0.4), (34.0, 84, 0.7),
    ]

    # Add pizzicato bass
    for b_idx, m_note in enumerate(bass_notes):
        if m_note == 0:
            continue
        start_s = b_idx * beat_sec
        start_i = int(start_s * SAMPLE_RATE)
        note_len = int(0.42 * beat_sec * SAMPLE_RATE)
        freq = midi_to_hz(m_note)
        for j in range(note_len):
            idx = start_i + j
            if idx >= n:
                break
            lt = j / SAMPLE_RATE
            env = math.exp(-lt * 11.0) * min(1.0, lt / 0.006)
            sig = 0.65 * math.sin(2 * math.pi * freq * lt) + 0.35 * math.sin(4 * math.pi * freq * lt)
            out[idx] += sig * env * 0.28

    # Add xylophone / marimba melody
    for beat_pos, m_note, gate in melody_events:
        start_s = beat_pos * beat_sec
        start_i = int(start_s * SAMPLE_RATE)
        note_len = int(gate * beat_sec * SAMPLE_RATE * 1.4)
        freq = midi_to_hz(m_note)
        for j in range(note_len):
            idx = start_i + j
            if idx >= n:
                break
            lt = j / SAMPLE_RATE
            env = math.exp(-lt * 13.5) * min(1.0, lt / 0.003)
            sig = (
                0.7 * math.sin(2 * math.pi * freq * lt)
                + 0.25 * math.sin(2 * math.pi * freq * 3.0 * lt) * math.exp(-lt * 25.0)
            )
            out[idx] += sig * env * 0.24

    save_wav("bgm-slapstick.wav", out)


if __name__ == "__main__":
    gen_boing()
    gen_whoosh()
    gen_bonk()
    gen_munch()
    gen_rumble()
    gen_pop_idea()
    gen_sizzle_rocket()
    gen_cliffhanger_boom()
    gen_bgm_slapstick()


def gen_vine_boom_heavy() -> None:
    dur = 0.85
    n = int(SAMPLE_RATE * dur)
    out = []
    phase = 0.0
    rng = random.Random(101)
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 4.2)
        freq = 165 * math.exp(-t * 9.0) + 38
        phase += 2 * math.pi * freq / SAMPLE_RATE
        punch = rng.uniform(-1, 1) * math.exp(-t * 55.0) * 0.7
        sub = math.tanh(3.4 * math.sin(phase)) * env
        out.append((sub + punch) * 0.92)
    save_wav("vine-boom-heavy.wav", out)


def gen_powerup_glitch() -> None:
    dur = 0.75
    n = int(SAMPLE_RATE * dur)
    out = []
    phase = 0.0
    notes = [523.25, 659.25, 783.99, 1046.5, 1318.5, 1567.98, 2093.0]
    for i in range(n):
        t = i / SAMPLE_RATE
        idx = min(len(notes) - 1, int((t / dur) * len(notes)))
        freq = notes[idx]
        phase += 2 * math.pi * freq / SAMPLE_RATE
        sq = 0.65 if math.sin(phase) >= 0 else -0.65
        env = min(1.0, (dur - t) * 8.0)
        out.append(sq * env * 0.65)
    save_wav("powerup-glitch.wav", out)


def gen_laser_blast() -> None:
    dur = 1.45
    n = int(SAMPLE_RATE * dur)
    out = []
    phase = 0.0
    rng = random.Random(303)
    for i in range(n):
        t = i / SAMPLE_RATE
        if t < 0.35:
            # High-speed turbine charge riser
            prog = t / 0.35
            freq = 240 + 1800 * (prog ** 2)
            phase += 2 * math.pi * freq / SAMPLE_RATE
            out.append(math.sin(phase) * prog * 0.8)
        else:
            bt = t - 0.35
            env = math.exp(-bt * 2.1)
            freq = 140 + 60 * math.sin(bt * 45.0)
            phase += 2 * math.pi * freq / SAMPLE_RATE
            roar = math.tanh(2.8 * math.sin(phase) + rng.uniform(-0.85, 0.85))
            out.append(roar * env * 0.9)
    save_wav("laser-blast.wav", out)


def gen_siren_alert() -> None:
    dur = 0.95
    n = int(SAMPLE_RATE * dur)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        mod = (t * 4.0) % 1.0
        freq = 680 + 420 * mod
        phase += 2 * math.pi * freq / SAMPLE_RATE
        saw = 2.0 * ((phase / (2 * math.pi)) % 1.0) - 1.0
        env = min(1.0, (dur - t) * 8.0)
        out.append(saw * env * 0.55)
    save_wav("siren-alert.wav", out)


def gen_record_stop() -> None:
    dur = 0.45
    n = int(SAMPLE_RATE * dur)
    out = []
    phase = 0.0
    rng = random.Random(88)
    for i in range(n):
        t = i / SAMPLE_RATE
        prog = 1.0 - (t / dur)
        freq = 620 * (prog ** 1.8) + 35
        phase += 2 * math.pi * freq / SAMPLE_RATE
        scratch = rng.uniform(-0.35, 0.35) * prog
        out.append((0.7 * math.sin(phase) + scratch) * prog * 0.85)
    save_wav("record-stop.wav", out)


def gen_phonk_hook_loop() -> None:
    # Hypnotic 155 BPM cowbell + 808 sub-bass loop (high-dopamine rhythmic anchor, 100% original)
    bpm = 155.0
    beat_s = 60.0 / bpm
    total_beats = 32
    dur = total_beats * beat_s
    n = int(SAMPLE_RATE * dur)
    out = [0.0] * n

    def midi_hz(m: int) -> float:
        return 440.0 * (2.0 ** ((m - 69) / 12.0))

    # Catchy minor-key drift cowbell hook (A minor: A5, C6, B5, E6, G5)
    hook = [
        (0.0, 81), (0.5, 81), (1.0, 84), (1.5, 81),
        (2.0, 83), (2.5, 81), (3.0, 79), (3.5, 76),
        (4.0, 81), (4.5, 81), (5.0, 88), (5.5, 86),
        (6.0, 84), (6.5, 83), (7.0, 81), (7.5, 79),
    ]
    for bar in range(4):
        offset_b = bar * 8.0
        # Kick + 808 on beats 0, 1.5, 2.5, 4, 5.5, 6.5
        for kb in [0.0, 1.5, 2.5, 4.0, 5.5, 6.5]:
            st = int((offset_b + kb) * beat_s * SAMPLE_RATE)
            klen = int(0.42 * beat_s * SAMPLE_RATE)
            ph = 0.0
            for j in range(klen):
                if st + j >= n:
                    break
                lt = j / SAMPLE_RATE
                f = 150 * math.exp(-lt * 22.0) + 45.0
                ph += 2 * math.pi * f / SAMPLE_RATE
                out[st + j] += math.tanh(2.2 * math.sin(ph)) * math.exp(-lt * 6.5) * 0.42

        # Sharp snare/clap on beats 1, 3, 5, 7
        rng = random.Random(bar + 500)
        for sb in [1.0, 3.0, 5.0, 7.0]:
            st = int((offset_b + sb) * beat_s * SAMPLE_RATE)
            slen = int(0.22 * beat_s * SAMPLE_RATE)
            for j in range(slen):
                if st + j >= n:
                    break
                lt = j / SAMPLE_RATE
                out[st + j] += rng.uniform(-1, 1) * math.exp(-lt * 26.0) * 0.28

        # 808 Cowbell Hook (dual detuned square/band tone @ 1x & 1.504x ratio)
        for hb, mnote in hook:
            st = int((offset_b + hb) * beat_s * SAMPLE_RATE)
            clen = int(0.38 * beat_s * SAMPLE_RATE)
            f1 = midi_hz(mnote)
            f2 = f1 * 1.504
            for j in range(clen):
                if st + j >= n:
                    break
                lt = j / SAMPLE_RATE
                env = math.exp(-lt * 16.0)
                s1 = 1.0 if math.sin(2 * math.pi * f1 * lt) >= 0 else -1.0
                s2 = 1.0 if math.sin(2 * math.pi * f2 * lt) >= 0 else -1.0
                cb = math.tanh((s1 + s2) * 0.65) * env
                out[st + j] += cb * 0.19

    save_wav("phonk-hook-loop.wav", out)


gen_vine_boom_heavy()
gen_powerup_glitch()
gen_laser_blast()
gen_siren_alert()
gen_record_stop()
gen_phonk_hook_loop()


def gen_sonic_pulse() -> None:
    dur = 0.9
    n = int(SAMPLE_RATE * dur)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 3.2) * (0.65 + 0.35 * math.sin(2 * math.pi * 18.0 * t))
        freq = 320 + 180 * math.sin(2 * math.pi * 9.0 * t)
        phase += 2 * math.pi * freq / SAMPLE_RATE
        out.append(math.sin(phase) * env * 0.8)
    save_wav("sonic-pulse.wav", out)


def gen_freeze_blast() -> None:
    dur = 0.85
    n = int(SAMPLE_RATE * dur)
    out = []
    rng = random.Random(707)
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 4.5)
        shimmer = (
            0.4 * math.sin(2 * math.pi * 2480 * t)
            + 0.35 * math.sin(2 * math.pi * 3120 * t)
            + 0.25 * math.sin(2 * math.pi * 4180 * t)
        )
        hiss = rng.uniform(-0.6, 0.6)
        out.append((shimmer + hiss) * env * 0.75)
    save_wav("freeze-blast.wav", out)


def gen_sword_slash() -> None:
    dur = 0.5
    n = int(SAMPLE_RATE * dur)
    out = []
    rng = random.Random(909)
    phase = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 9.0)
        freq = 1400 * math.exp(-t * 6.0) + 280
        phase += 2 * math.pi * freq / SAMPLE_RATE
        ring = 0.45 * math.sin(2 * math.pi * 1760 * t) * math.exp(-t * 5.0)
        whoosh = rng.uniform(-0.7, 0.7) * math.exp(-t * 14.0)
        out.append((0.5 * math.sin(phase) + ring + whoosh) * env * 0.9)
    save_wav("sword-slash.wav", out)


def gen_epic_boss_loop() -> None:
    # 16-second 150 BPM urgent sci-fi synthwave / boss battle loop (D minor)
    bpm = 150.0
    beat_s = 60.0 / bpm
    total_beats = 40  # 16.0 seconds cleanly
    dur = total_beats * beat_s
    n = int(SAMPLE_RATE * dur)
    out = [0.0] * n

    def midi_hz(m: int) -> float:
        return 440.0 * (2.0 ** ((m - 69) / 12.0))

    bass_seq = [38, 38, 50, 38, 41, 41, 45, 43]  # D2, D3, F2, A2, G2
    lead_seq = [
        (0.0, 62), (0.5, 65), (1.0, 69), (1.5, 74),
        (2.0, 72), (2.5, 69), (3.0, 67), (3.5, 65),
        (4.0, 62), (4.5, 65), (5.0, 70), (5.5, 69),
        (6.0, 67), (7.0, 64), (7.5, 61),
    ]

    for bar in range(5):
        base_b = bar * 8.0
        # Driving 8th-note synth bass + kick
        for step in range(16):
            st = int((base_b + step * 0.5) * beat_s * SAMPLE_RATE)
            blen = int(0.45 * 0.5 * beat_s * SAMPLE_RATE)
            bfreq = midi_hz(bass_seq[step % len(bass_seq)])
            for j in range(blen):
                if st + j >= n:
                    break
                lt = j / SAMPLE_RATE
                saw = 2.0 * ((bfreq * lt) % 1.0) - 1.0
                kick = math.sin(2 * math.pi * (130 * math.exp(-lt * 24.0) + 44) * lt) if step % 2 == 0 else 0.0
                out[st + j] += (saw * 0.22 + kick * 0.34) * math.exp(-lt * 9.0)

        # Heroic minor synth lead
        for lb, mnote in lead_seq:
            st = int((base_b + lb) * beat_s * SAMPLE_RATE)
            llen = int(0.42 * beat_s * SAMPLE_RATE)
            lfreq = midi_hz(mnote)
            for j in range(llen):
                if st + j >= n:
                    break
                lt = j / SAMPLE_RATE
                sq = 0.65 if math.sin(2 * math.pi * lfreq * lt) >= 0 else -0.65
                out[st + j] += sq * math.exp(-lt * 10.5) * 0.18

    save_wav("epic-boss-loop.wav", out)


gen_sonic_pulse()
gen_freeze_blast()
gen_sword_slash()
gen_epic_boss_loop()
