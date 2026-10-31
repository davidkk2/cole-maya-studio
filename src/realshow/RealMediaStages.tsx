import { Video } from "@remotion/media";
import type React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { type ActiveSpeechState, StudioHostAvatar } from "./StudioHosts";
import type { HostId, RealChapterMarker, RealShotSpec } from "./types";

const FONT_DISPLAY = "'Inter', 'Segoe UI', Arial, sans-serif";
const FONT_MONO = "'Consolas', 'Courier New', monospace";

// Master 1920x1080 Broadcast Safe-Zone Rails
const SAFE_X = 56;
const SAFE_TOP = 42;
const SAFE_BOTTOM = 40;

// ============================================================================
// 1. PICTURE-IN-PICTURE (PiP) HOST CORNER WINDOW (Flush to 56px Right/Left Rail)
// ============================================================================
export const HostPipOverlay: React.FC<{
  readonly host: HostId;
  readonly speech: ActiveSpeechState;
  readonly corner?: "bottom-right" | "bottom-left";
}> = ({ host, speech, corner = "bottom-right" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({
    frame,
    fps,
    config: { damping: 200 },
    durationInFrames: 16,
  });

  const isCole = host === "cole";
  const accent = isCole ? "#F59E0B" : "#38BDF8";
  const isSpeaking = speech.activeSpeaker === host;
  const expr = isCole ? speech.coleExpression : speech.mayaExpression;

  return (
    <div
      style={{
        position: "absolute",
        bottom: SAFE_BOTTOM,
        right: corner === "bottom-right" ? SAFE_X : undefined,
        left: corner === "bottom-left" ? SAFE_X : undefined,
        width: 312,
        height: 288,
        borderRadius: 16,
        overflow: "hidden",
        backgroundColor: "#070A12",
        border: `2px solid ${isSpeaking ? accent : "rgba(148,163,184,0.38)"}`,
        boxShadow: `0 24px 52px rgba(0,0,0,0.84), 0 0 24px ${isSpeaking ? `${accent}3D` : "transparent"}`,
        transform: `translateY(${interpolate(enter, [0, 1], [24, 0])}px) scale(${interpolate(enter, [0, 1], [0.95, 1])})`,
        opacity: enter,
        zIndex: 30,
      }}
    >
      {/* Real Manhattan Podcast Studio Backdrop Inside PiP */}
      <Img
        src={staticFile("studio/studio_set_1080p.jpg")}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: "50% 35%",
          filter: "brightness(0.55) blur(3px)",
          transform: "scale(1.18)",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(circle at 50% 38%, rgba(15,23,42,0.12) 0%, rgba(5,8,15,0.78) 100%)",
        }}
      />

      {/* Painterly Host Sprite with Generous Top Headroom (16px) */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: 16,
          transform: "translateX(-50%)",
        }}
      >
        <StudioHostAvatar
          host={host}
          isSpeaking={isSpeaking}
          cueText={speech.activeCue?.text ?? ""}
          expression={expr}
          deskSide={isCole ? "left" : "right"}
          widthPx={248}
          showMic={true}
        />
      </div>

      {/* Bottom Broadcast Status Bar (Optically Centered) */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: 36,
          background: "linear-gradient(90deg, #070A12 0%, #0F172A 100%)",
          borderTop: "1px solid rgba(255,255,255,0.14)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 14px",
        }}
      >
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: isSpeaking ? accent : "#475569",
              boxShadow: isSpeaking ? `0 0 10px ${accent}` : "none",
            }}
          />
          <span
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 12,
              lineHeight: 1,
              fontWeight: 800,
              letterSpacing: 1.4,
              color: "#F8FAFC",
            }}
          >
            {isCole ? "COLE" : "MAYA"}
          </span>
        </div>
        <span
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            lineHeight: 1,
            fontWeight: 700,
            color: isSpeaking ? accent : "#64748B",
            letterSpacing: 1,
          }}
        >
          {isSpeaking ? "ON AIR" : "STUDIO"}
        </span>
      </div>
    </div>
  );
};

