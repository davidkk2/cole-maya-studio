#!/usr/bin/env node
/**
 * Cole & Maya — Zero-Touch Cloud Autonomous Producer (Main 16:9 + 3 Daily Independent 9:16 Shorts)
 * -----------------------------------------------------------------------------------------------
 * Runs identically in GitHub Actions (Ubuntu Cloud, PC Turned Off) and on Windows/macOS:
 *   node scripts/auto_cloud_producer.mjs --slot short1 --upload   (Schedules 09:00 America/New_York)
 *   node scripts/auto_cloud_producer.mjs --slot short2 --upload   (Schedules 13:00 America/New_York)
 *   node scripts/auto_cloud_producer.mjs --slot main   --upload   (Schedules 17:00 America/New_York Prime-Time)
 *   node scripts/auto_cloud_producer.mjs --slot short3 --upload   (Schedules 21:00 America/New_York)
 *   node scripts/auto_cloud_producer.mjs --slot short1            (Local render-only dry run, no upload)
 */

import dns from "node:dns";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import {
  notifyProductionFailed,
  notifyProductionStarted,
  notifyProductionSucceeded,
} from "./cloud_notifier.mjs";

dns.setDefaultResultOrder("ipv4first");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname, "..");

const GEMINI_MODELS = [
  "gemini-3.8-flash",
  "gemini-flash-lite-latest",
  "gemini-3.5-flash-lite",
  "gemini-3.1-flash-lite",
  "gemini-flash-latest",
  "gemini-3.7-flash",
];

const SLOT_CONFIG = {
  short1: {
    mode: "short",
    nyHour: 9,
    lens: "Global Markets, Central Banks, Sovereign Debt, Currency Moves, or Major Financial Filings",
  },
  short2: {
    mode: "short",
    nyHour: 13,
    lens: "Geopolitics, Maritime Chokepoints, Energy Pipelines, Diplomatic Treaties, or Sanctions",
  },
  main: {
    mode: "main",
    nyHour: 17,
    lens: "High-Stakes Geopolitical, Central Bank, or Institutional Power Play paired with a Declassified Historical Intelligence Parallel",
  },
  short3: {
    mode: "short",
    nyHour: 21,
    lens: "Defense Technology, Semiconductor/AI Infrastructure Power Battles, Antitrust Filings, or Declassified Archives",
  },
};

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const tok = argv[i];
    if (tok.startsWith("--")) {
      const k = tok.slice(2);
      const next = argv[i + 1];
      if (!next || next.startsWith("--")) {
        args[k] = true;
      } else {
        args[k] = next;
        i++;
      }
    } else {
      args._.push(tok);
    }
  }
  return args;
}

function getPythonBin() {
  if (process.platform === "win32") return "python";
  const check = spawnSync("python3", ["--version"], { encoding: "utf8" });
  return check.status === 0 ? "python3" : "python";
}

function runCmd(bin, cmdArgs, label) {
  console.log(`\n▶️  [${label}] ${bin} ${cmdArgs.join(" ")}`);
  const res = spawnSync(bin, cmdArgs, {
    cwd: ROOT_DIR,
    stdio: "inherit",
    shell: process.platform === "win32" && bin === "npx",
  });
  if (res.status !== 0) {
    throw new Error(`${label} failed with exit code ${res.status}`);
  }
}

function loadGeminiKey() {
  if (process.env.GEMINI_API_KEY && process.env.GEMINI_API_KEY.trim()) {
    return process.env.GEMINI_API_KEY.trim();
  }
  const keyFile = path.join(ROOT_DIR, "secrets", "gemini_api_key.txt");
  if (fs.existsSync(keyFile)) {
    return fs.readFileSync(keyFile, "utf8").trim();
  }
  throw new Error(
    "GEMINI_API_KEY bulunamadi! GitHub Secrets icinde GEMINI_API_KEY veya yerel secrets/gemini_api_key.txt tanimlayin.",
  );
}

