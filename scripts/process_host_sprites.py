#!/usr/bin/env python3
"""
Extracts pixel-locked RGBA studio sprites for Cole & Maya, the broadcast SM7B boom mic,
and the 1080p Manhattan studio room + foreground walnut desk mask.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
BRAIN_DIR = Path(
    r"C:\Users\samet\.gemini\antigravity\brain\e57e62f5-9fc2-4891-8f31-a49a4304d4d5"
)
OUT_HOSTS = ROOT / "public" / "studio" / "hosts"
OUT_STUDIO = ROOT / "public" / "studio"

RAW_FILES = {
    "studio_bg": BRAIN_DIR / "studio_set_bg_1793439975629.jpg",
    "mic": BRAIN_DIR / "studio_mic_raw_1793440009790.jpg",
    "cole_idle": BRAIN_DIR / "cole_raw_idle_1793439988812.jpg",
    "cole_talk1": BRAIN_DIR / "cole_raw_talk1_1793440011993.jpg",
    "cole_talk2": BRAIN_DIR / "cole_raw_talk2_1793440030589.jpg",
    "cole_blink": BRAIN_DIR / "cole_raw_blink_1793440047054.jpg",
    "maya_idle": BRAIN_DIR / "maya_raw_idle_1793439976944.jpg",
    "maya_talk1": BRAIN_DIR / "maya_raw_talk1_1793439996342.jpg",
    "maya_talk2": BRAIN_DIR / "maya_raw_talk2_1793440016900.jpg",
    "maya_blink": BRAIN_DIR / "maya_raw_blink_1793440037136.jpg",
}


def chroma_key_rgba(
    img: Image.Image, low: float = 26.0, high: float = 88.0
) -> np.ndarray:
    """Cleanly keys out chroma green with smooth anti-aliased alpha & zero green edge halo."""
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]

    max_rb = np.maximum(r, b)
    green_excess = g - max_rb

    alpha = 1.0 - np.clip((green_excess - low) / (high - low), 0.0, 1.0)

    # Erode 1px & feather 1.2px on edge fringe so zero green JPEG ringing survives
    alpha_u8 = (alpha * 255.0).astype(np.uint8)
    eroded = Image.fromarray(alpha_u8, mode="L").filter(ImageFilter.MinFilter(3))
    smoothed = eroded.filter(ImageFilter.GaussianBlur(radius=1.15))
    alpha_s = np.asarray(smoothed, dtype=np.float32) / 255.0

    alpha_final = np.where(alpha > 0.97, 1.0, alpha_s)
    alpha_final = np.where(alpha < 0.04, 0.0, alpha_final)

    # Strong green despill on any pixel that had green excess
    despill_cap = np.maximum(r * 0.52 + b * 0.48, max_rb * 0.92)
    g_clean = np.where(green_excess > 8.0, np.minimum(g, despill_cap), g)

    rgba = np.zeros((*r.shape, 4), dtype=np.uint8)
    rgba[..., 0] = np.clip(r, 0, 255).astype(np.uint8)
    rgba[..., 1] = np.clip(g_clean, 0, 255).astype(np.uint8)
    rgba[..., 2] = np.clip(b, 0, 255).astype(np.uint8)
    rgba[..., 3] = np.clip(alpha_final * 255.0, 0, 255).astype(np.uint8)
    return rgba


def auto_crop_bbox(rgba: np.ndarray, pad: int = 12) -> tuple[int, int, int, int]:
    alpha = rgba[..., 3]
    ys, xs = np.where(alpha > 24)
    h, w = rgba.shape[:2]
    x0 = max(0, int(xs.min()) - pad)
    x1 = min(w, int(xs.max()) + pad)
    y0 = max(0, int(ys.min()) - pad)
    y1 = h if int(ys.max()) > h - 10 else min(h, int(ys.max()) + pad)
    return (x0, y0, x1, y1)


def build_locked_host_sprites(name: str) -> None:
    idle_im = Image.open(RAW_FILES[f"{name}_idle"]).convert("RGB")
    # Standardize high-res 900x900 bust before cropping
    base_size = (900, 900)
    idle_im = idle_im.resize(base_size, Image.Resampling.LANCZOS)
    idle_rgba = chroma_key_rgba(idle_im)
    bbox = auto_crop_bbox(idle_rgba, pad=10)

    idle_crop = idle_rgba[bbox[1] : bbox[3], bbox[0] : bbox[2]]
    Image.fromarray(idle_crop, mode="RGBA").save(OUT_HOSTS / f"{name}_idle.png")
    h, w = idle_crop.shape[:2]
    print(f"[{name}] Master idle sprite: {w}x{h}")

    # Spatial face window (protects hair silhouette, headphones, shoulders & blazer 100%)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = xx / float(w)
    ny = yy / float(h)

    for variant in ("talk1", "talk2", "blink"):
        var_im = (
            Image.open(RAW_FILES[f"{name}_{variant}"])
            .convert("RGB")
            .resize(base_size, Image.Resampling.LANCZOS)
        )
        var_rgba = chroma_key_rgba(var_im)
        var_crop = var_rgba[bbox[1] : bbox[3], bbox[0] : bbox[2]]

        if variant == "blink":
            cx, cy, rx, ry = 0.50, 0.34, 0.21, 0.13
        else:
            cx, cy, rx, ry = 0.50, 0.49, 0.20, 0.18

        dist = np.sqrt(((nx - cx) / rx) ** 2 + ((ny - cy) / ry) ** 2)
        zone = 1.0 - np.clip((dist - 0.65) / 0.35, 0.0, 1.0)
        zone_blur = (
            np.asarray(
                Image.fromarray((zone * 255.0).astype(np.uint8), mode="L").filter(
                    ImageFilter.GaussianBlur(radius=10)
                ),
                dtype=np.float32,
            )[..., None]
            / 255.0
        )

        opaque_guard = ((idle_crop[..., 3:4].astype(np.float32) / 255.0) > 0.98).astype(
            np.float32
        )
        mask = zone_blur * opaque_guard

        blended_rgb = (
            idle_crop[..., :3].astype(np.float32) * (1.0 - mask)
            + var_crop[..., :3].astype(np.float32) * mask
        )
        locked = np.zeros_like(idle_crop)
        locked[..., :3] = np.clip(blended_rgb, 0, 255).astype(np.uint8)
        locked[..., 3] = idle_crop[..., 3]

        Image.fromarray(locked, mode="RGBA").save(OUT_HOSTS / f"{name}_{variant}.png")
        print(f"[{name}] Saved pixel-locked {name}_{variant}.png")


def build_studio_layers() -> None:
    bg_im = (
        Image.open(RAW_FILES["studio_bg"])
        .convert("RGB")
        .resize((1920, 1080), Image.Resampling.LANCZOS)
    )
    bg_im.save(OUT_STUDIO / "studio_set_1080p.jpg", quality=95)
    print("[studio] Saved studio_set_1080p.jpg (1920x1080)")

    # Extract exact walnut foreground desk polygon from studio_set_1080p.jpg
    # Desk tabletop back edge sits at y=800 (74.1%), front corners flare from x=278..1642 (back) to x=242..1678 (front y=844..1080)
    rgb = np.asarray(bg_im, dtype=np.uint8)
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

    # Perspective trapezoid matching the walnut desk in studio_set_bg
    top_y = 800.0
    front_y = 846.0
    t_persp = np.clip((yy - top_y) / (front_y - top_y), 0.0, 1.0)
    left_edge = 278.0 * (1.0 - t_persp) + 244.0 * t_persp
    right_edge = 1642.0 * (1.0 - t_persp) + 1676.0 * t_persp

    inside_desk = (yy >= top_y) & (xx >= left_edge) & (xx <= right_edge)
    desk_mask = Image.fromarray((inside_desk.astype(np.uint8) * 255), mode="L").filter(
        ImageFilter.GaussianBlur(radius=1.2)
    )

    desk_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    desk_rgba[..., :3] = rgb
    desk_rgba[..., 3] = np.asarray(desk_mask, dtype=np.uint8)
    Image.fromarray(desk_rgba, mode="RGBA").save(OUT_STUDIO / "studio_desk_fg.png")
    print("[studio] Saved studio_desk_fg.png foreground occlusion layer")


def build_mic_sprite() -> None:
    mic_im = (
        Image.open(RAW_FILES["mic"])
        .convert("RGB")
        .resize((960, 540), Image.Resampling.LANCZOS)
    )
    mic_rgba = chroma_key_rgba(mic_im, low=22.0, high=85.0)
    bbox = auto_crop_bbox(mic_rgba, pad=6)
    mic_crop = mic_rgba[bbox[1] : bbox[3], bbox[0] : bbox[2]]
    Image.fromarray(mic_crop, mode="RGBA").save(OUT_HOSTS / "studio_mic.png")
    print(f"[mic] Saved studio_mic.png ({mic_crop.shape[1]}x{mic_crop.shape[0]})")


if __name__ == "__main__":
    OUT_HOSTS.mkdir(parents=True, exist_ok=True)
    OUT_STUDIO.mkdir(parents=True, exist_ok=True)
    build_studio_layers()
    build_mic_sprite()
    build_locked_host_sprites("cole")
    build_locked_host_sprites("maya")
