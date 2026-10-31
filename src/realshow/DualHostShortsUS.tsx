import { Audio, Video } from "@remotion/media";
import type React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  type ActiveSpeechState,
  resolveSpeechStateAtTime,
  StudioHostAvatar,
} from "./StudioHosts";
import type { DialogueCue, RealEpisodeManifest, RealShotSpec } from "./types";

const COLORS = {
  bgDeep: "#060911",
  panelDark: "rgba(8, 12, 22, 0.94)",
  coleAmber: "#F59E0B",
  mayaCyan: "#38BDF8",
  redAlert: "#EF4444",
  textPrimary: "#F8FAFC",
  textSecondary: "#CBD5E1",
  borderGlass: "rgba(148, 163, 184, 0.28)",
};

function isVideoAsset(pathStr?: string): boolean {
  if (!pathStr) return false;
  const lower = pathStr.toLowerCase();
  return lower.endsWith(".mp4") || lower.endsWith(".webm") || lower.endsWith(".mov");
}

/**
 * Splits a spoken sentence into rapid 5–7 word kinetic chunks synchronized
 * proportionally across the cue's [startSec, endSec] span for high-retention Shorts reading.
 */
function getActiveShortPhrase(cue: DialogueCue, timeSec: number): string {
  const words = cue.text.trim().split(/\s+/).filter(Boolean);
  if (words.length <= 7) {
    return cue.text.trim();
  }
  const chunkSize = 6;
  const chunks: string[] = [];
  for (let i = 0; i < words.length; i += chunkSize) {
    chunks.push(words.slice(i, i + chunkSize).join(" "));
  }
  const span = Math.max(0.2, cue.endSec - cue.startSec);
  const progress = Math.min(0.999, Math.max(0, (timeSec - cue.startSec) / span));
  const idx = Math.min(chunks.length - 1, Math.floor(progress * chunks.length));
  return chunks[idx] ?? chunks[0] ?? "";
}

