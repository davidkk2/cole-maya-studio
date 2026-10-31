import type React from "react";
import { Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { DialogueCue, HostExpression, HostId } from "./types";

export interface ActiveSpeechState {
  readonly activeSpeaker: HostId | null;
  readonly activeCue: DialogueCue | null;
  readonly coleExpression: HostExpression;
  readonly mayaExpression: HostExpression;
}

export function resolveSpeechStateAtTime(
  cues: readonly DialogueCue[],
  timeSec: number,
): ActiveSpeechState {
  let current: DialogueCue | null = null;
  let prevColeExpr: HostExpression = "neutral";
  let prevMayaExpr: HostExpression = "curious";

  for (const cue of cues) {
    if (cue.startSec <= timeSec) {
      if (cue.speaker === "cole" && cue.expression) {
        prevColeExpr = cue.expression;
      } else if (cue.speaker === "maya" && cue.expression) {
        prevMayaExpr = cue.expression;
      }
    }
    if (timeSec >= cue.startSec && timeSec <= cue.endSec) {
      current = cue;
      break;
    }
  }

  return {
    activeSpeaker: current ? current.speaker : null,
    activeCue: current,
    coleExpression:
      current?.speaker === "cole" && current.expression
        ? current.expression
        : prevColeExpr,
    mayaExpression:
      current?.speaker === "maya" && current.expression
        ? current.expression
        : prevMayaExpr,
  };
}

type SpriteState = "idle" | "talk1" | "talk2" | "blink";

function resolveSpriteState(
  host: HostId,
  isSpeaking: boolean,
  cueText: string,
  frame: number,
  fps: number,
  expression: HostExpression,
): SpriteState {
  const isCole = host === "cole";
  // Natural deterministic blink (~every 124 frames, 4 frames long, offset per host)
  const blinkCycle = (frame + (isCole ? 29 : 83)) % 124;
  if (blinkCycle >= 0 && blinkCycle <= 3) {
    return "blink";
  }

  if (!isSpeaking || !cueText) {
    if (expression === "shocked") {
      return "talk1";
    }
    return "idle";
  }

  // Deterministic syllable-cadence viseme selector (~9.5 syllables/sec)
  const charIdx =
    Math.floor((frame / fps) * 10.5) % Math.max(1, cueText.length);
  const ch = cueText[charIdx]?.toLowerCase() ?? "a";
  const wave =
    0.5 +
    0.35 * Math.sin(frame * 0.78) +
    0.22 * Math.cos(frame * 1.27 + charIdx * 0.5);

  if (" ,.—?;:!mbpv".includes(ch) || wave < 0.28) {
    return "idle";
  }
  if (("aouwy".includes(ch) && wave > 0.52) || wave > 0.78) {
    return "talk2";
  }
  return "talk1";
}

export interface StudioHostAvatarProps {
  readonly host: HostId;
  readonly isSpeaking: boolean;
  readonly cueText?: string;
  readonly expression?: HostExpression;
  readonly deskSide?: "left" | "right" | "center";
  readonly widthPx?: number;
  readonly showMic?: boolean;
  /** Override sprite state for static thumbnails if desired */
  readonly forcedSprite?: SpriteState;
}

export const StudioHostAvatar: React.FC<StudioHostAvatarProps> = ({
  host,
  isSpeaking,
  cueText = "",
  expression = "neutral",
  deskSide = host === "cole" ? "left" : "right",
  widthPx = 500,
  showMic = true,
  forcedSprite,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isCole = host === "cole";
  const phase = isCole ? 0 : 41;
  const f = frame + phase;

  const activeSprite =
    forcedSprite ??
    resolveSpriteState(host, isSpeaking, cueText, frame, fps, expression);

  // Subtle organic broadcast motion: breathing + speaking emphasis + attentive listener nod
  const breathY = Math.sin(f / 24) * 2.2;
  const speakBobY = isSpeaking ? Math.sin(frame * 0.36) * 2.1 : 0;
  const listenNodY = !isSpeaking ? Math.max(0, Math.sin(f / 42)) * 2.4 : 0;
  const tiltDeg = isSpeaking
    ? Math.sin(frame * 0.14 + phase) * 1.15
    : deskSide === "left"
      ? 0.55 + Math.sin(f / 50) * 0.45
      : deskSide === "right"
        ? -0.55 + Math.sin(f / 50) * 0.45
        : 0;

  const heightPx = Math.round(widthPx * 0.965);
  const accentGlow = isCole
    ? "rgba(245, 158, 11, 0.26)"
    : "rgba(56, 189, 248, 0.26)";

  const sprites: readonly SpriteState[] = ["idle", "talk1", "talk2", "blink"];

  return (
    <div
      style={{
        width: widthPx,
        height: heightPx,
        position: "relative",
        userSelect: "none",
      }}
    >
      {/* Subtle Studio Backlight Rim Behind Active Speaker */}
      <div
        style={{
          position: "absolute",
          left: "16%",
          right: "16%",
          top: "10%",
          bottom: "8%",
          borderRadius: "50%",
          background: `radial-gradient(circle, ${accentGlow} 0%, transparent 70%)`,
          opacity: isSpeaking ? 1 : 0.3,
          filter: "blur(18px)",
          pointerEvents: "none",
        }}
      />

      {/* Pre-Mounted Pixel-Locked RGBA Character Sprites (Zero Decode Flicker!) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translateY(${breathY + speakBobY + listenNodY}px) rotate(${tiltDeg}deg)`,
          transformOrigin: "50% 82%",
          filter: "drop-shadow(0 18px 28px rgba(0, 0, 0, 0.68))",
        }}
      >
        {sprites.map((sp) => (
          <Img
            key={sp}
            src={staticFile(`studio/hosts/${host}_${sp}.png`)}
            style={{
              position: "absolute",
              inset: 0,
              width: "100%",
              height: "100%",
              objectFit: "contain",
              opacity: activeSprite === sp ? 1 : 0,
            }}
          />
        ))}
      </div>

      {/* Real Studio Shure SM7B Boom Microphone (Optional — e.g. for PiP / Thumbnails) */}
      {showMic && (
        <div
          style={{
            position: "absolute",
            bottom: -Math.round(heightPx * 0.08),
            left: deskSide === "right" ? undefined : -Math.round(widthPx * 0.08),
            right:
              deskSide === "right" ? -Math.round(widthPx * 0.08) : undefined,
            width: Math.round(widthPx * 0.54),
            height: Math.round(heightPx * 0.44),
            transform: deskSide === "right" ? "scaleX(-1)" : undefined,
            filter: "drop-shadow(0 12px 20px rgba(0,0,0,0.8))",
            pointerEvents: "none",
          }}
        >
          <Img
            src={staticFile("studio/hosts/studio_mic.png")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "contain",
            }}
          />
        </div>
      )}
    </div>
  );
};
