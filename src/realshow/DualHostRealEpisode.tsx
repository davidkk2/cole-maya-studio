import { Audio } from "@remotion/media";
import type React from "react";
import {
  AbsoluteFill,
  Img,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  BroadcastHeaderBadge,
  BroadcastStudioStage,
  DualHostBroadcastCaptions,
  RealChapterCard,
  RealFullMediaStage,
  RealSplitEvidenceStage,
} from "./RealMediaStages";
import { resolveSpeechStateAtTime, StudioHostAvatar } from "./StudioHosts";
import type { RealEpisodeManifest } from "./types";

export const DualHostRealEpisode: React.FC<{
  readonly manifest: RealEpisodeManifest;
}> = ({ manifest }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const timeSec = frame / fps;

  const speech = resolveSpeechStateAtTime(manifest.cues, timeSec);
  const isChapterActive = (manifest.chapters ?? []).some((ch) => {
    const startF = Math.round(ch.startSec * fps);
    return frame >= startF && frame < startF + 80;
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#060911" }}>
      {manifest.masterAudioPath && (
        <Audio src={staticFile(manifest.masterAudioPath)} />
      )}

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
            {shot.layout === "studio_dual" ||
            shot.layout === "studio_solo_cole" ||
            shot.layout === "studio_solo_maya" ? (
              <BroadcastStudioStage
                shot={shot}
                speech={speech}
                episodeTitle={manifest.episodeTitle}
              />
            ) : shot.layout === "real_split_evidence" ? (
              <RealSplitEvidenceStage
                shot={shot}
                durationInFrames={durationInFrames}
                speech={speech}
              />
            ) : (
              <RealFullMediaStage
                shot={shot}
                durationInFrames={durationInFrames}
                speech={speech}
                suppressHeadline={isChapterActive}
              />
            )}
          </Sequence>
        );
      })}

      <BroadcastHeaderBadge
        categoryTag={manifest.categoryTag}
        episodeTitle={manifest.episodeTitle}
      />

      {(manifest.chapters ?? []).map((ch) => (
        <Sequence
          key={ch.index}
          from={Math.round(ch.startSec * fps)}
          durationInFrames={80}
        >
          <RealChapterCard chapter={ch} />
        </Sequence>
      ))}

      {/* Dead-Center Locked Subtitles (Never jumps horizontally between cuts) */}
      <DualHostBroadcastCaptions speech={speech} />
    </AbsoluteFill>
  );
};

// ============================================================================
// US YOUTUBE THUMBNAIL (1280x720 — Optically Balanced Left Column + Right Duo)
// ============================================================================
export const DualHostThumbnailUS: React.FC<{
  readonly bgPhotoPath?: string;
  readonly topBadge?: string;
  readonly line1?: string;
  readonly line2?: string;
  readonly line3?: string;
}> = ({
  bgPhotoPath = "archival/alcatraz_island_wide.jpg",
  topBadge = "DECLASSIFIED REAL FOOTAGE",
  line1 = "WHAT",
  line2 = "REALLY",
  line3 = "HAPPENED?",
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#060911", overflow: "hidden" }}>
      <Img
        src={staticFile(bgPhotoPath)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          filter: "contrast(1.14) brightness(0.92) saturate(1.08)",
          transform: "scale(1.03)",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(95deg, rgba(4,7,14,0.92) 0%, rgba(4,7,14,0.62) 28%, rgba(4,7,14,0.16) 46%, rgba(4,7,14,0.24) 100%)",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 24% 52%, rgba(245,158,11,0.16) 0%, transparent 54%)",
        }}
      />

      {/* Left Vertically-Centered Headline Column (x=52..565 — Zero Collision With Cole!) */}
      <div
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          left: 52,
          width: 520,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          gap: 10,
          zIndex: 10,
        }}
      >
        <div
          style={{
            alignSelf: "flex-start",
            display: "inline-flex",
            alignItems: "center",
            height: 36,
            padding: "0 16px",
            marginBottom: 8,
            borderRadius: 7,
            backgroundColor: "#EF4444",
            boxShadow: "0 10px 26px rgba(239,68,68,0.45)",
            fontFamily: "'Inter', 'Arial Black', sans-serif",
            fontSize: 17,
            lineHeight: 1,
            fontWeight: 900,
            letterSpacing: 1.8,
            color: "#FFFFFF",
          }}
        >
          {topBadge}
        </div>
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 106,
            fontWeight: 900,
            lineHeight: 0.92,
            letterSpacing: 2,
            color: "#FFFFFF",
            textShadow: "0 10px 30px rgba(0,0,0,0.95)",
          }}
        >
          {line1}
        </div>
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 106,
            fontWeight: 900,
            lineHeight: 0.92,
            letterSpacing: 2,
            color: "#FFFFFF",
            textShadow: "0 10px 30px rgba(0,0,0,0.95)",
          }}
        >
          {line2}
        </div>
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 104,
            fontWeight: 900,
            lineHeight: 0.92,
            letterSpacing: 1.5,
            color: "#FACC15",
            textShadow:
              "0 10px 30px rgba(0,0,0,0.95), 0 0 34px rgba(250,204,21,0.3)",
          }}
        >
          {line3}
        </div>
      </div>

      {/* Right Foreground: Cole & Maya Signature Presenters (Dominant Framing x=595..1280) */}
      <div
        style={{
          position: "absolute",
          right: 264,
          bottom: -24,
          zIndex: 8,
        }}
      >
        <StudioHostAvatar
          host="cole"
          isSpeaking={false}
          deskSide="left"
          widthPx={455}
          showMic={true}
          forcedSprite="idle"
        />
      </div>
      <div
        style={{
          position: "absolute",
          right: 4,
          bottom: -24,
          zIndex: 9,
        }}
      >
        <StudioHostAvatar
          host="maya"
          isSpeaking={true}
          deskSide="right"
          widthPx={455}
          showMic={true}
          forcedSprite="talk1"
        />
      </div>
    </AbsoluteFill>
  );
};