// ============================================================================
// 2. PHOTOREALISTIC MANHATTAN PODCAST STUDIO STAGE (Dual & Solo Cuts)
// ============================================================================
export const BroadcastStudioStage: React.FC<{
  readonly shot: RealShotSpec;
  readonly speech: ActiveSpeechState;
  readonly episodeTitle: string;
}> = ({ shot, speech, episodeTitle }) => {
  const frame = useCurrentFrame();

  const camScale = interpolate(frame, [0, 180], [1, 1.03], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const cameraFocusTransform =
    shot.layout === "studio_solo_cole"
      ? `scale(${1.2 * camScale}) translate(13%, -4.5%)`
      : shot.layout === "studio_solo_maya"
        ? `scale(${1.2 * camScale}) translate(-13%, -4.5%)`
        : `scale(${camScale})`;

  const monitorSrc = shot.monitorMediaPath || shot.mediaPath;
  const coleSpeaking = speech.activeSpeaker === "cole";
  const mayaSpeaking = speech.activeSpeaker === "maya";

  // Exact host centerlines: Cole left=256, width=508 -> cx=510; Maya right=256, width=508 -> cx=1410
  const hostWidth = 508;
  const coleLeft = 256;
  const coleCenterX = coleLeft + hostWidth / 2; // 510
  const mayaRight = 256;
  const mayaCenterX = 1920 - mayaRight - hostWidth / 2; // 1410

  return (
    <AbsoluteFill style={{ backgroundColor: "#06080F", overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          transform: cameraFocusTransform,
          transformOrigin: "50% 54%",
        }}
      >
        {/* LAYER 1: Real 8K Manhattan Night Podcast Studio Set */}
        <Img
          src={staticFile("studio/studio_set_1080p.jpg")}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />

        {/* LAYER 2: Center Studio Broadcast Display (Top aligned to SAFE_TOP = 42px) */}
        <div
          style={{
            position: "absolute",
            top: SAFE_TOP,
            left: "50%",
            transform: "translateX(-50%)",
            width: 580,
            height: 326,
            borderRadius: 14,
            overflow: "hidden",
            backgroundColor: "#070B14",
            border: "2px solid rgba(148,163,184,0.34)",
            boxShadow:
              "0 26px 64px rgba(0,0,0,0.86), 0 0 38px rgba(15,23,42,0.8)",
          }}
        >
          {monitorSrc ? (
            <Img
              src={staticFile(monitorSrc)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: "brightness(0.88) contrast(1.08)",
                transform: `scale(${interpolate(frame, [0, 180], [1.02, 1.09], {
                  extrapolateRight: "clamp",
                })})`,
              }}
            />
          ) : (
            <Img
              src={staticFile("studio/nyc_night_skyline.jpg")}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
              }}
            />
          )}
          <div
            style={{
              position: "absolute",
              inset: 0,
              background:
                "linear-gradient(180deg, rgba(6,10,18,0.76) 0%, rgba(6,10,18,0.06) 34%, rgba(6,10,18,0.88) 100%)",
            }}
          />

          {/* Matched Left & Right Pills on Monitor Top Rail */}
          <div
            style={{
              position: "absolute",
              top: 12,
              left: 14,
              right: 14,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                height: 24,
                padding: "0 10px",
                borderRadius: 6,
                backgroundColor: "rgba(7,10,18,0.88)",
                border: "1px solid rgba(245,158,11,0.48)",
                fontFamily: FONT_MONO,
                fontSize: 11,
                lineHeight: 1,
                fontWeight: 800,
                letterSpacing: 1.3,
                color: "#F59E0B",
              }}
            >
              CASE ARCHIVE FEED
            </span>
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                height: 24,
                padding: "0 10px",
                borderRadius: 6,
                backgroundColor: "rgba(7,10,18,0.82)",
                border: "1px solid rgba(255,255,255,0.16)",
                fontFamily: FONT_MONO,
                fontSize: 11,
                lineHeight: 1,
                fontWeight: 700,
                color: "#E2E8F0",
                letterSpacing: 1.1,
              }}
            >
              {shot.locationDate || "NEW YORK STUDIO"}
            </span>
          </div>

          {/* Centered Monitor Headline Footer */}
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              right: 0,
              padding: "10px 18px 13px",
              textAlign: "center",
              fontFamily: FONT_DISPLAY,
              fontSize: 16,
              lineHeight: 1.2,
              fontWeight: 800,
              color: "#F8FAFC",
              letterSpacing: 0.5,
              textShadow: "0 2px 10px rgba(0,0,0,0.95)",
            }}
          >
            {shot.headline || episodeTitle}
          </div>
        </div>

        {/* LAYER 3: Cole (Left) & Maya (Right) Seated Physically Behind Walnut Desk */}
        <div
          style={{
            position: "absolute",
            left: coleLeft,
            top: 320,
          }}
        >
          <StudioHostAvatar
            host="cole"
            isSpeaking={coleSpeaking}
            cueText={speech.activeCue?.text ?? ""}
            expression={speech.coleExpression}
            deskSide="left"
            widthPx={hostWidth}
            showMic={false}
          />
        </div>

        <div
          style={{
            position: "absolute",
            right: mayaRight,
            top: 320,
          }}
        >
          <StudioHostAvatar
            host="maya"
            isSpeaking={mayaSpeaking}
            cueText={speech.activeCue?.text ?? ""}
            expression={speech.mayaExpression}
            deskSide="right"
            widthPx={hostWidth}
            showMic={false}
          />
        </div>

        {/* LAYER 4: Foreground Real Walnut Broadcast Desk Occlusion */}
        <Img
          src={staticFile("studio/studio_desk_fg.png")}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            pointerEvents: "none",
          }}
        />

        {/* Natural Contact Shadows on Walnut Tabletop */}
        <div
          style={{
            position: "absolute",
            left: coleCenterX - 205,
            top: 798,
            width: 410,
            height: 28,
            borderRadius: "50%",
            background:
              "radial-gradient(ellipse, rgba(0,0,0,0.58) 0%, transparent 72%)",
            pointerEvents: "none",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: mayaCenterX - 205,
            top: 798,
            width: 410,
            height: 28,
            borderRadius: "50%",
            background:
              "radial-gradient(ellipse, rgba(0,0,0,0.58) 0%, transparent 72%)",
            pointerEvents: "none",
          }}
        />

        {/* Left & Right Real Shure SM7B Studio Boom Microphones */}
        <div
          style={{
            position: "absolute",
            left: 238,
            top: 596,
            width: 286,
            height: 224,
            filter: "drop-shadow(0 16px 22px rgba(0,0,0,0.78))",
            pointerEvents: "none",
          }}
        >
          <Img
            src={staticFile("studio/hosts/studio_mic.png")}
            style={{ width: "100%", height: "100%", objectFit: "contain" }}
          />
        </div>

        <div
          style={{
            position: "absolute",
            right: 238,
            top: 596,
            width: 286,
            height: 224,
            transform: "scaleX(-1)",
            filter: "drop-shadow(0 16px 22px rgba(0,0,0,0.78))",
            pointerEvents: "none",
          }}
        >
          <Img
            src={staticFile("studio/hosts/studio_mic.png")}
            style={{ width: "100%", height: "100%", objectFit: "contain" }}
          />
        </div>

        {/* Desk Nameplates Strictly Centered on Each Host's Exact Centerline (cx=510 & cx=1410) */}
        <div
          style={{
            position: "absolute",
            top: 884,
            left: coleCenterX,
            transform: "translateX(-50%)",
            display: "inline-flex",
            alignItems: "center",
            gap: 9,
            height: 32,
            padding: "0 16px",
            borderRadius: 8,
            backgroundColor: "rgba(9,13,22,0.88)",
            border: `1px solid ${coleSpeaking ? "rgba(245,158,11,0.68)" : "rgba(148,163,184,0.22)"}`,
            boxShadow: "0 8px 20px rgba(0,0,0,0.55)",
          }}
        >
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: coleSpeaking ? "#F59E0B" : "#475569",
              boxShadow: coleSpeaking ? "0 0 10px #F59E0B" : "none",
            }}
          />
          <span
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 12,
              lineHeight: 1,
              fontWeight: 800,
              letterSpacing: 1.5,
              color: "#F8FAFC",
            }}
          >
            COLE
          </span>
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              lineHeight: 1,
              color: "#94A3B8",
            }}
          >
            LEAD HOST
          </span>
        </div>

        <div
          style={{
            position: "absolute",
            top: 884,
            left: mayaCenterX,
            transform: "translateX(-50%)",
            display: "inline-flex",
            alignItems: "center",
            gap: 9,
            height: 32,
            padding: "0 16px",
            borderRadius: 8,
            backgroundColor: "rgba(9,13,22,0.88)",
            border: `1px solid ${mayaSpeaking ? "rgba(56,189,248,0.68)" : "rgba(148,163,184,0.22)"}`,
            boxShadow: "0 8px 20px rgba(0,0,0,0.55)",
          }}
        >
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: mayaSpeaking ? "#38BDF8" : "#475569",
              boxShadow: mayaSpeaking ? "0 0 10px #38BDF8" : "none",
            }}
          />
          <span
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 12,
              lineHeight: 1,
              fontWeight: 800,
              letterSpacing: 1.5,
              color: "#F8FAFC",
            }}
          >
            MAYA
          </span>
          <span
            style={{
              fontFamily: FONT_MONO,
              fontSize: 11,
              lineHeight: 1,
              color: "#94A3B8",
            }}
          >
            CO-HOST
          </span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ============================================================================
