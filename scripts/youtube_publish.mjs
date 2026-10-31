#!/usr/bin/env node
import crypto from "node:crypto";
import dns from "node:dns";
import fs from "node:fs";
import http from "node:http";
import https from "node:https";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

// Prevent IPv6 happy-eyeballs timeouts on residential ISPs
dns.setDefaultResultOrder("ipv4first");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname, "..");
const CLIENT_SECRET_PATH = path.join(ROOT_DIR, "secrets", "client_secret.json");
const TOKEN_PATH = path.join(ROOT_DIR, "secrets", "youtube_token.json");

const SCOPES = [
  "https://www.googleapis.com/auth/youtube.upload",
  "https://www.googleapis.com/auth/youtube",
];

// 8 MB chunk size (must be a multiple of 256 KB per YouTube Resumable Upload API)
const CHUNK_SIZE = 8 * 1024 * 1024;

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (token.startsWith("--")) {
      const key = token.slice(2);
      const next = argv[i + 1];
      if (!next || next.startsWith("--")) {
        args[key] = true;
      } else {
        args[key] = next;
        i++;
      }
    } else {
      args._.push(token);
    }
  }
  return args;
}

function loadClientConfig() {
  if (process.env.YT_CLIENT_ID && process.env.YT_CLIENT_SECRET) {
    return {
      client_id: process.env.YT_CLIENT_ID.trim(),
      client_secret: process.env.YT_CLIENT_SECRET.trim(),
      token_uri: "https://oauth2.googleapis.com/token",
      auth_uri: "https://accounts.google.com/o/oauth2/v2/auth",
    };
  }
  if (!fs.existsSync(CLIENT_SECRET_PATH)) {
    throw new Error(
      `OAuth client_secret bulunamadi: ${CLIENT_SECRET_PATH} (veya YT_CLIENT_ID / YT_CLIENT_SECRET ortam degiskeni yok).`,
    );
  }
  const raw = JSON.parse(fs.readFileSync(CLIENT_SECRET_PATH, "utf8"));
  const cfg = raw.installed || raw.web;
  if (!cfg || !cfg.client_id || !cfg.client_secret) {
    throw new Error("secrets/client_secret.json gecersiz formatta.");
  }
  return cfg;
}

function openBrowser(url) {
  if (process.platform === "win32") {
    // rundll32 avoids '&' truncation issues in cmd.exe 'start'
    const child = spawn("rundll32", ["url.dll,FileProtocolHandler", url], {
      detached: true,
      stdio: "ignore",
    });
    child.unref();
  } else if (process.platform === "darwin") {
    spawn("open", [url], { detached: true, stdio: "ignore" }).unref();
  } else {
    spawn("xdg-open", [url], { detached: true, stdio: "ignore" }).unref();
  }
}

