#!/usr/bin/env python3
"""
Deterministic Cloud Asset & Manifest Builder for Cole & Maya Autonomous Studio
------------------------------------------------------------------------------
Subcommands:
  1. acquire  --plan <plan.json> --out-dir <dir> --catalog <catalog.json> --mode <main|short>
     - Pulls verified Wikipedia REST summaries for primary factual grounding
     - Harvests & normalizes 100% REAL photographs & archival/location videos
     - Emits verified catalog.json with real local paths inside public/

  2. finalize --script <script.json> --catalog <catalog.json> --out-dir <dir> --mode <main|short>
     - Synthesizes Cole & Maya neural speech (edge-tts) + -16 LUFS ambient bed
     - Enforces <58.5s hard ceiling for YouTube Shorts eligibility
     - Compiles gapless frame-accurate Remotion manifests & thumbnail assets
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_dual_host_audio import (  # noqa: E402
    find_ffmpeg,
    get_duration_sec,
    synthesize_dialogue_lines,
)
from research_real_media import (  # noqa: E402
    USER_AGENT,
    fetch_and_normalize_video,
    fetch_and_verify_photo,
    search_wikimedia,
    search_wikipedia_article_media,
)

SKIP_FILENAME_TOKENS = (
    "flag_of",
    "coat_of_arms",
    "seal_of",
    "logo",
    "icon",
    "signature",
    "blank_map",
    "locator_map",
    "orthographic",
    "diagram",
    "chart",
    "graph",
    "plot",
    "infographic",
    "painting",
    "engraving",
    "lithograph",
    "caricature",
    "cartoon",
    "illustration",
    "drawing",
    "emblem",
)

FALLBACK_INSTITUTION_QUERIES = [
    "Federal Reserve Building Washington",
    "New York Stock Exchange facade",
    "United States Capitol dusk",
    "Lower Manhattan financial district skyline",
    "Pentagon aerial photograph",
]


def is_clean_photo_candidate(item: dict[str, Any]) -> bool:
    if item.get("kind", "photo") != "photo":
        return False
    url = str(item.get("url") or item.get("downloadUrl") or "").lower()
    clean_url = url.split("?")[0]
    title = str(item.get("title") or "").lower().replace(" ", "_")
    # Enforce genuine camera photography (.jpg / .jpeg) — reject .png charts/diagrams/graphics
    if not clean_url.endswith((".jpg", ".jpeg")):
        return False
    for tok in SKIP_FILENAME_TOKENS:
        if tok in clean_url or tok in title:
            return False
    return True


def fetch_wikipedia_summary(article: str) -> dict[str, str] | None:
    slug = article.strip().replace(" ", "_")
    if not slug:
        return None
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(slug)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        extract = str(data.get("extract") or "").strip()
        if not extract:
            return None
        return {
            "title": str(data.get("title") or article),
            "description": str(data.get("description") or ""),
            "extract": extract[:900],
        }
    except Exception:
        return None


def cmd_acquire(args: argparse.Namespace) -> None:
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    public_root = (ROOT / "public").resolve()
    is_short = args.mode == "short"
    target_photos = 6 if is_short else 10
    target_videos = 1 if is_short else 2

    wiki_articles: list[str] = list(plan.get("wikipediaArticles") or [])
    photo_queries: list[str] = list(plan.get("photoQueries") or [])
    video_queries: list[str] = list(plan.get("videoQueries") or [])

    print(f"[acquire] Fetching Wikipedia primary summaries ({len(wiki_articles)} articles)...")
    wiki_facts: list[dict[str, str]] = []
    photo_pool: list[dict[str, Any]] = []

    for art in wiki_articles[:10]:
        summary = fetch_wikipedia_summary(art)
        if summary:
            wiki_facts.append(summary)
        try:
            art_media = search_wikipedia_article_media(art, limit=4)
            for m in art_media:
                if is_clean_photo_candidate(m):
                    photo_pool.append(m)
        except Exception as exc:
            print(f"  [warn] wiki media '{art}': {exc}")

    print(f"[acquire] Searching Wikimedia Commons real photographs ({len(photo_queries)} queries)...")
    for q in photo_queries[:12]:
        try:
            found = search_wikimedia(q, "bitmap", limit=4, min_width=750)
            for m in found:
                if is_clean_photo_candidate(m):
                    photo_pool.append(m)
        except Exception as exc:
            print(f"  [warn] commons photo '{q}': {exc}")

    # Guarantee plenty of high-res candidates via institutional fallbacks if needed
    for fb_q in FALLBACK_INSTITUTION_QUERIES:
        if len(photo_pool) >= target_photos * 3:
            break
        try:
            for m in search_wikimedia(fb_q, "bitmap", limit=2, min_width=750):
                if is_clean_photo_candidate(m):
                    photo_pool.append(m)
        except Exception:
            pass

    assets: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    photo_idx = 1

    for cand in photo_pool:
        if photo_idx > target_photos:
            break
        dl_url = str(cand.get("url") or cand.get("downloadUrl") or "")
        if not dl_url or dl_url in seen_urls:
            continue
        seen_urls.add(dl_url)

        asset_id = f"photo_{photo_idx:02d}"
        dest = out_dir / f"{asset_id}.jpg"
        try:
            info = fetch_and_verify_photo(dl_url, dest, min_width=650)
            rel_path = dest.resolve().relative_to(public_root).as_posix()
            assets.append(
                {
                    "id": asset_id,
                    "kind": "photo",
                    "relPath": rel_path,
                    "width": info["width"],
                    "height": info["height"],
                    "title": str(cand.get("title") or asset_id),
                    "description": str(cand.get("description") or "")[:180],
                    "suggestedSourceTag": str(
                        cand.get("suggestedSourceTag") or "WIKIMEDIA ARCHIVE · REAL PHOTO"
                    )[:56],
                }
            )
            print(f"  [ok] {asset_id} ({info['width']}x{info['height']}) <- {cand.get('title')}")
            photo_idx += 1
        except Exception as exc:
            if dest.exists():
                dest.unlink()
            print(f"  [skip] photo candidate failed: {exc}")

    # Optional real 1080p video clips from Wikimedia Commons
    video_idx = 1
    for vq in video_queries[:6]:
        if video_idx > target_videos:
            break
        try:
            v_cands = search_wikimedia(vq, "video", limit=3)
        except Exception:
            v_cands = []
        for vc in v_cands:
            if video_idx > target_videos:
                break
            v_url = str(vc.get("url") or vc.get("downloadUrl") or "")
            if not v_url or v_url in seen_urls:
                continue
            seen_urls.add(v_url)
            asset_id = f"video_{video_idx:02d}"
            dest_mp4 = out_dir / f"{asset_id}.mp4"
            try:
                v_info = fetch_and_normalize_video(
                    v_url,
                    dest_mp4,
                    start_sec=1.0,
                    duration_sec=11.0,
                )
                rel_path = dest_mp4.resolve().relative_to(public_root).as_posix()
                assets.append(
                    {
                        "id": asset_id,
                        "kind": "video",
                        "relPath": rel_path,
                        "width": 1920,
                        "height": 1080,
                        "durationSec": v_info["durationSec"],
                        "title": str(vc.get("title") or asset_id),
                        "description": str(vc.get("description") or "")[:180],
                        "suggestedSourceTag": str(
                            vc.get("suggestedSourceTag") or "ARCHIVAL FOOTAGE · 1080P"
                        )[:56],
                    }
                )
                print(f"  [ok] {asset_id} (1080p {v_info['durationSec']}s) <- {vc.get('title')}")
                video_idx += 1
                break
            except Exception as exc:
                if dest_mp4.exists():
                    dest_mp4.unlink()
                print(f"  [skip] video candidate failed: {exc}")

    if not any(a["kind"] == "photo" for a in assets):
        raise RuntimeError("No verified real photographs could be acquired for this topic.")

    catalog = {
        "wikipediaFacts": wiki_facts,
        "assets": assets,
    }
    Path(args.catalog).write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[acquire] Saved {len(assets)} verified real assets -> {args.catalog}")


def mix_broadcast_master(vo_wav: Path, out_mp3: Path, pad_sec: float = 0.8) -> float:
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = find_ffmpeg()
    vo_dur = get_duration_sec(vo_wav)
    total_dur = round(vo_dur + pad_sec, 3)

    bed_wav = vo_wav.parent / "auto_ambient_bed.wav"
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
            "[0:a]volume=0.013[a0];[1:a]volume=0.007[a1];[a0][a1]amix=inputs=2:duration=longest,aformat=channel_layouts=stereo",
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
            f"[0:a]apad=pad_dur={pad_sec}[vo];[vo][1:a]amix=inputs=2:duration=first:weights=1 0.35,loudnorm=I=-16:TP=-1.5:LRA=11",
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


def build_thumbnail_bg(hero_photo: Path, out_jpg: Path) -> None:
    im = Image.open(hero_photo).convert("RGB")
    w, h = im.size
    target_ratio = 1280 / 720
    cur_ratio = w / max(1, h)
    if cur_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = max(0, int((h - new_h) * 0.22))
        im = im.crop((0, top, w, min(h, top + new_h)))
    im = im.resize((1280, 720), Image.Resampling.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Brightness(im).enhance(1.06)
    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_jpg, quality=94)


def cmd_finalize(args: argparse.Namespace) -> None:
    script_data = json.loads(Path(args.script).read_text(encoding="utf-8"))
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir).resolve()
    public_root = (ROOT / "public").resolve()
    is_short = args.mode == "short"

    assets: list[dict[str, Any]] = catalog["assets"]
    by_asset_id = {a["id"]: a for a in assets}
    photo_assets = [a for a in assets if a["kind"] == "photo"]

    raw_cues = list(script_data.get("cues") or [])
    valid_expr = {"neutral", "serious", "curious", "skeptical", "shocked", "emphatic"}
    clean_lines: list[dict[str, Any]] = []
    for idx, c in enumerate(raw_cues):
        spk = str(c.get("speaker") or ("cole" if idx % 2 == 0 else "maya")).lower().strip()
        if spk not in ("cole", "maya"):
            spk = "cole" if idx % 2 == 0 else "maya"
        expr = str(c.get("expression") or "serious").lower().strip()
        if expr not in valid_expr:
            expr = "serious"
        txt = str(c.get("text") or "").strip()
        if not txt:
            continue
        clean_lines.append(
            {
                "id": f"c{len(clean_lines) + 1:02d}",
                "speaker": spk,
                "expression": expr,
                "text": txt,
            }
        )

    if len(clean_lines) < 4:
        raise RuntimeError(f"Script too short ({len(clean_lines)} lines).")

    tmp_audio = ROOT / (".tmp_auto_short_audio" if is_short else ".tmp_auto_main_audio")
    if tmp_audio.exists():
        shutil.rmtree(tmp_audio)

    pause_s = 0.14 if is_short else 0.24
    pad_s = 0.45 if is_short else 0.85

    cues_timed, raw_vo_wav = asyncio.run(
        synthesize_dialogue_lines(clean_lines, tmp_audio, pause_sec=pause_s)
    )

    # Hard YouTube Shorts (<58.0s) eligibility ceiling
    if is_short and cues_timed[-1]["endSec"] + pad_s > 58.0:
        while len(clean_lines) > 5 and cues_timed[-1]["endSec"] + pad_s > 58.0:
            clean_lines.pop(-2)  # drop penultimate elaboration line, keep closing punchline!
            shutil.rmtree(tmp_audio)
            cues_timed, raw_vo_wav = asyncio.run(
                synthesize_dialogue_lines(clean_lines, tmp_audio, pause_sec=0.12)
            )

    master_mp3 = out_dir / "master_audio.mp3"
    total_dur = mix_broadcast_master(raw_vo_wav, master_mp3, pad_sec=pad_s)
    shutil.rmtree(tmp_audio, ignore_errors=True)

    master_rel = master_mp3.resolve().relative_to(public_root).as_posix()

    # Map shots deterministically across cues_timed
    raw_shots = list(script_data.get("shots") or [])
    num_cues = len(cues_timed)

    if not raw_shots:
        raw_shots = [
            {"cueStart": i, "cueEnd": i, "layout": "real_photo_pip", "assetId": photo_assets[i % len(photo_assets)]["id"]}
            for i in range(num_cues)
        ]

    # Partition [0..num_cues-1] cleanly across len(raw_shots)
    shot_count = min(len(raw_shots), num_cues)
    raw_shots = raw_shots[:shot_count]

    shots_out: list[dict[str, Any]] = []
    cursor = 0.0
    for s_idx in range(shot_count):
        c_start = int(round(s_idx * num_cues / shot_count))
        c_end = int(round((s_idx + 1) * num_cues / shot_count)) - 1
        c_start = max(0, min(num_cues - 1, c_start))
        c_end = max(c_start, min(num_cues - 1, c_end))

        is_last = s_idx == shot_count - 1
        if is_last:
            end_t = round(total_dur, 3)
        else:
            next_c_start = max(c_end + 1, min(num_cues - 1, int(round((s_idx + 1) * num_cues / shot_count))))
            end_t = round(
                (cues_timed[c_end]["endSec"] + cues_timed[next_c_start]["startSec"]) / 2.0,
                3,
            )

        raw_s = raw_shots[s_idx]
        req_asset_id = str(raw_s.get("assetId") or "")
        asset = by_asset_id.get(req_asset_id) or photo_assets[s_idx % len(photo_assets)]
        is_vid = asset["kind"] == "video"

        layout = str(raw_s.get("layout") or ("real_photo_full" if is_short else "real_photo_pip"))
        if is_short:
            layout = "real_video_full" if is_vid else "real_photo_full"
        else:
            valid_layouts = {
                "studio_dual",
                "studio_solo_cole",
                "studio_solo_maya",
                "real_video_pip",
                "real_photo_pip",
                "real_split_evidence",
                "real_photo_full",
                "real_video_full",
            }
            if layout not in valid_layouts:
                layout = "real_video_pip" if is_vid else "real_photo_pip"
            if is_vid and layout in ("real_photo_pip", "real_photo_full", "real_split_evidence"):
                layout = "real_video_pip"
            if (not is_vid) and layout in ("real_video_pip", "real_video_full"):
                layout = "real_photo_pip"

        active_spk = cues_timed[c_start]["speaker"]
        shot_obj: dict[str, Any] = {
            "id": f"s{s_idx + 1:02d}",
            "startSec": cursor,
            "endSec": end_t,
            "layout": layout,
            "sourceTag": str(raw_s.get("sourceTag") or asset["suggestedSourceTag"])[:56],
            "locationDate": str(raw_s.get("locationDate") or "PRIMARY RECORD")[:44],
            "headline": str(raw_s.get("headline") or script_data.get("episodeTitle") or "")[:62].upper(),
        }

        if layout.startswith("studio_"):
            photo_fallback = asset if not is_vid else photo_assets[s_idx % len(photo_assets)]
            shot_obj["monitorMediaPath"] = photo_fallback["relPath"]
        else:
            shot_obj["mediaPath"] = asset["relPath"]
            shot_obj["pipHost"] = active_spk
            if is_vid:
                shot_obj["videoTrimStartSec"] = 0.0
            else:
                # Portrait aspect check -> protect upper face region
                if asset.get("height", 1080) > asset.get("width", 1920):
                    shot_obj["mediaObjectPosition"] = "50% 18%"

        raw_facts = list(raw_s.get("facts") or [])
        if raw_facts and (is_short or layout == "real_split_evidence"):
            clean_facts = []
            for f_item in raw_facts[:2]:
                lbl = str(f_item.get("label") or "KEY RECORD")[:32]
                val = str(f_item.get("value") or "")[:72]
                acc = str(f_item.get("accent") or "amber")
                if acc not in ("amber", "cyan", "red"):
                    acc = "amber"
                if val:
                    clean_facts.append({"label": lbl, "value": val, "accent": acc})
            if clean_facts:
                shot_obj["facts"] = clean_facts

        raw_notes = list(raw_s.get("notes") or [])
        if raw_notes and layout == "real_split_evidence":
            shot_obj["notes"] = [str(raw_notes[0])[:140]]

        shots_out.append(shot_obj)
        cursor = end_t

    chapters_out: list[dict[str, Any]] = []
    if not is_short:
        raw_ch = list(script_data.get("chapters") or [])
        for c_i, ch in enumerate(raw_ch[:4]):
            cue_idx = int(ch.get("cueIndex", c_i * max(1, num_cues // 4)))
            cue_idx = max(1, min(num_cues - 2, cue_idx))
            chapters_out.append(
                {
                    "index": f"{c_i + 1:02d}",
                    "title": str(ch.get("title") or f"Part {c_i + 1}")[:44],
                    "subtitle": str(ch.get("subtitle") or "PRIMARY RECORD")[:38].upper(),
                    "startSec": round(cues_timed[cue_idx]["startSec"], 2),
                }
            )

    manifest = {
        "episodeTitle": str(script_data.get("episodeTitle") or "PRIMARY RECORD INVESTIGATION")[:68].upper(),
        "categoryTag": str(script_data.get("categoryTag") or "PRIMARY RECORD")[:24].upper(),
        "masterAudioPath": master_rel,
        "totalDurationSec": round(total_dur, 2),
        "cues": cues_timed,
        "shots": shots_out,
        "chapters": chapters_out,
    }

    if is_short:
        manifest_path = ROOT / "src" / "realshow" / "autoShortManifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[finalize] Wrote Short manifest -> {manifest_path} ({total_dur:.2f}s, {len(cues_timed)} cues)")
    else:
        manifest_path = ROOT / "src" / "realshow" / "autoMainManifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        thumb_hero_id = str(script_data.get("thumbnailAssetId") or "")
        hero_asset = by_asset_id.get(thumb_hero_id)
        if not hero_asset or hero_asset["kind"] != "photo":
            hero_asset = photo_assets[0]
        hero_disk = public_root / hero_asset["relPath"]
        thumb_bg = out_dir / "thumb_bg.jpg"
        build_thumbnail_bg(hero_disk, thumb_bg)
        thumb_rel = thumb_bg.resolve().relative_to(public_root).as_posix()

        thumb_meta = script_data.get("thumbnail") or {}
        thumb_props = {
            "bgPhotoPath": thumb_rel,
            "topBadge": str(thumb_meta.get("topBadge") or manifest["categoryTag"])[:24].upper(),
            "line1": str(thumb_meta.get("line1") or "FOLLOW")[:10].upper(),
            "line2": str(thumb_meta.get("line2") or "THE")[:10].upper(),
            "line3": str(thumb_meta.get("line3") or "RECORD")[:10].upper(),
        }
        thumb_props_path = ROOT / "src" / "realshow" / "autoMainThumbProps.json"
        thumb_props_path.write_text(json.dumps(thumb_props, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[finalize] Wrote Main manifest & Thumbnail props -> {manifest_path} ({total_dur:.2f}s)")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_acq = sub.add_parser("acquire")
    p_acq.add_argument("--plan", required=True)
    p_acq.add_argument("--out-dir", required=True)
    p_acq.add_argument("--catalog", required=True)
    p_acq.add_argument("--mode", choices=["main", "short"], required=True)
    p_acq.set_defaults(func=cmd_acquire)

    p_fin = sub.add_parser("finalize")
    p_fin.add_argument("--script", required=True)
    p_fin.add_argument("--catalog", required=True)
    p_fin.add_argument("--out-dir", required=True)
    p_fin.add_argument("--mode", choices=["main", "short"], required=True)
    p_fin.set_defaults(func=cmd_finalize)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