// 3. 100% REAL VIDEO & REAL PHOTOGRAPH DOCUMENTARY STAGE (+ Optional PiP)
// ============================================================================
export const RealFullMediaStage: React.FC<{
  readonly shot: RealShotSpec;
  readonly durationInFrames: number;
  readonly speech: ActiveSpeechState;
  readonly suppressHeadline?: boolean;
}> = ({ shot, durationInFrames, speech, suppressHeadline = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isVideo =
    shot.layout === "real_video_full" || shot.layout === "real_video_pip";
  const showPip =
    shot.layout === "real_video_pip" || shot.layout === "real_photo_pip";
  const pipHost: HostId = shot.pipHost ?? speech.activeSpeaker ?? "cole";

  const baseZoom = shot.cropScale ?? 1.04;
  const mediaScale = interpolate(
    frame,
    [0, Math.max(30, durationInFrames)],
    [baseZoom, baseZoom + 0.06],
    {
      easing: Easing.inOut(Easing.quad),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );

  const mediaPath = shot.mediaPath || "archival/alcatraz_island_wide.jpg";

  return (
    <AbsoluteFill style={{ backgroundColor: "#05070D", overflow: "hidden" }}>
      {isVideo && shot.verticalSocialVideo ? (
        <>
          {/* Atmospheric Blurred Backdrop From Real Vertical Video */}
          <AbsoluteFill
            style={{
              transform: "scale(1.18)",
              filter: "blur(30px) brightness(0.34) saturate(0.92)",
            }}
          >
            <Video
              src={staticFile(mediaPath)}
              muted
              loop
              objectFit="cover"
              trimBefore={Math.round((shot.videoTrimStartSec ?? 0) * fps)}
              style={{ width: "100%", height: "100%" }}
            />
          </AbsoluteFill>
          <AbsoluteFill
            style={{
              background:
                "radial-gradient(circle at 50% 46%, rgba(15,23,42,0.18) 0%, rgba(5,8,15,0.82) 100%)",
              pointerEvents: "none",
            }}
          />
          {/* Uncropped 9:16 Vertical Social Broadcast Frame (x=714..1206, y=42..916 — Zero UI Overlap!) */}
          <div
            style={{
              position: "absolute",
              top: SAFE_TOP,
              left: "50%",
              transform: "translateX(-50%)",
              width: 492,
              height: 874,
              borderRadius: 18,
              overflow: "hidden",
              backgroundColor: "#060911",
              border: "2px solid rgba(255,255,255,0.22)",
              boxShadow: "0 28px 68px rgba(0,0,0,0.88)",
              zIndex: 8,
            }}
          >
            <Video
              src={staticFile(mediaPath)}
              muted
              loop
              objectFit="cover"
              trimBefore={Math.round((shot.videoTrimStartSec ?? 0) * fps)}
              style={{
                width: "100%",
                height: "100%",
                transform: `scale(${interpolate(
                  frame,
                  [0, Math.max(30, durationInFrames)],
                  [1.0, 1.04],
                  { extrapolateRight: "clamp" },
                )})`,
              }}
            />
          </div>
        </>
      ) : (
        <AbsoluteFill
          style={{
            transform: `scale(${mediaScale})`,
            transformOrigin: "50% 48%",
          }}
        >
          {isVideo ? (
            <Video
              src={staticFile(mediaPath)}
              muted
              loop
              objectFit="cover"
              trimBefore={Math.round((shot.videoTrimStartSec ?? 0) * fps)}
              style={{
                width: "100%",
                height: "100%",
                filter: "contrast(1.08) brightness(0.92)",
              }}
            />
          ) : (
            <Img
              src={staticFile(mediaPath)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: shot.mediaFit ?? "cover",
                objectPosition: shot.mediaObjectPosition ?? "50% 24%",
                filter: "contrast(1.08) brightness(0.92)",
              }}
            />
          )}
        </AbsoluteFill>
      )}

      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(5,8,15,0.58) 0%, rgba(5,8,15,0.03) 26%, rgba(5,8,15,0.06) 68%, rgba(5,8,15,0.82) 100%)",
          pointerEvents: "none",
        }}
      />

      {shot.callout && (
        <div
          style={{
            position: "absolute",
            left: `${shot.callout.cxPct}%`,
            top: `${shot.callout.cyPct}%`,
            transform: "translate(-50%, -50%)",
            pointerEvents: "none",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <div
            style={{
              width: shot.callout.radiusPx * 2,
              height: shot.callout.radiusPx * 2,
              borderRadius: "50%",
              border: "3px solid #F59E0B",
              boxShadow: "0 0 28px rgba(245,158,11,0.55)",
            }}
          />
          {shot.callout.label && (
            <div
              style={{
                marginTop: 10,
                padding: "6px 14px",
                backgroundColor: "rgba(9,13,22,0.92)",
                border: "1px solid #F59E0B",
                borderRadius: 6,
                fontFamily: FONT_MONO,
                fontSize: 13,
                lineHeight: 1,
                fontWeight: 700,
                color: "#F8FAFC",
                whiteSpace: "nowrap",
              }}
            >
              {shot.callout.label}
            </div>
          )}
        </div>
      )}

      {/* Upper-Right Source & Date Chyron (Aligned strictly to SAFE_TOP=42, SAFE_X=56) */}
      {(shot.sourceTag || shot.locationDate) && (
        <div
          style={{
            position: "absolute",
            top: SAFE_TOP,
            right: SAFE_X,
            padding: "10px 18px",
            borderRadius: 10,
            backgroundColor: "rgba(7, 10, 18, 0.85)",
            border: "1px solid rgba(255,255,255,0.16)",
            backdropFilter: "blur(10px)",
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-end",
            gap: 5,
          }}
        >
          {shot.sourceTag && (
            <span
              style={{
                fontFamily: FONT_MONO,
                fontSize: 12,
                lineHeight: 1,
                fontWeight: 800,
                letterSpacing: 1.4,
                color: "#F59E0B",
              }}
            >
              {shot.sourceTag}
            </span>
          )}
          {shot.locationDate && (
            <span
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: 13,
                lineHeight: 1,
                fontWeight: 600,
                color: "#E2E8F0",
              }}
            >
              {shot.locationDate}
            </span>
          )}
        </div>
      )}

      {/* Upper-Left Sub-Headline Aligned Strictly to SAFE_X = 56 (Yields cleanly to Chapter Card) */}
      {shot.headline && !suppressHeadline && (
        <div
          style={{
            position: "absolute",
            top: SAFE_TOP + 54,
            left: SAFE_X,
            height: 38,
            padding: "0 16px",
            display: "inline-flex",
            alignItems: "center",
            borderLeft: "4px solid #38BDF8",
            borderRadius: "0 8px 8px 0",
            backgroundColor: "rgba(7, 10, 18, 0.82)",
            backdropFilter: "blur(8px)",
            fontFamily: FONT_DISPLAY,
            fontSize: 17,
            lineHeight: 1,
            fontWeight: 800,
            color: "#F8FAFC",
            letterSpacing: 0.4,
          }}
        >
          {shot.headline}
        </div>
      )}

      {showPip && (
        <HostPipOverlay
          host={pipHost}
          speech={speech}
          corner={shot.pipCorner ?? "bottom-right"}
        />
      )}
    </AbsoluteFill>
  );
};