function base64Url(buf) {
  return buf
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

async function runOAuthLogin() {
  const client = loadClientConfig();
  const codeVerifier = base64Url(crypto.randomBytes(48));
  const codeChallenge = base64Url(
    crypto.createHash("sha256").update(codeVerifier).digest(),
  );
  const expectedState = base64Url(crypto.randomBytes(16));

  return new Promise((resolve, reject) => {
    const server = http.createServer(async (req, res) => {
      try {
        const reqUrl = new URL(req.url || "/", "http://localhost");
        const error = reqUrl.searchParams.get("error");
        const code = reqUrl.searchParams.get("code");
        const state = reqUrl.searchParams.get("state");

        if (error) {
          res.writeHead(400, { "Content-Type": "text/html; charset=utf-8" });
          res.end(
            `<h2>❌ Google OAuth Hatasi: ${error}</h2><p>Google Cloud Console &rarr; Audience (Test Users) listesine Gmail adresini eklediginden emin ol.</p>`,
          );
          server.close();
          reject(new Error(`Google OAuth error: ${error}`));
          return;
        }

        if (!code) {
          res.writeHead(204);
          res.end();
          return;
        }

        if (state !== expectedState) {
          res.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" });
          res.end("Invalid OAuth state.");
          server.close();
          reject(new Error("OAuth state mismatch."));
          return;
        }

        const address = server.address();
        const port = typeof address === "object" && address ? address.port : 80;
        const redirectUri = `http://localhost:${port}`;

        const tokenResp = await fetch(
          client.token_uri || "https://oauth2.googleapis.com/token",
          {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
              code,
              client_id: client.client_id,
              client_secret: client.client_secret,
              redirect_uri: redirectUri,
              grant_type: "authorization_code",
              code_verifier: codeVerifier,
            }),
          },
        );

        const tokenData = await tokenResp.json();
        if (!tokenResp.ok) {
          throw new Error(
            `Token degisimi basarisiz: ${JSON.stringify(tokenData)}`,
          );
        }

        let existing = {};
        if (fs.existsSync(TOKEN_PATH)) {
          try {
            existing = JSON.parse(fs.readFileSync(TOKEN_PATH, "utf8"));
          } catch {
            existing = {};
          }
        }

        const saved = {
          ...existing,
          ...tokenData,
          refresh_token: tokenData.refresh_token || existing.refresh_token,
          expiry_date: Date.now() + (tokenData.expires_in || 3600) * 1000,
          saved_at: new Date().toISOString(),
        };

        fs.mkdirSync(path.dirname(TOKEN_PATH), { recursive: true });
        fs.writeFileSync(TOKEN_PATH, JSON.stringify(saved, null, 2), "utf8");

        res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
        res.end(`<!doctype html>
<html>
<body style="font-family: system-ui, sans-serif; background:#0F172A; color:#F8FAFC; display:flex; align-items:center; justify-content:center; height:100vh; margin:0;">
  <div style="background:#1E293B; padding:36px 48px; border-radius:20px; border:3px solid #38BDF8; text-align:center; max-width:520px;">
    <h1 style="color:#FACC15; margin-top:0;">✅ YouTube Bağlantısı Başarılı!</h1>
    <p style="font-size:18px; line-height:1.5;">OAuth token güvenli şekilde kaydedildi.<br/>Artık bu sekmeyi kapatıp terminale dönebilirsin kanka!</p>
  </div>
</body>
</html>`);

        server.close();
        resolve(saved);
      } catch (err) {
        server.close();
        reject(err);
      }
    });

    server.listen(0, () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : 80;
      const redirectUri = `http://localhost:${port}`;

      const authUrl = new URL(
        client.auth_uri || "https://accounts.google.com/o/oauth2/v2/auth",
      );
      authUrl.searchParams.set("client_id", client.client_id);
      authUrl.searchParams.set("redirect_uri", redirectUri);
      authUrl.searchParams.set("response_type", "code");
      authUrl.searchParams.set("scope", SCOPES.join(" "));
      authUrl.searchParams.set("access_type", "offline");
      authUrl.searchParams.set("prompt", "consent");
      authUrl.searchParams.set("state", expectedState);
      authUrl.searchParams.set("code_challenge", codeChallenge);
      authUrl.searchParams.set("code_challenge_method", "S256");

      console.log("\n🔐 Tarayicida Google/YouTube giris ekrani aciliyor...");
      console.log(
        "👉 Tarayici otomatik acilmazsa bu linki kopyalayip ac:\n" +
          authUrl.toString() +
          "\n",
      );
      openBrowser(authUrl.toString());
    });
  });
}

async function getValidAccessToken() {
  const client = loadClientConfig();
  if (process.env.YT_REFRESH_TOKEN) {
    const resp = await fetch(
      client.token_uri || "https://oauth2.googleapis.com/token",
      {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          client_id: client.client_id,
          client_secret: client.client_secret,
          refresh_token: process.env.YT_REFRESH_TOKEN.trim(),
          grant_type: "refresh_token",
        }),
      },
    );
    const refreshed = await resp.json();
    if (!resp.ok || !refreshed.access_token) {
      throw new Error(
        `Bulut YT_REFRESH_TOKEN ile access_token alinamadi (${resp.status}): ${JSON.stringify(refreshed)}`,
      );
    }
    return refreshed.access_token;
  }

  if (!fs.existsSync(TOKEN_PATH)) {
    console.log("ℹ️ Kayitli oturum bulunamadi, ilk kez giris baslatiliyor...");
    const fresh = await runOAuthLogin();
    return fresh.access_token;
  }

  const token = JSON.parse(fs.readFileSync(TOKEN_PATH, "utf8"));
  if (
    token.access_token &&
    token.expiry_date &&
    Date.now() < token.expiry_date - 60_000
  ) {
    return token.access_token;
  }

  if (!token.refresh_token) {
    console.log("ℹ️ Refresh token yok, yeniden yetkilendirme aciliyor...");
    const fresh = await runOAuthLogin();
    return fresh.access_token;
  }

  const resp = await fetch(
    client.token_uri || "https://oauth2.googleapis.com/token",
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: client.client_id,
        client_secret: client.client_secret,
        refresh_token: token.refresh_token,
        grant_type: "refresh_token",
      }),
    },
  );

  const refreshed = await resp.json();
  if (!resp.ok) {
    throw new Error(
      `Access token yenilenemedi (${resp.status}): ${JSON.stringify(refreshed)}\n` +
        `Yeniden giris icin: npm run yt:auth`,
    );
  }

  const merged = {
    ...token,
    ...refreshed,
    refresh_token: refreshed.refresh_token || token.refresh_token,
    expiry_date: Date.now() + (refreshed.expires_in || 3600) * 1000,
    updated_at: new Date().toISOString(),
  };
  fs.writeFileSync(TOKEN_PATH, JSON.stringify(merged, null, 2), "utf8");
  return merged.access_token;
}