const ShortEvidenceViewport: React.FC<{
  readonly shot: RealShotSpec;
  readonly durationInFrames: number;
}> = ({ shot, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const mediaPath = shot.mediaPath || shot.monitorMediaPath || "studio/studio_set_1080p.jpg";
  const isVid = isVideoAsset(mediaPath);
  const baseScale = shot.cropScale ?? 1.04;
  const kenBurns = interpolate(
    frame,
    [0, Math.max(30, durationInFrames)],
    [baseScale, baseScale + (isVid ? 0.03 : 0.08)],
    { extrapolateRight: "clamp" },
  );

  const firstFact = shot.facts?.[0];

  return (
    <div
      style={{
        position: "absolute",
        left: 38,
        right: 38,
        top: 284,
        height: 714,
        borderRadius: 26,
        overflow: "hidden",
        backgroundColor: "#050811",
        border: `2px solid ${COLORS.borderGlass}`,
        boxShadow: "0 24px 56px rgba(0,0,0,0.88)",
        zIndex: 6,
      }}
    >
      {/* Blurred Atmospheric Fill for 'contain' Archival Documents */}
      {shot.mediaFit === "contain" && !isVid && (
        <Img
          src={staticFile(mediaPath)}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: "blur(24px) brightness(0.35)",
            transform: "scale(1.12)",
          }}
        />
      )}

      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `scale(${shot.mediaFit === "contain" ? 1 : kenBurns})`,
          transformOrigin: "center center",
        }}
      >
        {isVid ? (
          <Video
            src={staticFile(mediaPath)}
            muted
            loop
            objectFit="cover"
            trimBefore={Math.round((shot.videoTrimStartSec ?? 0) * fps)}
            style={{
              width: "100%",
              height: "100%",
              filter: "contrast(1.06) saturate(1.04)",
            }}
          />
        ) : (
          <Img
            src={staticFile(mediaPath)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: shot.mediaFit ?? "cover",
              objectPosition: shot.mediaObjectPosition ?? "50% 22%",
              filter: "contrast(1.06) brightness(0.96)",
            }}
          />
        )}
      </div>

      {/* Subtle Top & Bottom Readability Gradients Inside Evidence Frame */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(4,7,14,0.68) 0%, rgba(4,7,14,0.04) 26%, rgba(4,7,14,0.06) 68%, rgba(4,7,14,0.82) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Top-Left Primary Source Chyron */}
      {(shot.sourceTag || shot.locationDate) && (
        <div
          style={{
            position: "absolute",
            left: 22,
            top: 20,
            maxWidth: 910,
            padding: "8px 16px",
            borderRadius: 10,
            backgroundColor: "rgba(6, 9, 17, 0.88)",
            border: "1px solid rgba(56, 189, 248, 0.42)",
            display: "inline-flex",
            alignItems: "center",
            gap: 10,
            fontFamily: "'Consolas', 'Courier New', monospace",
            fontSize: 18,
            fontWeight: 800,
            letterSpacing: 1.4,
            color: COLORS.mayaCyan,
          }}
        >
          <span
            style={{
              width: 9,
              height: 9,
              borderRadius: "50%",
              backgroundColor: COLORS.redAlert,
              display: "inline-block",
              flexShrink: 0,
            }}
          />
          <span
            style={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {[shot.sourceTag, shot.locationDate].filter(Boolean).join(" · ")}
          </span>
        </div>
      )}

      {/* Shot Sub-Headline / Verified Evidence Fact Strip at Bottom of Frame */}
      {(firstFact || shot.headline) && (
        <div
          style={{
            position: "absolute",
            left: 22,
            right: 22,
            bottom: 20,
            padding: "12px 18px",
            borderRadius: 14,
            backgroundColor: "rgba(8, 12, 22, 0.9)",
            borderLeft: `5px solid ${COLORS.coleAmber}`,
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          {firstFact ? (
            <>
              <div
                style={{
                  fontFamily: "'Consolas', 'Courier New', monospace",
                  fontSize: 16,
                  fontWeight: 800,
                  letterSpacing: 1.6,
                  color: COLORS.coleAmber,
                }}
              >
                {firstFact.label.toUpperCase()}
              </div>
              <div
                style={{
                  fontFamily: "'Inter', 'Segoe UI', sans-serif",
                  fontSize: 23,
                  lineHeight: 1.2,
                  fontWeight: 800,
                  color: COLORS.textPrimary,
                }}
              >
                {firstFact.value}
              </div>
            </>
          ) : (
            <div
              style={{
                fontFamily: "'Inter', 'Arial Black', sans-serif",
                fontSize: 23,
                lineHeight: 1.18,
                fontWeight: 900,
                letterSpacing: 0.5,
                color: COLORS.textPrimary,
              }}
            >
              {shot.headline}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const ShortStudioStage: React.FC<{
  readonly speech: ActiveSpeechState;
}> = ({ speech }) => {
  const coleSpeaking = speech.activeSpeaker === "cole";
  const mayaSpeaking = speech.activeSpeaker === "maya";

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 1088,
        bottom: 0,
        overflow: "hidden",
        backgroundColor: "#060911",
      }}
    >
      <Img
        src={staticFile("studio/studio_set_1080p.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          filter: "brightness(0.55) contrast(1.1)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(6,9,17,0.92) 0%, rgba(6,9,17,0.18) 22%, rgba(6,9,17,0.45) 75%, rgba(4,6,12,0.95) 100%)",
        }}
      />

      {/* Cole (Left) & Maya (Shifted Left of x=920 Right-Side Shorts Action Icons!) */}
      <div
        style={{
          position: "absolute",
          left: 16,
          top: 96,
          transform: coleSpeaking ? "scale(1.04)" : "scale(0.98)",
          transformOrigin: "bottom center",
          opacity: mayaSpeaking ? 0.88 : 1,
        }}
      >
        <StudioHostAvatar
          host="cole"
          isSpeaking={coleSpeaking}
          cueText={coleSpeaking ? speech.activeCue?.text : ""}
          expression={speech.coleExpression}
          deskSide="left"
          widthPx={455}
          showMic={true}
        />
      </div>

      <div
        style={{
          position: "absolute",
          left: 454,
          top: 96,
          transform: mayaSpeaking ? "scale(1.04)" : "scale(0.98)",
          transformOrigin: "bottom center",
          opacity: coleSpeaking ? 0.88 : 1,
        }}
      >
        <StudioHostAvatar
          host="maya"
          isSpeaking={mayaSpeaking}
          cueText={mayaSpeaking ? speech.activeCue?.text : ""}
          expression={speech.mayaExpression}
          deskSide="right"
          widthPx={455}
          showMic={true}
        />
      </div>

      {/* Walnut Studio Desk Ledge Anchoring Host Torsos (Above Bottom Shorts UI Overlay) */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 516,
          bottom: 0,
          background:
            "linear-gradient(180deg, #3A261B 0%, #241710 8%, #0B0F1A 20%, #050810 100%)",
          borderTop: "3px solid rgba(245, 158, 11, 0.55)",
          boxShadow: "0 -16px 36px rgba(0,0,0,0.9)",
        }}
      />

      {/* Speaker Nameplates Aligned Under Cole (cx=244) & Maya (cx=682), Safely Above y=1690 Bottom Shorts UI */}
      <div
        style={{
          position: "absolute",
          left: 244,
          top: 540,
          transform: "translateX(-50%)",
          padding: "7px 20px",
          borderRadius: 999,
          backgroundColor: "rgba(9,13,22,0.95)",
          border: `2px solid ${coleSpeaking ? COLORS.coleAmber : "rgba(148,163,184,0.3)"}`,
          fontFamily: "'Inter', 'Arial Black', sans-serif",
          fontSize: 19,
          fontWeight: 900,
          letterSpacing: 1.8,
          color: coleSpeaking ? COLORS.coleAmber : COLORS.textSecondary,
          whiteSpace: "nowrap",
        }}
      >
        COLE
      </div>
      <div
        style={{
          position: "absolute",
          left: 682,
          top: 540,
          transform: "translateX(-50%)",
          padding: "7px 20px",
          borderRadius: 999,
          backgroundColor: "rgba(9,13,22,0.95)",
          border: `2px solid ${mayaSpeaking ? COLORS.mayaCyan : "rgba(148,163,184,0.3)"}`,
          fontFamily: "'Inter', 'Arial Black', sans-serif",
          fontSize: 19,
          fontWeight: 900,
          letterSpacing: 1.8,
          color: mayaSpeaking ? COLORS.mayaCyan : COLORS.textSecondary,
          whiteSpace: "nowrap",
        }}
      >
        MAYA
      </div>
    </div>
  );
};

/**
 * 9:16 Vertical YouTube Shorts Composition (1080x1920, 30fps)
 * Safe-zone engineered for mobile Shorts feed:
 * - Top hook headline: y=132..276
 * - Real 100% photographic/video evidence stage: y=292..1060
 * - Rapid kinetic center-seam captions: y=1024..1168 (x=54..906, clear of right-side icons)
 * - Studio hosts Cole & Maya: y=1184..1660 (Maya shifted left of x=910 right-side icons, desk above y=1670 bottom title overlay)
 */
export const DualHostShortsUS: React.FC<{
  readonly manifest: RealEpisodeManifest;
}> = ({ manifest }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const timeSec = frame / fps;

  const speech = resolveSpeechStateAtTime(manifest.cues, timeSec);
  const activeCue = speech.activeCue;
  const isCole = activeCue?.speaker === "cole";
  const accentColor = isCole ? COLORS.coleAmber : COLORS.mayaCyan;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bgDeep, overflow: "hidden" }}>
      {manifest.masterAudioPath && (
        <Audio src={staticFile(manifest.masterAudioPath)} />
      )}

      {/* Top Hook Banner (Safely Below Status Bar at y=126) */}
      <div
        style={{
          position: "absolute",
          left: 42,
          right: 42,
          top: 124,
          height: 152,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 10,
          zIndex: 10,
        }}
      >
        <div
          style={{
            padding: "6px 18px",
            borderRadius: 999,
            backgroundColor: "rgba(239, 68, 68, 0.92)",
            fontFamily: "'Consolas', 'Courier New', monospace",
            fontSize: 17,
            fontWeight: 900,
            letterSpacing: 2.2,
            color: "#FFFFFF",
          }}
        >
          COLE & MAYA · {manifest.categoryTag || "PRIMARY RECORD"}
        </div>
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 44,
            lineHeight: 1.04,
            fontWeight: 900,
            letterSpacing: 1,
            color: COLORS.textPrimary,
            textAlign: "center",
            textTransform: "uppercase",
            textShadow: "0 8px 24px rgba(0,0,0,0.95)",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {manifest.episodeTitle}
        </div>
      </div>

      {/* Upper 100% Real Visual Evidence Viewport */}
      {manifest.shots.map((shot) => {
        const fromFrame = Math.round(shot.startSec * fps);
        const durationInFrames = Math.max(
          1,
          Math.round((shot.endSec - shot.startSec) * fps),
        );
        return (
          <Sequence
            key={shot.id}
            from={fromFrame}
            durationInFrames={durationInFrames}
          >
            <ShortEvidenceViewport
              shot={shot}
              durationInFrames={durationInFrames}
            />
          </Sequence>
        );
      })}

      {/* Lower Dual-Host Manhattan Studio Stage */}
      <ShortStudioStage speech={speech} />

      {/* Rapid Kinetic Seam Captions (22px Clear Below Evidence Frame, Clear of Right-Side Shorts Icons!) */}
      {activeCue && (
        <div
          style={{
            position: "absolute",
            left: 42,
            right: 116,
            top: 1020,
            zIndex: 20,
            display: "flex",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              padding: "14px 24px",
              borderRadius: 18,
              backgroundColor: COLORS.panelDark,
              border: `2.5px solid ${accentColor}`,
              boxShadow: "0 18px 40px rgba(0,0,0,0.92)",
              display: "inline-flex",
              alignItems: "center",
              gap: 14,
              maxWidth: "100%",
            }}
          >
            <span
              style={{
                padding: "5px 12px",
                borderRadius: 8,
                backgroundColor: accentColor,
                color: "#060911",
                fontFamily: "'Inter', 'Arial Black', sans-serif",
                fontSize: 18,
                fontWeight: 900,
                letterSpacing: 1.4,
                flexShrink: 0,
              }}
            >
              {isCole ? "COLE" : "MAYA"}
            </span>
            <span
              style={{
                fontFamily: "'Inter', 'Segoe UI', sans-serif",
                fontSize: 29,
                lineHeight: 1.22,
                fontWeight: 800,
                color: COLORS.textPrimary,
              }}
            >
              {getActiveShortPhrase(activeCue, timeSec)}
            </span>
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