// ============================================================================
// 4. REAL PHOTO / REAL ARCHIVAL DOCUMENT + VERIFIED FACTS SPLIT STAGE
// ============================================================================
export const RealSplitEvidenceStage: React.FC<{
  readonly shot: RealShotSpec;
  readonly durationInFrames: number;
  readonly speech: ActiveSpeechState;
}> = ({ shot, durationInFrames, speech }) => {
  const frame = useCurrentFrame();
  const mediaPath = shot.mediaPath || "archival/fbi_dummy_head.jpg";

  const photoZoom = interpolate(
    frame,
    [0, Math.max(30, durationInFrames)],
    [1.02, 1.09],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#060911", overflow: "hidden" }}>
      <Img
        src={staticFile(mediaPath)}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          filter: "brightness(0.24) blur(28px) saturate(0.9)",
          transform: "scale(1.18)",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 72% 38%, rgba(56,189,248,0.09) 0%, rgba(5,8,15,0.8) 75%)",
        }}
      />

      {/* Split Grid Aligned Strictly to SAFE_X = 56 on Left & Right, Leaving Clean Subtitle Zone Below y=900 */}
      <div
        style={{
          position: "absolute",
          top: 108,
          left: SAFE_X,
          right: SAFE_X,
          height: 786,
          display: "flex",
          gap: 44,
          alignItems: "stretch",
        }}
      >
        {/* Left: Genuine Real Photograph / Real Document */}
        <div
          style={{
            flex: "0 0 1020px",
            borderRadius: 16,
            overflow: "hidden",
            position: "relative",
            border: "2px solid rgba(255,255,255,0.18)",
            boxShadow: "0 30px 68px rgba(0,0,0,0.8)",
            backgroundColor: "#090D16",
          }}
        >
          {shot.mediaFit === "contain" && (
            <Img
              src={staticFile(mediaPath)}
              style={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: "brightness(0.28) blur(22px)",
                transform: "scale(1.15)",
              }}
            />
          )}
          <Img
            src={staticFile(mediaPath)}
            style={{
              position: "relative",
              width: "100%",
              height: "100%",
              objectFit: shot.mediaFit ?? "cover",
              objectPosition: shot.mediaObjectPosition ?? "50% 20%",
              transform:
                shot.mediaFit === "contain"
                  ? `scale(${interpolate(
                      frame,
                      [0, Math.max(30, durationInFrames)],
                      [0.98, 1.02],
                      { extrapolateRight: "clamp" },
                    )})`
                  : `scale(${photoZoom})`,
            }}
          />
          {shot.sourceTag && (
            <div
              style={{
                position: "absolute",
                bottom: 18,
                left: 18,
                height: 30,
                padding: "0 14px",
                display: "inline-flex",
                alignItems: "center",
                borderRadius: 7,
                backgroundColor: "rgba(7,10,18,0.9)",
                border: "1px solid rgba(245,158,11,0.5)",
                fontFamily: FONT_MONO,
                fontSize: 12,
                lineHeight: 1,
                fontWeight: 700,
                color: "#F59E0B",
                letterSpacing: 1.3,
              }}
            >
              {shot.sourceTag}
            </div>
          )}
        </div>

        {/* Right: Verified Real-World Facts & Evidence Dossier (Cap-aligned to top of photo y=108) */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "flex-start",
            gap: 18,
          }}
        >
          {shot.headline && (
            <div
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: 31,
                fontWeight: 900,
                color: "#F8FAFC",
                lineHeight: 1.15,
                letterSpacing: -0.3,
                marginTop: -3,
                marginBottom: 2,
              }}
            >
              {shot.headline}
            </div>
          )}

          {(shot.facts ?? []).map((fact, idx) => {
            const accentHex =
              fact.accent === "red"
                ? "#EF4444"
                : fact.accent === "cyan"
                  ? "#38BDF8"
                  : "#F59E0B";
            return (
              <div
                key={idx}
                style={{
                  padding: "16px 22px",
                  borderRadius: 14,
                  backgroundColor: "rgba(11, 17, 30, 0.88)",
                  backdropFilter: "blur(12px)",
                  borderLeft: `4px solid ${accentHex}`,
                  borderTop: "1px solid rgba(255,255,255,0.1)",
                  borderRight: "1px solid rgba(255,255,255,0.1)",
                  borderBottom: "1px solid rgba(255,255,255,0.1)",
                  boxShadow: "0 14px 32px rgba(0,0,0,0.45)",
                }}
              >
                <div
                  style={{
                    fontFamily: FONT_MONO,
                    fontSize: 12,
                    lineHeight: 1,
                    fontWeight: 700,
                    letterSpacing: 1.4,
                    color: accentHex,
                    marginBottom: 8,
                  }}
                >
                  {fact.label}
                </div>
                <div
                  style={{
                    fontFamily: FONT_DISPLAY,
                    fontSize: 22,
                    lineHeight: 1.25,
                    fontWeight: 800,
                    color: "#F8FAFC",
                  }}
                >
                  {fact.value}
                </div>
              </div>
            );
          })}

          {(shot.notes ?? []).map((note, idx) => (
            <div
              key={idx}
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: 17,
                lineHeight: 1.5,
                color: "#CBD5E1",
                paddingLeft: 14,
                borderLeft: "2px solid rgba(148,163,184,0.4)",
              }}
            >
              {note}
            </div>
          ))}
        </div>
      </div>

      {shot.pipHost && (
        <HostPipOverlay
          host={shot.pipHost}
          speech={speech}
          corner="bottom-right"
        />
      )}
    </AbsoluteFill>
  );
};