async function checkChannel(accessToken) {
  const resp = await fetch(
    "https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,status&mine=true",
    {
      headers: { Authorization: `Bearer ${accessToken}` },
    },
  );
  const data = await resp.json();
  if (!resp.ok) {
    throw new Error(
      `YouTube Data API v3 hatasi (${resp.status}): ${JSON.stringify(data)}\n` +
        `Ipucu: Google Cloud Console -> APIs & Services -> Library -> 'YouTube Data API v3' etkin (Enabled) olmali!`,
    );
  }

  if (!data.items || data.items.length === 0) {
    console.log("\n⚠️ DIKKAT: Hesaba giris basarili AMA henuz YouTube kanali olusturulmamis!");
    console.log(
      "👉 YouTube Ayarlar ekranindaki mavi 'Kanal olustur' butonuna tiklayip kanali olustur, sonra tekrar dene.\n",
    );
    return null;
  }

  const ch = data.items[0];
  const longStatus = ch.status?.longUploadsStatus || "unknown";
  const phoneVerified =
    longStatus === "allowed" || longStatus === "eligible";

  console.log("\n==========================================");
  console.log(`📺 Kanal Adi     : ${ch.snippet?.title}`);
  console.log(`🔗 Handle        : ${ch.snippet?.customUrl || "(henuz atanmamis)"}`);
  console.log(`🆔 Channel ID    : ${ch.id}`);
  console.log(`🌍 Ulke          : ${ch.snippet?.country || "(secilmemis - YouTube Studio'dan ayarlanabilir)"}`);
  console.log(
    `📱 Telefon Onayi : ${
      phoneVerified
        ? "✅ ONAYLI (Ozel Thumbnail + 15dk ustu video acik!)"
        : `⚠️ BEKLIYOR (${longStatus}) -> Ozel Thumbnail yuklemek icin YouTube Studio > Ayarlar > Kanal > Ozellik uygunlugu > Telefon numarasi dogrulamasi yap!`
    }`,
  );
  console.log("==========================================\n");
  return ch;
}

const CHANNEL_TITLE_US = "Cole & Maya";

const CHANNEL_DESCRIPTION_US = [
  "Primary-source investigations into global power, central banks, geopolitics, and declassified intelligence history — hosted from our studio by Cole & Maya.",
  "",
  "Every week, viral rumors and algorithmic myths distract millions of people from how real institutional power actually moves. On this channel, we skip the speculation and pull the receipts: timestamped official records, treaty calendars, financial filings, real archival footage, and declassified espionage dossiers.",
  "",
  "OUR VISUAL STANDARD:",
  "• Studio commentary & analysis by Cole & Maya",
  "• 100% real footage, archival photography & primary documents on screen — zero fictional reenactments",
  "",
  "New investigative episodes every week. Subscribe and turn on notifications to follow the primary record.",
].join("\n");

const CHANNEL_KEYWORDS_US = [
  '"Cole and Maya"',
  '"investigative documentary"',
  "geopolitics",
  '"global finance"',
  '"central banks"',
  '"declassified history"',
  '"intelligence history"',
  '"primary sources"',
  '"fact check"',
  '"economic power"',
  '"world affairs"',
  '"espionage history"',
  '"archival documentary"',
  '"media literacy"',
  '"financial history"',
].join(" ");

