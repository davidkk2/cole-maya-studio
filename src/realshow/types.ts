export type HostId = "cole" | "maya";

export type HostExpression =
  | "neutral"
  | "serious"
  | "curious"
  | "skeptical"
  | "shocked"
  | "emphatic";

export type ShotLayoutMode =
  | "studio_dual"
  | "studio_solo_cole"
  | "studio_solo_maya"
  | "real_video_full"
  | "real_photo_full"
  | "real_video_pip"
  | "real_photo_pip"
  | "real_split_evidence";

export interface DialogueCue {
  readonly id: string;
  readonly speaker: HostId;
  readonly startSec: number;
  readonly endSec: number;
  readonly text: string;
  readonly expression?: HostExpression;
}

export interface EvidenceFactItem {
  readonly label: string;
  readonly value: string;
  readonly accent?: "amber" | "cyan" | "red";
}

export interface RealShotSpec {
  readonly id: string;
  readonly startSec: number;
  readonly endSec: number;
  readonly layout: ShotLayoutMode;
  /** Path inside public/ (e.g. "archival/video/clip.mp4" or "archival/photo.jpg") */
  readonly mediaPath?: string;
  /** Optional secondary real photo for studio monitor or split comparison */
  readonly monitorMediaPath?: string;
  /** Start offset in seconds when trimming a real video clip */
  readonly videoTrimStartSec?: number;
  /** Optional base zoom multiplier (e.g. 1.35 to crop baked-in 4:3 pillarbox bars on vintage reels) */
  readonly cropScale?: number;
  /** Render a 9:16 vertical social media video uncropped inside a centered broadcast frame */
  readonly verticalSocialVideo?: boolean;
  /** Optional fit mode for archival documents / multi-panel screenshots ('cover' default, 'contain' for full document) */
  readonly mediaFit?: "cover" | "contain";
  /** Optional CSS object-position for portrait photos (default '50% 22%' to protect heads/eyes) */
  readonly mediaObjectPosition?: string;
  /** Source / location / date documentary chyron */
  readonly sourceTag?: string;
  readonly locationDate?: string;
  readonly headline?: string;
  /** Which host appears in PiP corner for *_pip layouts */
  readonly pipHost?: HostId;
  readonly pipCorner?: "bottom-right" | "bottom-left";
  /** Optional callout ring on real photograph (percentages 0..100) */
  readonly callout?: {
    readonly cxPct: number;
    readonly cyPct: number;
    readonly radiusPx: number;
    readonly label?: string;
  };
  /** Verified real-world evidence bullets for real_split_evidence layout */
  readonly facts?: readonly EvidenceFactItem[];
  readonly notes?: readonly string[];
}

export interface RealChapterMarker {
  readonly index: string;
  readonly title: string;
  readonly subtitle: string;
  readonly startSec: number;
}

export interface RealEpisodeManifest {
  readonly episodeTitle: string;
  readonly categoryTag: string;
  readonly masterAudioPath?: string;
  readonly totalDurationSec: number;
  readonly cues: readonly DialogueCue[];
  readonly shots: readonly RealShotSpec[];
  readonly chapters?: readonly RealChapterMarker[];
}
