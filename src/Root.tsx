import type React from "react";
import { Composition, Folder, Still } from "remotion";
import { ChannelAvatarUS, ChannelBannerUS } from "./ChannelBrandingUS";
import {
  DualHostRealEpisode,
  DualHostThumbnailUS,
  STUDIO_TEMPLATE_MANIFEST,
} from "./realshow/DualHostRealEpisode";
import { DualHostShortsUS } from "./realshow/DualHostShortsUS";
import autoMainManifestJson from "./realshow/autoMainManifest.json";
import autoMainThumbJson from "./realshow/autoMainThumbProps.json";
import autoShortManifestJson from "./realshow/autoShortManifest.json";
import ep01ManifestJson from "./realshow/ep01LagardeManifest.json";
import type { RealEpisodeManifest } from "./realshow/types";

const EP01_LAGARDE_MANIFEST = ep01ManifestJson as unknown as RealEpisodeManifest;
const AUTO_MAIN_MANIFEST = autoMainManifestJson as unknown as RealEpisodeManifest;
const AUTO_SHORT_MANIFEST = autoShortManifestJson as unknown as RealEpisodeManifest;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="AutonomousCloud">
        <Composition
          id="Auto-MainEpisode"
          component={DualHostRealEpisode}
          durationInFrames={Math.max(
            30,
            Math.round(AUTO_MAIN_MANIFEST.totalDurationSec * 30),
          )}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{
            manifest: AUTO_MAIN_MANIFEST,
          }}
        />
        <Still
          id="Auto-MainThumbnail"
          component={DualHostThumbnailUS}
          width={1280}
          height={720}
          defaultProps={{
            bgPhotoPath: autoMainThumbJson.bgPhotoPath,
            topBadge: autoMainThumbJson.topBadge,
            line1: autoMainThumbJson.line1,
            line2: autoMainThumbJson.line2,
            line3: autoMainThumbJson.line3,
          }}
        />
        <Composition
          id="Auto-ShortEpisode"
          component={DualHostShortsUS}
          durationInFrames={Math.max(
            30,
            Math.round(AUTO_SHORT_MANIFEST.totalDurationSec * 30),
          )}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={{
            manifest: AUTO_SHORT_MANIFEST,
          }}
        />
      </Folder>

      <Folder name="Episodes">
        <Composition
          id="Ep01-Lagarde-EarlyExit"
          component={DualHostRealEpisode}
          durationInFrames={Math.round(
            EP01_LAGARDE_MANIFEST.totalDurationSec * 30,
          )}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{
            manifest: EP01_LAGARDE_MANIFEST,
          }}
        />
        <Still
          id="Ep01-Thumbnail-Lagarde"
          component={DualHostThumbnailUS}
          width={1280}
          height={720}
          defaultProps={{
            bgPhotoPath: "episodes/ep01_lagarde/ep01_thumb_bg.jpg",
            topBadge: "ECB SHOCK EXIT",
            line1: "WHY",
            line2: "QUIT",
            line3: "NOW?",
          }}
        />
      </Folder>

      <Folder name="Templates">
        <Composition
          id="DualHost-RealEpisode-Template"
          component={DualHostRealEpisode}
          durationInFrames={Math.round(
            STUDIO_TEMPLATE_MANIFEST.totalDurationSec * 30,
          )}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{
            manifest: STUDIO_TEMPLATE_MANIFEST,
          }}
        />

        <Still
          id="DualHost-Thumbnail-US"
          component={DualHostThumbnailUS}
          width={1280}
          height={720}
        />
      </Folder>

      <Folder name="Branding">
        <Still
          id="ChannelAvatar-US"
          component={ChannelAvatarUS}
          width={800}
          height={800}
        />
        <Still
          id="ChannelBanner-US"
          component={ChannelBannerUS}
          width={2560}
          height={1440}
        />
      </Folder>
    </>
  );
};