async function setupChannelBrandingAndSettings(accessToken) {
  console.log("\n⚙️  Cole & Maya kanal ayarlari ve yeni Banner YouTube Data API v3 uzerinden otomatik yapilandiriliyor...");

  const getResp = await fetch(
    "https://www.googleapis.com/youtube/v3/channels?part=brandingSettings,status,snippet,localizations&mine=true",
    {
      headers: { Authorization: `Bearer ${accessToken}` },
    },
  );
  const getJson = await getResp.json();
  if (!getResp.ok || !getJson.items?.length) {
    throw new Error(
      `Kanal bilgisi alinamadi (${getResp.status}): ${JSON.stringify(getJson)}`,
    );
  }

  const current = getJson.items[0];
  const channelId = current.id;

  // Step 1: Upload 2560x1440 Channel Banner via channelBanners.insert
  const bannerPath = path.join(ROOT_DIR, "out", "channel-banner.png");
  let bannerExternalUrl = current.brandingSettings?.image?.bannerExternalUrl;

  if (fs.existsSync(bannerPath)) {
    console.log("🖼️  Cole & Maya Kanal Banner gorseli (2560x1440) API ile yukleniyor...");
    const bannerBytes = fs.readFileSync(bannerPath);
    const bannerResp = await fetch(
      "https://www.googleapis.com/upload/youtube/v3/channelBanners/insert?uploadType=media",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "image/png",
          "Content-Length": String(bannerBytes.byteLength),
        },
        body: bannerBytes,
      },
    );
    const bannerJson = await bannerResp.json();
    if (bannerResp.ok && bannerJson.url) {
      bannerExternalUrl = bannerJson.url;
      console.log("✅ Yeni Cole & Maya Banner gorseli YouTube sunucusuna yuklendi!");
    } else {
      console.warn(
        `⚠️ Banner yukleme uyarisi (${bannerResp.status}): ${JSON.stringify(bannerJson)}`,
      );
    }
  }

  // Step 2a: Update Channel Branding (Description, Keywords, Default Language en, Country US, Banner)
  const existingChannelBrand = { ...(current.brandingSettings?.channel || {}) };
  delete existingChannelBrand.title;

  const brandingPayload = {
    id: channelId,
    brandingSettings: {
      channel: {
        ...existingChannelBrand,
        description: CHANNEL_DESCRIPTION_US,
        keywords: CHANNEL_KEYWORDS_US,
        defaultLanguage: "en",
        country: "US",
      },
      ...(bannerExternalUrl
        ? {
            image: {
              bannerExternalUrl,
            },
          }
        : {}),
    },
  };

  const updBrandResp = await fetch(
    "https://www.googleapis.com/youtube/v3/channels?part=brandingSettings",
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json; charset=UTF-8",
      },
      body: JSON.stringify(brandingPayload),
    },
  );
  const updBrandJson = await updBrandResp.json();
  if (!updBrandResp.ok) {
    throw new Error(
      `Kanal branding guncellenemedi (${updBrandResp.status}): ${JSON.stringify(updBrandJson)}`,
    );
  }
  console.log(
    "✅ Yeni Cole & Maya Kanal Aciklamasi, Anahtar Kelimeler, Varsayilan Dil (en), Ulke (US) ve 2560x1440 Banner kaydedildi!",
  );

  // Step 2b: Update Channel Localizations (en_US) separately per YouTube Data API v3 part rules
  const updatedLocalizations = {
    ...(current.localizations || {}),
    en_US: {
      title: CHANNEL_TITLE_US,
      description: CHANNEL_DESCRIPTION_US,
    },
  };

  const updLocResp = await fetch(
    "https://www.googleapis.com/youtube/v3/channels?part=localizations",
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json; charset=UTF-8",
      },
      body: JSON.stringify({
        id: channelId,
        localizations: updatedLocalizations,
      }),
    },
  );
  if (updLocResp.ok) {
    console.log(
      `✅ Kanal en_US Yerellestirmesi ('${CHANNEL_TITLE_US}' + Yeni Aciklama) kaydedildi!`,
    );
  } else {
    const locErr = await updLocResp.text();
    console.warn(`⚠️ Kanal localizations uyarisi (${updLocResp.status}): ${locErr}`);
  }

  // Step 3: Set Channel-Level Audience -> Not Made For Kids (protects US Finance/Geopolitics RPM & comments!)
  const statusPayload = {
    id: channelId,
    status: {
      selfDeclaredMadeForKids: false,
    },
  };
  const updStatusResp = await fetch(
    "https://www.googleapis.com/youtube/v3/channels?part=status",
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json; charset=UTF-8",
      },
      body: JSON.stringify(statusPayload),
    },
  );
  if (updStatusResp.ok) {
    console.log(
      "✅ Kanal Kitle Ayari: 'Cocuklara Ozel Degil (selfDeclaredMadeForKids: false)' olarak kilitlendi!",
    );
  } else {
    const stErr = await updStatusResp.text();
    console.warn(`⚠️ Kanal status uyarisi (${updStatusResp.status}): ${stErr}`);
  }

  console.log("\n🎉 COLE & MAYA KANAL AYARLARI VE YENI BANNER API ILE OTOMATIK TAMAMLANDI!\n");
}

