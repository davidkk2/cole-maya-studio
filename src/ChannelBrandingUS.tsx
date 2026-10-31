import type React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { StudioHostAvatar } from "./realshow/StudioHosts";

export const ChannelAvatarUS: React.FC = () => {
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#060911" }}>
      <Img
        src={staticFile("studio/studio_set_1080p.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          filter: "brightness(0.54) blur(3px)",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 32% 38%, rgba(245,158,11,0.16) 0%, rgba(5,8,15,0) 46%), radial-gradient(circle at 68% 38%, rgba(56,189,248,0.16) 0%, rgba(5,8,15,0.72) 100%)",
        }}
      />

      {/* Centered Portrait Duo Sized for Maximum Legibility Inside Circular Crop (r=400) */}
      <div style={{ position: "absolute", left: -24, top: 108 }}>
        <StudioHostAvatar
          host="cole"
          isSpeaking={false}
          deskSide="left"
          widthPx={500}
          showMic={false}
          forcedSprite="idle"
        />
      </div>
      <div style={{ position: "absolute", right: -24, top: 108 }}>
        <StudioHostAvatar
          host="maya"
          isSpeaking={true}
          deskSide="right"
          widthPx={500}
          showMic={false}
          forcedSprite="talk1"
        />
      </div>

      {/* Bottom Solid Studio Desk Ledge + Circular-Safe Duo Nameplate (Zero Jacket Cut Seam) */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 526,
          height: 40,
          background:
            "linear-gradient(180deg, rgba(6,9,17,0) 0%, rgba(6,9,17,0.92) 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 564,
          bottom: 0,
          background: "linear-gradient(180deg, #1E1510 0%, #090D16 16%, #060911 100%)",
          borderTop: "2.5px solid rgba(245,158,11,0.5)",
          boxShadow: "0 -10px 28px rgba(0,0,0,0.88)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: 616,
          transform: "translateX(-50%)",
          height: 54,
          padding: "0 30px",
          borderRadius: 999,
          backgroundColor: "rgba(9,13,22,0.96)",
          border: "2px solid #F59E0B",
          boxShadow: "0 12px 28px rgba(0,0,0,0.85)",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          whiteSpace: "nowrap",
          fontFamily: "'Inter', 'Arial Black', sans-serif",
          fontSize: 29,
          lineHeight: 1,
          fontWeight: 900,
          letterSpacing: 2.5,
          color: "#F8FAFC",
        }}
      >
        COLE & MAYA
      </div>
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: 684,
          transform: "translateX(-50%)",
          whiteSpace: "nowrap",
          fontFamily: "'Consolas', 'Courier New', monospace",
          fontSize: 15,
          lineHeight: 1,
          fontWeight: 800,
          letterSpacing: 2.8,
          color: "#38BDF8",
        }}
      >
        INVESTIGATIONS
      </div>
    </AbsoluteFill>
  );
};

export const ChannelBannerUS: React.FC<{
  readonly channelTitle?: string;
  readonly tagline?: string;
  readonly subTagline?: string;
}> = ({
  channelTitle = "COLE & MAYA",
  tagline = "100% REAL FOOTAGE · PRIMARY RECORDS",
  subTagline = "GEOPOLITICS · GLOBAL FINANCE · DECLASSIFIED HISTORY",
}) => {
  // Official YouTube 2560x1440 All-Device Safe Zone: 1546x423 centered (x=507..2053, y=508..931)
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#060911" }}>
      <Img
        src={staticFile("studio/studio_set_1080p.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          filter: "brightness(0.46) contrast(1.12)",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(circle at 50% 50%, rgba(15,23,42,0.18) 0%, rgba(4,7,14,0.78) 100%)",
        }}
      />

      {/* Left Host Seated Physically Behind Walnut Desk (x=518..898, y=546..913) */}
      <div style={{ position: "absolute", left: 518, top: 546 }}>
        <StudioHostAvatar
          host="cole"
          isSpeaking={false}
          deskSide="left"
          widthPx={380}
          showMic={false}
          forcedSprite="idle"
        />
      </div>

      {/* Right Host Seated Physically Behind Walnut Desk (x=1662..2042, y=546..913) */}
      <div style={{ position: "absolute", right: 518, top: 546 }}>
        <StudioHostAvatar
          host="maya"
          isSpeaking={true}
          deskSide="right"
          widthPx={380}
          showMic={false}
          forcedSprite="talk1"
        />
      </div>

      {/* Walnut Studio Desk Positioned at y=883 (Overlaps Jacket Bottoms at y=883..913 — Zero Floating Cut!) */}
      <Img
        src={staticFile("studio/studio_desk_fg.png")}
        style={{
          position: "absolute",
          left: 0,
          top: -175,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 1255,
          bottom: 0,
          backgroundColor: "#06080E",
        }}
      />

      {/* Foreground Boom Microphones Mounted Above Walnut Desk */}
      <div
        style={{
          position: "absolute",
          left: 500,
          top: 734,
          width: 215,
          height: 168,
          filter: "drop-shadow(0 14px 20px rgba(0,0,0,0.8))",
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
          right: 500,
          top: 734,
          width: 215,
          height: 168,
          transform: "scaleX(-1)",
          filter: "drop-shadow(0 14px 20px rgba(0,0,0,0.8))",
          pointerEvents: "none",
        }}
      >
        <Img
          src={staticFile("studio/hosts/studio_mic.png")}
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
        />
      </div>

      {/* Center Typography Stack Centered Between Safe-Zone Top (y=508) & Walnut Desk (y=883) */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: 694,
          transform: "translate(-50%, -50%)",
          textAlign: "center",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 13,
          zIndex: 10,
        }}
      >
        <div
          style={{
            height: 30,
            padding: "0 16px",
            borderRadius: 6,
            backgroundColor: "rgba(239,68,68,0.92)",
            display: "inline-flex",
            alignItems: "center",
            fontFamily: "'Consolas', 'Courier New', monospace",
            fontSize: 15,
            lineHeight: 1,
            fontWeight: 800,
            letterSpacing: 2.4,
            color: "#FFFFFF",
          }}
        >
          INVESTIGATIVE DOCUMENTARY SERIES
        </div>
        <div
          style={{
            fontFamily: "Impact, 'Arial Black', sans-serif",
            fontSize: 88,
            lineHeight: 0.96,
            fontWeight: 900,
            letterSpacing: 3.5,
            color: "#F8FAFC",
            textShadow: "0 10px 32px rgba(0,0,0,0.95)",
          }}
        >
          {channelTitle}
        </div>
        <div
          style={{
            height: 44,
            padding: "0 26px",
            borderRadius: 999,
            backgroundColor: "#F59E0B",
            boxShadow: "0 10px 28px rgba(0,0,0,0.75)",
            display: "inline-flex",
            alignItems: "center",
            fontFamily: "'Inter', 'Arial Black', sans-serif",
            fontSize: 20,
            lineHeight: 1,
            fontWeight: 900,
            letterSpacing: 1.8,
            color: "#090D16",
          }}
        >
          {tagline}
        </div>
        <div
          style={{
            fontFamily: "'Consolas', 'Courier New', monospace",
            fontSize: 15,
            lineHeight: 1,
            fontWeight: 800,
            letterSpacing: 2.4,
            color: "#38BDF8",
            textShadow: "0 4px 16px rgba(0,0,0,0.95)",
            whiteSpace: "nowrap",
            marginTop: 2,
          }}
        >
          {subTagline}
        </div>
      </div>
    </AbsoluteFill>
  );
};