// ============================================================================
// 5. DOCUMENTARY UPPER-LEFT HEADER & CHAPTER BUMPER (Locked to SAFE_TOP=42, SAFE_X=56)
// ============================================================================
export const BroadcastHeaderBadge: React.FC<{
  readonly categoryTag: string;
  readonly episodeTitle: string;
}> = ({ categoryTag, episodeTitle }) => (
  <div
    style={{
      position: "absolute",
      top: SAFE_TOP,
      left: SAFE_X,
      height: 40,
      display: "inline-flex",
      alignItems: "center",
      gap: 12,
      padding: "0 16px 0 10px",
      borderRadius: 10,
      backgroundColor: "rgba(7, 10, 18, 0.85)",
      backdropFilter: "blur(10px)",
      border: "1px solid rgba(255,255,255,0.16)",
      zIndex: 25,
    }}
  >
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        height: 24,
        padding: "0 9px",
        borderRadius: 5,
        backgroundColor: "#EF4444",
        fontFamily: FONT_MONO,
        fontSize: 11,
        lineHeight: 1,
        fontWeight: 800,
        letterSpacing: 1.3,
        color: "#FFFFFF",
      }}
    >
      {categoryTag}
    </span>
    <span
      style={{
        fontFamily: FONT_DISPLAY,
        fontSize: 13,
        lineHeight: 1,
        fontWeight: 700,
        color: "#F1F5F9",
        letterSpacing: 0.6,
      }}
    >
      {episodeTitle}
    </span>
  </div>
);