/**
 * Calculates the next US East Coast Adult Documentary Prime-Time slot (17:00 America/New_York = 5:00 PM EST/EDT)
 */
function getNextNewYorkHourISO(targetHour = 17) {
  const now = new Date();
  for (let addHours = 1; addHours <= 36; addHours++) {
    const candidate = new Date(now.getTime() + addHours * 3600 * 1000);
    candidate.setUTCMinutes(0, 0, 0);
    const nyHour = Number(
      new Intl.DateTimeFormat("en-US", {
        timeZone: "America/New_York",
        hour: "numeric",
        hour12: false,
      }).format(candidate),
    );
    if (nyHour === targetHour) {
      return candidate.toISOString();
    }
  }
  return new Date(now.getTime() + 6 * 3600 * 1000).toISOString();
}

function getNextUSPrimeTimeISO() {
  return getNextNewYorkHourISO(17);
}

function httpsReq(method, targetUrl, headers, bodyBuf) {
  return new Promise((resolve, reject) => {
    const u = new URL(targetUrl);
    const req = https.request(
      {
        protocol: u.protocol,
        hostname: u.hostname,
        port: u.port || 443,
        path: u.pathname + u.search,
        method,
        headers,
        family: 4,
        timeout: 180_000,
      },
      (res) => {
        const chunks = [];
        res.on("data", (c) => chunks.push(c));
        res.on("end", () => {
          resolve({
            status: res.statusCode || 0,
            headers: res.headers,
            text: Buffer.concat(chunks).toString("utf8"),
          });
        });
      },
    );
    req.on("timeout", () => {
      req.destroy(new Error("HTTPS socket timeout"));
    });
    req.on("error", reject);
    if (bodyBuf && bodyBuf.length > 0) {
      req.write(bodyBuf);
    }
    req.end();
  });
}

async function uploadThumbnail(accessToken, videoId, thumbnailPath) {
  if (!fs.existsSync(thumbnailPath)) {
    console.log(`⚠️ Thumbnail dosyasi bulunamadi (${thumbnailPath}), atlaniyor.`);
    return false;
  }
  const ext = path.extname(thumbnailPath).toLowerCase();
  const mime = ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
  const bytes = fs.readFileSync(thumbnailPath);

  console.log(`🖼️  Ozel US Kapak Gorseli (Thumbnail) yukleniyor: ${thumbnailPath} ...`);
  const resp = await httpsReq(
    "POST",
    `https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=${encodeURIComponent(
      videoId,
    )}&uploadType=media`,
    {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": mime,
      "Content-Length": String(bytes.byteLength),
    },
    bytes,
  );

  if (resp.status < 200 || resp.status >= 300) {
    console.warn(
      `\n⚠️ Video yuklendi ama ozel Thumbnail ayarlanamadi (${resp.status}).\n` +
        `Cozum: npm run yt:thumb -- --video-id ${videoId} --file "${thumbnailPath}"\n` +
        `Detay: ${resp.text}\n`,
    );
    return false;
  }

  console.log("✅ Ozel Thumbnail basariyla ayarlandi!");
  return true;
}