// ============================================================================
// STUDIO SHOWCASE TEMPLATE MANIFEST (12s / 360 frames @ 30fps)
// ============================================================================
export const STUDIO_TEMPLATE_MANIFEST: RealEpisodeManifest = {
  episodeTitle: "COLE & MAYA · REAL EVIDENCE STUDIO",
  categoryTag: "INVESTIGATIVE",
  totalDurationSec: 12,
  cues: [
    {
      id: "c1",
      speaker: "cole",
      startSec: 0.2,
      endSec: 3.8,
      text: "Tonight we're skipping every rumor and looking strictly at the real footage.",
      expression: "emphatic",
    },
    {
      id: "c2",
      speaker: "maya",
      startSec: 4.1,
      endSec: 7.8,
      text: "Look at the tidal current rushing right past the bridge towers in real time.",
      expression: "curious",
    },
    {
      id: "c3",
      speaker: "cole",
      startSec: 8.1,
      endSec: 11.8,
      text: "Every single photograph in the federal archive points to the exact same night.",
      expression: "serious",
    },
  ],
  shots: [
    {
      id: "s1",
      startSec: 0,
      endSec: 4,
      layout: "studio_dual",
      monitorMediaPath: "archival/alcatraz_island_wide.jpg",
      locationDate: "MANHATTAN STUDIO · LIVE",
      headline: "100% REAL ARCHIVAL FOOTAGE & PHOTOGRAPHY",
    },
    {
      id: "s2",
      startSec: 4,
      endSec: 8,
      layout: "real_video_pip",
      mediaPath: "studio/demo_goldengate_real_1080p.mp4",
      videoTrimStartSec: 0.5,
      pipHost: "maya",
      pipCorner: "bottom-right",
      sourceTag: "REAL 1080P FOOTAGE · CC BY-SA 4.0",
      locationDate: "GOLDEN GATE STRAIT · SAN FRANCISCO BAY",
      headline: "TIDAL CURRENT FIELD RECORDING",
    },
    {
      id: "s3",
      startSec: 8,
      endSec: 12,
      layout: "real_split_evidence",
      mediaPath: "archival/fbi_dummy_head.jpg",
      pipHost: "cole",
      sourceTag: "FBI FORENSIC PHOTOGRAPH · 1962",
      headline: "VERIFIED FEDERAL CASE EXHIBIT",
      facts: [
        {
          label: "EXHIBIT RECORD",
          value: "FBI Physical Archive #62-Alcatraz",
          accent: "amber",
        },
        {
          label: "CHANNEL STANDARD",
          value: "Zero Scene Animation · 100% Real Media",
          accent: "cyan",
        },
      ],
      notes: [
        "Only verified real-world video footage, archival photography, and declassified documents — hosted by Cole & Maya.",
      ],
    },
  ],
};