async function getYouTubeAccessTokenOptional() {
  try {
    let clientId = process.env.YT_CLIENT_ID?.trim();
    let clientSecret = process.env.YT_CLIENT_SECRET?.trim();
    let refreshToken = process.env.YT_REFRESH_TOKEN?.trim();

    const secretPath = path.join(ROOT_DIR, "secrets", "client_secret.json");
    const tokenPath = path.join(ROOT_DIR, "secrets", "youtube_token.json");

    if ((!clientId || !clientSecret) && fs.existsSync(secretPath)) {
      const raw = JSON.parse(fs.readFileSync(secretPath, "utf8"));
      const cfg = raw.installed || raw.web;
      clientId = cfg?.client_id;
      clientSecret = cfg?.client_secret;
    }
    if (!refreshToken && fs.existsSync(tokenPath)) {
      const tok = JSON.parse(fs.readFileSync(tokenPath, "utf8"));
      refreshToken = tok?.refresh_token;
    }
    if (!clientId || !clientSecret || !refreshToken) return null;

    const r = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: clientId,
        client_secret: clientSecret,
        refresh_token: refreshToken,
        grant_type: "refresh_token",
      }),
    });
    if (!r.ok) return null;
    const j = await r.json();
    return j.access_token || null;
  } catch {
    return null;
  }
}

function getNextNewYorkHourISO(targetHour = 17) {
  const now = new Date();
  for (let addHours = 1; addHours <= 36; addHours++) {
    const candidate = new Date(now.getTime() + addHours * 3600 * 1000);
    candidate.setUTCMinutes(0, 0, 0);
    if (candidate.getTime() - now.getTime() < 15 * 60 * 1000) {
      continue;
    }
    const nyHour = Number(
      new Intl.DateTimeFormat("en-US", {
        timeZone: "America/New_York",
        hour: "numeric",
        hourCycle: "h23",
      }).format(candidate),
    );
    if (nyHour === targetHour) {
      return candidate.toISOString();
    }
  }
  return new Date(now.getTime() + 6 * 3600 * 1000).toISOString();
}

async function fetchExistingChannelState() {
  const token = await getYouTubeAccessTokenOptional();
  if (!token) return { titles: [], scheduledVideos: [] };
  try {
    const resp = await fetch(
      "https://www.googleapis.com/youtube/v3/search?part=snippet&forMine=true&type=video&maxResults=50",
      { headers: { Authorization: `Bearer ${token}` } },
    );
    if (!resp.ok) return { titles: [], scheduledVideos: [] };
    const data = await resp.json();
    const items = data.items || [];
    const titles = items
      .map((it) => String(it.snippet?.title || "").trim())
      .filter(Boolean);
    const ids = items
      .map((it) => it.id?.videoId)
      .filter(Boolean)
      .slice(0, 50);

    let scheduledVideos = [];
    if (ids.length > 0) {
      const vResp = await fetch(
        `https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id=${ids.join(",")}`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      if (vResp.ok) {
        const vData = await vResp.json();
        scheduledVideos = (vData.items || [])
          .filter((v) => v.status?.publishAt)
          .map((v) => ({
            id: v.id,
            title: v.snippet?.title || "",
            publishAt: v.status.publishAt,
          }));
      }
    }
    return { titles, scheduledVideos };
  } catch {
    return { titles: [], scheduledVideos: [] };
  }
}

function decodeXmlEntities(str) {
  return str
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
}

async function fetchRssTitles(url, sourceLabel, maxItems = 16) {
  try {
    const resp = await fetch(url, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ColeMayaInvestigativeBot/1.0",
      },
    });
    if (!resp.ok) return [];
    const xml = await resp.text();
    const items = [];
    const itemRegex = /<item>([\s\S]*?)<\/item>/gi;
    let match;
    while ((match = itemRegex.exec(xml)) !== null && items.length < maxItems) {
      const block = match[1];
      const titleMatch = block.match(/<title>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/title>/i);
      const pubMatch = block.match(/<pubDate>([\s\S]*?)<\/pubDate>/i);
      if (titleMatch) {
        const cleanTitle = decodeXmlEntities(titleMatch[1].trim()).replace(/\s+/g, " ");
        if (cleanTitle.length > 8) {
          items.push({
            source: sourceLabel,
            title: cleanTitle,
            pubDate: pubMatch ? pubMatch[1].trim() : "",
          });
        }
      }
    }
    return items;
  } catch {
    return [];
  }
}