async function uploadVideo(accessToken, meta, cliArgs) {
  const videoPath = path.resolve(ROOT_DIR, cliArgs.video || meta.videoFile);
  if (!fs.existsSync(videoPath)) {
    throw new Error(
      `Video MP4 dosyasi bulunamadi: ${videoPath}\n` +
        `Once render almak icin: npm run render:ep1  (veya tek komutta: npm run publish:ep1)`,
    );
  }

  const stat = fs.statSync(videoPath);
  const totalBytes = stat.size;

  let privacyStatus = cliArgs.privacy || meta.privacyStatus || "public";
  let publishAt = cliArgs["publish-at"] || meta.publishAt || undefined;

  if (cliArgs["schedule-ny-hour"] !== undefined) {
    const targetH = Number(cliArgs["schedule-ny-hour"]);
    privacyStatus = "private";
    publishAt = getNextNewYorkHourISO(targetH);
    console.log(
      `⏰ ABD Zamanlayici Aktif: Video ${publishAt} (${String(targetH).padStart(2, "0")}:00 New York EST/EDT) saatinde otomatik yayina girecek!`,
    );
  } else if (cliArgs["schedule-us-prime"]) {
    privacyStatus = "private";
    publishAt = getNextUSPrimeTimeISO();
    console.log(
      `⏰ ABD Prime-Time Zamanlayici Aktif: Video ${publishAt} (17:00 New York EST/EDT) saatinde otomatik yayina girecek!`,
    );
  }

  const requestBody = {
    snippet: {
      title: cliArgs.title || meta.title,
      description: meta.description,
      tags: meta.tags || [],
      categoryId: String(meta.categoryId || "25"),
      defaultLanguage: meta.defaultLanguage || "en-US",
      defaultAudioLanguage: meta.defaultAudioLanguage || "en-US",
    },
    status: {
      privacyStatus,
      selfDeclaredMadeForKids: Boolean(meta.madeForKids ?? false),
      ...(publishAt ? { publishAt } : {}),
    },
    recordingDetails: {
      locationDescription: meta.locationDescription || "United States",
    },
  };

  console.log(`\n🚀 YouTube ABD Kanalina Resumable Upload Baslatiliyor...`);
  console.log(`📄 Baslik  : ${requestBody.snippet.title}`);
  console.log(`📦 Boyut   : ${(totalBytes / (1024 * 1024)).toFixed(2)} MB`);
  console.log(`🔒 Gizlilik: ${privacyStatus}${publishAt ? ` (Yayin: ${publishAt})` : ""}`);

  const bodyBuffer = Buffer.from(JSON.stringify(requestBody), "utf8");
  const initResp = await httpsReq(
    "POST",
    "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status,recordingDetails",
    {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json; charset=UTF-8",
      "Content-Length": String(bodyBuffer.byteLength),
      "X-Upload-Content-Length": String(totalBytes),
      "X-Upload-Content-Type": "video/mp4",
    },
    bodyBuffer,
  );

  if (initResp.status < 200 || initResp.status >= 300) {
    throw new Error(
      `Upload oturumu baslatilamadi (${initResp.status}): ${initResp.text}`,
    );
  }

  const uploadUrl = initResp.headers.location;
  if (!uploadUrl) {
    throw new Error("YouTube Resumable Upload Location basligi donmedi.");
  }

  const fd = fs.openSync(videoPath, "r");
  let offset = 0;
  let uploadedVideo = null;
  const httpsPut = (targetUrl, headers, bodyBuf) =>
    httpsReq("PUT", targetUrl, headers, bodyBuf);

  try {
    while (offset < totalBytes) {
      const remaining = totalBytes - offset;
      const chunkLen = Math.min(CHUNK_SIZE, remaining);
      const buffer = Buffer.allocUnsafe(chunkLen);
      fs.readSync(fd, buffer, 0, chunkLen, offset);

      const endByte = offset + chunkLen - 1;
      let putResp = null;

      for (let attempt = 1; attempt <= 5; attempt++) {
        try {
          putResp = await httpsPut(
            uploadUrl,
            {
              "Content-Length": String(chunkLen),
              "Content-Type": "video/mp4",
              "Content-Range": `bytes ${offset}-${endByte}/${totalBytes}`,
            },
            buffer,
          );
          break;
        } catch (err) {
          console.warn(
            `\n⚠️ Ag dalgalanmasi (deneme ${attempt}/5): ${err.message}. Kaldigi yerden devam ediliyor...`,
          );
          await new Promise((r) => setTimeout(r, 2000 * attempt));
          // Query Google Resumable Upload server for exact received byte offset
          try {
            const probe = await httpsPut(
              uploadUrl,
              {
                "Content-Length": "0",
                "Content-Range": `bytes */${totalBytes}`,
              },
              Buffer.alloc(0),
            );
            if (probe.status === 308 && probe.headers.range) {
              const m = String(probe.headers.range).match(/bytes=0-(\d+)/);
              if (m) {
                offset = Number(m[1]) + 1;
              }
            } else if (probe.status >= 200 && probe.status < 300) {
              putResp = probe;
              break;
            }
          } catch {
            // Ignore probe error and retry chunk
          }
          if (attempt === 5) throw err;
        }
      }

      if (!putResp) {
        throw new Error("Parca yukleme yaniti alinamadi.");
      }

      if (putResp.status === 308) {
        const rangeHdr = putResp.headers?.range;
        if (rangeHdr) {
          const m = String(rangeHdr).match(/bytes=0-(\d+)/);
          offset = m ? Number(m[1]) + 1 : offset + chunkLen;
        } else {
          offset += chunkLen;
        }
        const pct = ((offset / totalBytes) * 100).toFixed(1);
        console.log(
          `⬆️  Yukleniyor: %${pct} (${(offset / 1048576).toFixed(1)} / ${(totalBytes / 1048576).toFixed(1)} MB)`,
        );
        continue;
      }

      if (putResp.status >= 200 && putResp.status < 300) {
        uploadedVideo = JSON.parse(putResp.text);
        console.log(
          `⬆️  Yukleniyor: %100.0 (${(totalBytes / 1048576).toFixed(1)} MB) — Tamamlandi!`,
        );
        break;
      }

      throw new Error(`Parca yukleme hatasi (${putResp.status}): ${putResp.text}`);
    }
  } finally {
    fs.closeSync(fd);
  }

  if (!uploadedVideo?.id) {
    throw new Error("Video yuklendi ancak YouTube video ID donmedi.");
  }

  let thumbOk = false;
  if (meta.isShort) {
    console.log("📱 Dikey YouTube Shorts yuklendi — yerel 9:16 kapak cercevesi korundu.");
  } else {
    const thumbPath = path.resolve(
      ROOT_DIR,
      cliArgs.thumbnail || meta.thumbnailFile || "out/Ep01-Thumbnail-Lagarde.png",
    );
    thumbOk = await uploadThumbnail(accessToken, uploadedVideo.id, thumbPath);
  }

  const receipt = {
    videoId: uploadedVideo.id,
    watchUrl: `https://youtu.be/${uploadedVideo.id}`,
    studioUrl: `https://studio.youtube.com/video/${uploadedVideo.id}/edit`,
    title: requestBody.snippet.title,
    privacyStatus,
    publishAt: publishAt || null,
    thumbnailApplied: thumbOk,
    uploadedAt: new Date().toISOString(),
  };

  const receiptPath = path.join(ROOT_DIR, "out", "last-upload-receipt.json");
  fs.mkdirSync(path.dirname(receiptPath), { recursive: true });
  fs.writeFileSync(receiptPath, JSON.stringify(receipt, null, 2), "utf8");

  console.log("\n🎉 BINGO! VIDEO YOUTUBE ABD KANALINA YUKLENDI!");
  console.log(`🎬 Izleme Linki : ${receipt.watchUrl}`);
  console.log(`🛠️  Studio Linki : ${receipt.studioUrl}\n`);
}