export const RealChapterCard: React.FC<{
  readonly chapter: RealChapterMarker;
}> = ({ chapter }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 12, 62, 78], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: SAFE_TOP + 54,
        left: SAFE_X,
        opacity,
        padding: "12px 22px",
        borderRadius: 12,
        backgroundColor: "rgba(7, 10, 18, 0.9)",
        borderLeft: "4px solid #F59E0B",
        boxShadow: "0 16px 40px rgba(0,0,0,0.68)",
        zIndex: 28,
      }}
    >
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 12,
          lineHeight: 1,
          fontWeight: 700,
          letterSpacing: 1.8,
          color: "#F59E0B",
        }}
      >
        CHAPTER {chapter.index} · {chapter.subtitle}
      </div>
      <div
        style={{
          fontFamily: FONT_DISPLAY,
          fontSize: 23,
          lineHeight: 1.2,
          fontWeight: 900,
          color: "#F8FAFC",
          marginTop: 5,
        }}
      >
        {chapter.title}
      </div>
    </div>
  );
};

// ============================================================================
// 6. DEAD-CENTER LOCKED BROADCAST SUBTITLES (Zero Horizontal Shift Across Cuts!)
//    maxWidth=1020 spans x=450..1470 -> 82px clean gap before Right PiP (x=1552..1864)
// ============================================================================
export const DualHostBroadcastCaptions: React.FC<{
  readonly speech: ActiveSpeechState;
  readonly hasRightPip?: boolean;
}> = ({ speech }) => {
  const cue = speech.activeCue;
  if (!cue) return null;

  const isCole = cue.speaker === "cole";
  const accent = isCole ? "#F59E0B" : "#38BDF8";

  return (
    <div
      style={{
        position: "absolute",
        bottom: SAFE_BOTTOM,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
        zIndex: 35,
      }}
    >
      <div
        style={{
          maxWidth: 1020,
          padding: "13px 24px",
          borderRadius: 14,
          backgroundColor: "rgba(7, 10, 18, 0.9)",
          backdropFilter: "blur(12px)",
          border: `1.5px solid ${accent}70`,
          boxShadow: "0 16px 40px rgba(0,0,0,0.82)",
          display: "inline-flex",
          alignItems: "center",
          gap: 15,
        }}
      >
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            height: 26,
            padding: "0 10px",
            borderRadius: 6,
            backgroundColor: `${accent}24`,
            border: `1px solid ${accent}`,
            fontFamily: FONT_MONO,
            fontSize: 12,
            lineHeight: 1,
            fontWeight: 800,
            letterSpacing: 1.3,
            color: accent,
            flexShrink: 0,
          }}
        >
          {isCole ? "COLE" : "MAYA"}
        </span>
        <span
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 23,
            fontWeight: 700,
            color: "#F8FAFC",
            lineHeight: 1.32,
          }}
        >
          {cue.text}
        </span>
      </div>
    </div>
  );
};