async function harvestUSTrends() {
  console.log("📡 ABD canli gundem ve trend akislari taraniyor...");
  const feeds = [
    ["US_TRENDS", "https://trends.google.com/trending/rss?geo=US", 15],
    [
      "US_BUSINESS",
      "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
      18,
    ],
    [
      "WORLD_GEOPOLITICS",
      "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en",
      18,
    ],
    [
      "US_NATION_POLICY",
      "https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=US&ceid=US:en",
      15,
    ],
    [
      "TECH_INFRASTRUCTURE",
      "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
      14,
    ],
  ];

  const all = [];
  const seen = new Set();
  for (const [label, url, limit] of feeds) {
    const items = await fetchRssTitles(url, label, limit);
    for (const it of items) {
      const norm = it.title.toLowerCase().slice(0, 48);
      if (!seen.has(norm)) {
        seen.add(norm);
        all.push(it);
      }
    }
  }
  console.log(`  ✅ ${all.length} tekil canli ABD haber/trend basligi toplandi.`);
  return all;
}

async function callGeminiJSON(apiKey, promptText, temperature = 0.4) {
  let lastErr = null;
  for (const model of GEMINI_MODELS) {
    for (let attempt = 1; attempt <= 2; attempt++) {
      try {
        const resp = await fetch(
          `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-goog-api-key": apiKey,
            },
            body: JSON.stringify({
              contents: [{ parts: [{ text: promptText }] }],
              generationConfig: {
                temperature,
                responseMimeType: "application/json",
              },
            }),
          },
        );
        const bodyText = await resp.text();
        if (resp.status === 503 || resp.status === 429) {
          lastErr = new Error(`${model} HTTP ${resp.status}: ${bodyText.slice(0, 180)}`);
          await new Promise((r) => setTimeout(r, 2500 * attempt));
          continue;
        }
        if (resp.status === 404) {
          lastErr = new Error(`${model} HTTP 404`);
          break;
        }
        if (!resp.ok) {
          throw new Error(`${model} HTTP ${resp.status}: ${bodyText.slice(0, 260)}`);
        }
        const outer = JSON.parse(bodyText);
        const rawText =
          outer.candidates?.[0]?.content?.parts
            ?.map((p) => p.text || "")
            .join("")
            .trim() || "";
        const cleaned = rawText
          .replace(/^```json\s*/i, "")
          .replace(/^```\s*/i, "")
          .replace(/\s*```$/i, "")
          .trim();
        const parsed = JSON.parse(cleaned);
        console.log(`  🤖 Gemini yaniti alindi (${model})`);
        return Array.isArray(parsed) ? parsed[0] : parsed;
      } catch (err) {
        lastErr = err;
        await new Promise((r) => setTimeout(r, 1500));
      }
    }
  }
  throw new Error(`Tum Gemini modelleri basarisiz oldu: ${lastErr?.message}`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const slotKey = String(args.slot || "short1").toLowerCase();
  const slot = SLOT_CONFIG[slotKey];
  if (!slot) {
    throw new Error(
      `Gecersiz --slot '${slotKey}'. Gecerli degerler: short1 | short2 | main | short3`,
    );
  }

  const isShort = slot.mode === "short";
  const shouldUpload = Boolean(args.upload);
  const workDir = path.join(ROOT_DIR, ".tmp_auto_work");
  fs.mkdirSync(workDir, { recursive: true });
  const failFlagPath = path.join(workDir, "notified_failure.flag");
  if (fs.existsSync(failFlagPath)) fs.unlinkSync(failFlagPath);

  let activeIssueNumber = null;
  let activeTopicPlan = null;
  const targetPublishISO = getNextNewYorkHourISO(slot.nyHour);

  try {
  const geminiKey = loadGeminiKey();
  const pythonBin = getPythonBin();

  const todayISO = new Date().toISOString().slice(0, 10);
  console.log(`\n=============================================================`);
  console.log(`🚀 COLE & MAYA OTONOM BULUT URETICI BASLATILDI`);
  console.log(`📅 Tarih : ${todayISO} | Slot: ${slotKey.toUpperCase()} (${slot.mode.toUpperCase()})`);
  console.log(`⏰ Hedef : ${String(slot.nyHour).padStart(2, "0")}:00 America/New_York`);
  console.log(`=============================================================\n`);

  const { titles: existingTitles, scheduledVideos } = await fetchExistingChannelState();
  console.log(`📚 Kanal arsiv kontrolu: ${existingTitles.length} mevcut/planli video basligi tarandi.`);

  if (shouldUpload && !args["test-unlisted"] && !args.force) {
    const targetMs = new Date(targetPublishISO).getTime();
    const collision = scheduledVideos.find(
      (sv) => Math.abs(new Date(sv.publishAt).getTime() - targetMs) <= 45 * 60 * 1000,
    );
    if (collision) {
      console.log(
        `✅ Hedef saat dilimi (${targetPublishISO}) icin kanalda zaten zamanlanmis video var: "${collision.title}" (${collision.id}). Cift yuklemeyi onlemek icin bu vardiya atlandi.`,
      );
      return;
    }
  }

  const liveTrends = await harvestUSTrends();
  const trendLines = liveTrends
    .slice(0, 60)
    .map((t, idx) => `${idx + 1}. [${t.source}] ${t.title}`)
    .join("\n");

  const planPrompt = `You are the Executive Producer of "Cole & Maya", a high-CPM US YouTube investigative journalism channel covering geopolitics, central banks, global finance, institutional power moves, and declassified intelligence history.

TODAY'S DATE: ${todayISO}
PRODUCTION SLOT: ${slotKey.toUpperCase()} (${isShort ? "Vertical YouTube Short, 45-54 seconds, 1080x1920" : "Main Horizontal Investigative Documentary, 4.5-5.5 minutes, 1920x1080"})
EDITORIAL LENS FOR THIS SLOT: ${slot.lens}

EXISTING VIDEOS ALREADY ON OUR CHANNEL (STRICT RULE: DO NOT REPEAT OR OVERLAP WITH ANY TOPIC, PERSON, OR EVENT BELOW):
${existingTitles.length ? existingTitles.map((t) => `- ${t}`).join("\n") : "- (none)"}

LIVE US TRENDING HEADLINES TODAY:
${trendLines}

STRICT YOUTUBE MONETIZATION & EDITORIAL RULES:
1. Pick ONE compelling story from LIVE US TRENDING HEADLINES TODAY matching this slot's editorial lens, with ZERO overlap with EXISTING VIDEOS ALREADY ON OUR CHANNEL.
2. NEVER pick celebrity gossip, sports scores, violent tragedies/shootings, adult topics, or demonetized conspiracy buzzwords (never use words like "QAnon" or graphic violence). Frame everything as smart, primary-source institutional/financial/geopolitical analysis.
3. Because our visual engine uses 100% REAL archival & public-domain/CC photographs from Wikipedia and Wikimedia Commons, provide exact English Wikipedia article titles (e.g. "Federal_Reserve", "Jerome_Powell", "Strait_of_Hormuz", "Taiwan_Semiconductor_Manufacturing_Company", "Bretton_Woods_system") and specific Wikimedia Commons photo/video search queries for the real people, buildings, maps/locations, summits, and historical parallels involved.

Return a single JSON object with this exact schema:
{
  "selectedHeadline": "exact headline chosen from the live list",
  "turkishTitle": "Clear, concise Turkish headline summarizing the selected story for the channel owner's email notification (<= 75 chars)",
  "turkishSummary": "3 clear Turkish sentences explaining what the video covers, the hidden financial/geopolitical mechanism, and why it matters",
  "angleSummary": "2-3 sentences explaining the hidden institutional, treaty, financial, or historical angle Cole & Maya will uncover",
  "historicalParallel": "1-2 sentences naming a real documented historical/declassified parallel (especially rich if mode is main)",
  "wikipediaArticles": ["Exact_English_Wikipedia_Title_1", "Exact_English_Wikipedia_Title_2", "Exact_English_Wikipedia_Title_3", "Exact_English_Wikipedia_Title_4", "Exact_English_Wikipedia_Title_5", "Exact_English_Wikipedia_Title_6"],
  "photoQueries": ["specific person or building query 1", "query 2", "query 3", "query 4", "query 5", "query 6", "query 7", "query 8"],
  "videoQueries": ["city skyline or institution video query 1", "historical newsreel or aerial query 2"]
}`;

  console.log("🧠 Adim 1/5: Gemini ile benzersiz trend konu ve birincil arsiv plani seciliyor...");
  const topicPlan = await callGeminiJSON(geminiKey, planPrompt, 0.45);
  activeTopicPlan = topicPlan;
  console.log(`  🎯 Secilen Konu: ${topicPlan.selectedHeadline}`);
  console.log(`  📐 Aci: ${topicPlan.angleSummary}`);

  activeIssueNumber = await notifyProductionStarted({
    slotKey,
    isShort,
    targetPublishISO,
    topicPlan,
  });

  const planPath = path.join(workDir, `plan_${slotKey}.json`);
  const catalogPath = path.join(workDir, `catalog_${slotKey}.json`);
  const scriptPath = path.join(workDir, `script_${slotKey}.json`);
  const autoPublicDir = path.join(ROOT_DIR, "public", "episodes", `auto_${slotKey}`);

  fs.writeFileSync(planPath, JSON.stringify(topicPlan, null, 2), "utf8");

  console.log("🖼️  Adim 2/5: Gercek fotograflar, videolar ve Wikipedia birincil verileri indiriliyor...");
  runCmd(
    pythonBin,
    [
      "scripts/build_auto_assets.py",
      "acquire",
      "--plan",
      planPath,
      "--out-dir",
      autoPublicDir,
      "--catalog",
      catalogPath,
      "--mode",
      slot.mode,
    ],
    "RealMediaAcquire",
  );

  const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));
  const assetListText = catalog.assets
    .map(
      (a) =>
        `- ${a.id} (${a.kind}, ${a.width}x${a.height}): title="${a.title}" | sourceTag="${a.suggestedSourceTag}" | desc="${a.description}"`,
    )
    .join("\n");
  const wikiFactsText = (catalog.wikipediaFacts || [])
    .map((w) => `• ${w.title} (${w.description}): ${w.extract}`)
    .join("\n");

  const cueRequirement = isShort
    ? `Write 8 to 9 tight, fast-paced, alternating cues between "cole" and "maya" totaling ~115 to 132 spoken words total (strictly 42 to 53 seconds total duration so it stays under YouTube Shorts' 60s limit!). First cue MUST be an instant 0.5-second curiosity hook; final cue MUST deliver a sharp institutional takeaway.`
    : `Write 28 to 32 crisp, investigative alternating cues between "cole" and "maya" totaling ~680 to 780 spoken words (~4.5 to 5.4 minutes). Structure into 4 clear acts: Act 1 (The Breaking Move & Viral Misconception), Act 2 (The Primary Filing / Numbers Nobody Read), Act 3 (The Institutional Chess / Geopolitical Stakes), Act 4 (The Declassified / Historical Parallel & Final Verdict).`;

  const shotRequirement = isShort
    ? `Create 6 to 8 visual shots in "shots", each referencing a verified "assetId" from AVAILABLE REAL ASSETS BELOW (vary the assets so the visual changes every ~6 seconds!), with a crisp "headline" (<=52 chars), "locationDate" (<=32 chars), and 1 verified "facts" item ({ "label": "...", "value": "...", "accent": "amber"|"cyan"|"red" }).`
    : `Create 16 to 20 visual shots in "shots" spanning the episode. Mix layouts intelligently: use "studio_dual" for the cold open, thesis pivot, and final signoff (3-4 times total), "real_split_evidence" (4-5 times with 2 verified "facts" bullets and 1 "notes" sentence), and "real_photo_pip" / "real_video_pip" for the rest. Every shot MUST reference a real "assetId" from AVAILABLE REAL ASSETS BELOW.`;

  const scriptPrompt = `You are the Head Investigative Scriptwriter for "Cole & Maya" (US English YouTube channel).

SELECTED BREAKING STORY: ${topicPlan.selectedHeadline}
INVESTIGATIVE ANGLE: ${topicPlan.angleSummary}
HISTORICAL / INSTITUTIONAL PARALLEL: ${topicPlan.historicalParallel}
TODAY'S DATE: ${todayISO}

VERIFIED WIKIPEDIA PRIMARY FACTS (USE ONLY ACCURATE DATES, NAMES & INSTITUTIONS):
${wikiFactsText || "Use verified public institutional facts."}

AVAILABLE REAL ASSETS DOWNLOADED ON DISK (ONLY USE THESE EXACT assetId VALUES):
${assetListText}

DIALOGUE & PACING RULES:
- ${cueRequirement}
- Alternate naturally between "cole" (analytical lead investigator) and "maya" (incisive financial/intelligence co-host).
- Write numbers/dates cleanly for neural TTS speech, avoid markdown asterisks inside spoken "text", and NEVER use advertiser-unfriendly conspiracy slurs.
- ${shotRequirement}

YOUTUBE METADATA RULES:
- If mode is "short": YouTube "youtubeTitle" MUST be <= 82 characters and end with "#Shorts" (high-curiosity US English hook, zero clickbait lies).
- If mode is "main": YouTube "youtubeTitle" MUST be 55 to 92 characters (high-CPM US investigative documentary style like Johnny Harris / ColdFusion / WSJ). Also provide "thumbnail" with "topBadge" (2-3 words), and 3 giant impact lines "line1", "line2", "line3" (EACH line MUST be 1 word of MAX 8 LETTERS so it never overflows!).

Return a single JSON object matching this exact schema:
{
  "episodeTitle": "SHORT UPPERCASE ON-SCREEN HEADER (MAX 54 CHARS)",
  "categoryTag": "2-WORD TAG E.G. CENTRAL BANKS or GEOPOLITICS",
  "youtubeTitle": "Full US YouTube Title${isShort ? " #Shorts" : ""}",
  "youtubeDescription": "3 rich paragraphs + primary sources summary (chapters will be auto-injected for main)",
  "youtubeTags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"],
  "thumbnailAssetId": "photo_01",
  "thumbnail": {
    "topBadge": "SHOCK FILING",
    "line1": "HIDDEN",
    "line2": "RATE",
    "line3": "TRAP"
  },
  "cues": [
    { "speaker": "cole", "expression": "serious", "text": "..." },
    { "speaker": "maya", "expression": "curious", "text": "..." }
  ],
  "shots": [
    {
      "layout": "${isShort ? "real_photo_full" : "studio_dual"}",
      "assetId": "photo_01",
      "sourceTag": "OFFICIAL ARCHIVE",
      "locationDate": "WASHINGTON, D.C.",
      "headline": "UPPERCASE SHOT CHYRON",
      "facts": [
        { "label": "PRIMARY RECORD", "value": "Concise verified fact under 64 chars", "accent": "amber" }
      ],
      "notes": ["One concise analytical sentence for split-screen evidence."]
    }
  ],
  "chapters": [
    { "cueIndex": 1, "title": "The Headline vs. The Filing", "subtitle": "PRIMARY RECORD" },
    { "cueIndex": 8, "title": "Follow The Institutional Money", "subtitle": "MARKET MECHANICS" },
    { "cueIndex": 16, "title": "The Strategic Power Window", "subtitle": "GEOPOLITICAL STAKES" },
    { "cueIndex": 23, "title": "The Historical Playbook", "subtitle": "ARCHIVAL PARALLEL" }
  ]
}`;

  console.log("✍️  Adim 3/5: Cole & Maya senaryosu, kanit kartlari ve sahne kurgusu yaziliyor...");
  const scriptJson = await callGeminiJSON(geminiKey, scriptPrompt, 0.4);
  fs.writeFileSync(scriptPath, JSON.stringify(scriptJson, null, 2), "utf8");

  console.log("🎙️  Adim 4/5: Cole & Maya seslendirmesi (-16 LUFS) ve kare-hassas manifesto uretiliyor...");
  runCmd(
    pythonBin,
    [
      "scripts/build_auto_assets.py",
      "finalize",
      "--script",
      scriptPath,
      "--catalog",
      catalogPath,
      "--out-dir",
      autoPublicDir,
      "--mode",
      slot.mode,
    ],
    "AudioAndManifestFinalize",
  );

  // Build final YouTube upload metadata JSON (injecting exact chapter timestamps for Main)
  const manifestFile = path.join(
    ROOT_DIR,
    "src",
    "realshow",
    isShort ? "autoShortManifest.json" : "autoMainManifest.json",
  );
  const finalManifest = JSON.parse(fs.readFileSync(manifestFile, "utf8"));

  const outVideoRel = isShort
    ? `out/Auto-${slotKey}-${todayISO}.mp4`
    : `out/Auto-Main-${todayISO}.mp4`;
  const outThumbRel = `out/Auto-MainThumb-${todayISO}.png`;
  const outShortCoverRel = `out/Auto-ShortCover-${slotKey}-${todayISO}.jpg`;

  console.log("🎬 Adim 5/5: Remotion Full HD / Shorts MP4 render aliniyor...");
  const maxCpus = Math.max(1, os.cpus().length);
  const linuxRenderFlags =
    process.platform === "linux"
      ? [`--concurrency=${maxCpus}`, "--gl=swangle"]
      : [];
  const linuxStillFlags = process.platform === "linux" ? ["--gl=swangle"] : [];
  if (isShort) {
    runCmd(
      "npx",
      [
        "remotion",
        "still",
        "Auto-ShortEpisode",
        outShortCoverRel,
        "--frame=45",
        "--image-format=jpeg",
        "--quality=88",
        ...linuxStillFlags,
      ],
      "RenderShortEmailCover",
    );
    runCmd(
      "npx",
      [
        "remotion",
        "render",
        "Auto-ShortEpisode",
        outVideoRel,
        "--codec=h264",
        "--crf=20",
        ...linuxRenderFlags,
      ],
      "RenderShortMP4",
    );
  } else {
    runCmd(
      "npx",
      ["remotion", "still", "Auto-MainThumbnail", outThumbRel, ...linuxStillFlags],
      "RenderMainThumbnail",
    );
    runCmd(
      "npx",
      [
        "remotion",
        "render",
        "Auto-MainEpisode",
        outVideoRel,
        "--codec=h264",
        "--crf=20",
        ...linuxRenderFlags,
      ],
      "RenderMainMP4",
    );
  }

  const fmtTime = (sec) => {
    const s = Math.max(0, Math.floor(sec));
    const mm = String(Math.floor(s / 60)).padStart(2, "0");
    const ss = String(s % 60).padStart(2, "0");
    return `${mm}:${ss}`;
  };

  let finalDesc = String(scriptJson.youtubeDescription || "").trim();
  if (!isShort && Array.isArray(finalManifest.chapters) && finalManifest.chapters.length > 0) {
    const chLines = [
      "00:00 Cold Open & Primary Record",
      ...finalManifest.chapters.map((c) => `${fmtTime(c.startSec)} ${c.title}`),
    ];
    finalDesc += `\n\nCHAPTERS\n${chLines.join("\n")}`;
  }
  finalDesc += `\n\nABOUT COLE & MAYA\nPrimary-source investigations into global power, central banks, geopolitics, and declassified intelligence history. Studio commentary by Cole & Maya — 100% real footage, archival photography, and primary documents on screen.\n\n${
    isShort
      ? "#Shorts #geopolitics #finance #history #documentary"
      : "#geopolitics #finance #centralbanks #documentary #history"
  }`;

  let ytTitle = String(scriptJson.youtubeTitle || finalManifest.episodeTitle).trim();
  if (isShort && !/#shorts/i.test(ytTitle)) {
    ytTitle = `${ytTitle.slice(0, 88).trim()} #Shorts`;
  }
  ytTitle = ytTitle.slice(0, 99);

  const baseTags = Array.isArray(scriptJson.youtubeTags) ? scriptJson.youtubeTags : [];
  const mergedTags = [
    ...new Set([
      ...baseTags.map((t) => String(t).trim()).filter(Boolean),
      "Cole and Maya",
      "investigative documentary",
      "geopolitics",
      "global finance",
      ...(isShort ? ["Shorts", "YouTube Shorts"] : ["declassified history"]),
    ]),
  ].slice(0, 16);

  const uploadMeta = {
    compositionId: isShort ? "Auto-ShortEpisode" : "Auto-MainEpisode",
    thumbnailCompositionId: "Auto-MainThumbnail",
    videoFile: outVideoRel,
    thumbnailFile: outThumbRel,
    isShort,
    title: ytTitle,
    description: finalDesc,
    tags: mergedTags,
    categoryId: "25",
    defaultLanguage: "en-US",
    defaultAudioLanguage: "en-US",
    locationDescription: "United States",
    madeForKids: false,
    privacyStatus: "private",
  };

  const uploadMetaPath = path.join(ROOT_DIR, "episodes", `auto_${slotKey}_meta.json`);
  fs.mkdirSync(path.dirname(uploadMetaPath), { recursive: true });
  fs.writeFileSync(uploadMetaPath, JSON.stringify(uploadMeta, null, 2), "utf8");
  console.log(`✅ YouTube yukleme manifestosu hazir: ${uploadMetaPath}`);

  if (shouldUpload) {
    const uploadArgs = [
      "scripts/youtube_publish.mjs",
      "upload",
      "--meta",
      uploadMetaPath,
    ];
    if (args["test-unlisted"]) {
      uploadArgs.push("--privacy", "unlisted");
    } else {
      uploadArgs.push("--schedule-ny-hour", String(slot.nyHour));
    }
    runCmd("node", uploadArgs, "YouTubeUploadAndSchedule");

    const receiptPath = path.join(ROOT_DIR, "out", "last-upload-receipt.json");
    const receipt = fs.existsSync(receiptPath)
      ? JSON.parse(fs.readFileSync(receiptPath, "utf8"))
      : null;
    const videoAbsPath = path.resolve(ROOT_DIR, outVideoRel);
    const videoBytes = fs.existsSync(videoAbsPath)
      ? fs.statSync(videoAbsPath).size
      : 0;
    const coverAbsPath = path.resolve(
      ROOT_DIR,
      isShort ? outShortCoverRel : outThumbRel,
    );

    await notifyProductionSucceeded({
      issueNumber: activeIssueNumber,
      slotKey,
      isShort,
      topicPlan,
      scriptJson,
      receipt,
      durationSec: Number(finalManifest.totalDurationSec || 0),
      videoBytes,
      coverImagePath: coverAbsPath,
    });
  } else {
    console.log(
      `\nℹ️  Yerel kuru-calistirma (dry-run) tamamlandi! Yuklemek icin '--upload' parametresi ekleyin.\n   Cikti MP4: ${outVideoRel}`,
    );
  }
  } catch (err) {
    fs.writeFileSync(failFlagPath, "1", "utf8");
    await notifyProductionFailed({
      issueNumber: activeIssueNumber,
      slotKey,
      isShort,
      topicPlan: activeTopicPlan,
      errorMessage: err.stack || err.message || String(err),
    });
    throw err;
  }
}

main().catch((err) => {
  console.error("\n❌ OTONOM URETIM HATASI:", err.stack || err.message || err);
  process.exitCode = 1;
});