function ensureRendered(meta, forceRender = false) {
  const videoPath = path.resolve(ROOT_DIR, meta.videoFile);
  const thumbPath = path.resolve(ROOT_DIR, meta.thumbnailFile);

  if (forceRender || !fs.existsSync(thumbPath)) {
    console.log(`🎨 Thumbnail render aliniyor (${meta.thumbnailCompositionId})...`);
    const res = spawnSync(
      "npx",
      ["remotion", "still", meta.thumbnailCompositionId, meta.thumbnailFile],
      { cwd: ROOT_DIR, stdio: "inherit", shell: true },
    );
    if (res.status !== 0) {
      throw new Error("Thumbnail render basarisiz oldu.");
    }
  }

  if (forceRender || !fs.existsSync(videoPath)) {
    console.log(
      `🎬 10 Dakikalik Full HD Film render aliniyor (${meta.compositionId} -> ${meta.videoFile})...`,
    );
    const res = spawnSync(
      "npx",
      ["remotion", "render", meta.compositionId, meta.videoFile],
      { cwd: ROOT_DIR, stdio: "inherit", shell: true },
    );
    if (res.status !== 0) {
      throw new Error("Video MP4 render basarisiz oldu.");
    }
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0] || "help";

  if (cmd === "help" || args.help) {
    console.log(`
Cole & Maya — US Investigative Studio (YouTube Otomasyon Araci)
Kullanim:
  npm run yt:auth                                                   -> Google OAuth girisi yap & token kaydet
  npm run yt:check                                                  -> Kanal durumunu ve telefon dogrulamasini kontrol et
  npm run yt:setup                                                  -> Yeni kanal aciklamasi, anahtar kelimeler ve Banner'i uygula
  npm run yt:upload -- --meta episodes/ep01_lagarde_early_exit.json -> Hazir MP4 + Thumbnail'i ABD ayarlariyla yukle
  npm run yt:upload:prime                                           -> ABD Belgesel Prime-Time (17:00 New York) saatine zamanla!
  npm run yt:thumb -- --video-id <ID>                               -> Mevcut videoya ozel kapak gorseli yukle
  npm run publish:ep1                                               -> Eksikse render al + otomatik YouTube'a yukle!
`);
    return;
  }

  if (cmd === "auth") {
    const token = await runOAuthLogin();
    await checkChannel(token.access_token);
    return;
  }

  if (cmd === "setup") {
    const accessToken = await getValidAccessToken();
    const channel = await checkChannel(accessToken);
    if (!channel) {
      process.exitCode = 1;
      return;
    }
    await setupChannelBrandingAndSettings(accessToken);
    return;
  }

  if (cmd === "check") {
    const accessToken = await getValidAccessToken();
    await checkChannel(accessToken);
    return;
  }

  if (cmd === "set-privacy") {
    const videoId = args["video-id"];
    const privacyStatus = args.privacy || "unlisted";
    if (!videoId || !["public", "unlisted", "private"].includes(privacyStatus)) {
      throw new Error(
        "Kullanim: node scripts/youtube_publish.mjs set-privacy --video-id <ID> --privacy <unlisted|private|public>",
      );
    }
    const accessToken = await getValidAccessToken();
    const getV = await fetch(
      `https://www.googleapis.com/youtube/v3/videos?part=status&id=${encodeURIComponent(videoId)}`,
      { headers: { Authorization: `Bearer ${accessToken}` } },
    );
    const getVJ = await getV.json();
    const curStatus = getVJ.items?.[0]?.status || {};
    const updV = await fetch(
      "https://www.googleapis.com/youtube/v3/videos?part=status",
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json; charset=UTF-8",
        },
        body: JSON.stringify({
          id: videoId,
          status: {
            privacyStatus,
            selfDeclaredMadeForKids: Boolean(curStatus.selfDeclaredMadeForKids ?? false),
          },
        }),
      },
    );
    if (!updV.ok) {
      throw new Error(`Gizlilik guncellenemedi (${updV.status}): ${await updV.text()}`);
    }
    console.log(`✅ Video (${videoId}) gizlilik durumu '${privacyStatus}' olarak guncellendi!`);
    return;
  }

  if (cmd === "thumbnail") {
    const videoId = args["video-id"];
    const file = path.resolve(ROOT_DIR, args.file || "out/Ep01-Thumbnail-Lagarde.png");
    if (!videoId) {
      throw new Error("Kullanim: npm run yt:thumb -- --video-id <VIDEO_ID>");
    }
    const accessToken = await getValidAccessToken();
    await uploadThumbnail(accessToken, videoId, file);
    return;
  }

  if (cmd === "update-meta") {
    const receiptPath = path.join(ROOT_DIR, "out", "last-upload-receipt.json");
    const receipt = fs.existsSync(receiptPath)
      ? JSON.parse(fs.readFileSync(receiptPath, "utf8"))
      : null;
    const videoId = args["video-id"] || receipt?.videoId;
    if (!videoId) {
      throw new Error("Video ID bulunamadi.");
    }
    const metaPath = path.resolve(
      ROOT_DIR,
      args.meta || "episodes/ep01_lagarde_early_exit.json",
    );
    const meta = JSON.parse(fs.readFileSync(metaPath, "utf8"));
    const accessToken = await getValidAccessToken();

    const updResp = await fetch(
      "https://www.googleapis.com/youtube/v3/videos?part=snippet,recordingDetails",
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json; charset=UTF-8",
        },
        body: JSON.stringify({
          id: videoId,
          snippet: {
            title: meta.title,
            description: meta.description,
            tags: meta.tags || [],
            categoryId: String(meta.categoryId || "25"),
            defaultLanguage: meta.defaultLanguage || "en-US",
            defaultAudioLanguage: meta.defaultAudioLanguage || "en-US",
          },
          recordingDetails: {
            locationDescription: meta.locationDescription || "United States",
          },
        }),
      },
    );
    if (!updResp.ok) {
      throw new Error(`Video metadata guncellenemedi: ${await updResp.text()}`);
    }
    console.log(`✅ Video (${videoId}) ABD metadata + konum (United States) + hashtagler guncellendi!`);
    return;
  }

  if (cmd === "upload" || cmd === "publish") {
    const metaPath = path.resolve(
      ROOT_DIR,
      args.meta || "episodes/ep01_lagarde_early_exit.json",
    );
    const meta = JSON.parse(fs.readFileSync(metaPath, "utf8"));
    let accessToken = await getValidAccessToken();
    const channel = await checkChannel(accessToken);
    if (!channel) {
      process.exitCode = 1;
      return;
    }
    if (cmd === "publish") {
      ensureRendered(meta, Boolean(args["force-render"]));
      // Refresh token after long render so upload always has a fresh 60-min token
      accessToken = await getValidAccessToken();
    }
    await uploadVideo(accessToken, meta, args);
    return;
  }

  throw new Error(`Bilinmeyen komut: ${cmd}. Yardim icin: node scripts/youtube_publish.mjs help`);
}

main().catch((err) => {
  console.error("\n❌ HATA:", err.message || err);
  process.exitCode = 1;
});
