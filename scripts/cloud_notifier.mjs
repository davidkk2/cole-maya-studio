/**
 * Cole & Maya — Cloud Email Notification Dispatcher (via GitHub Issues -> GitHub Primary Email)
 * ---------------------------------------------------------------------------------------------
 * Uses GITHUB_TOKEN (github-actions[bot]) to open & update rich Markdown/HTML Issues mentioning
 * and assigning the repository owner (@davidkk2), which GitHub immediately delivers as DKIM-signed
 * HTML emails (with inline cover images!) to the owner's primary GitHub email address.
 */

import fs from "node:fs";
import path from "node:path";

function getGitHubContext() {
  const token = process.env.GITHUB_TOKEN?.trim();
  const repoFull = process.env.GITHUB_REPOSITORY?.trim(); // e.g. "davidkk2/cole-maya-studio"
  const owner =
    process.env.GITHUB_REPOSITORY_OWNER?.trim() ||
    (repoFull ? repoFull.split("/")[0] : "");
  const serverUrl = process.env.GITHUB_SERVER_URL?.trim() || "https://github.com";
  const runId = process.env.GITHUB_RUN_ID?.trim() || "";
  const runUrl =
    repoFull && runId ? `${serverUrl}/${repoFull}/actions/runs/${runId}` : "";

  if (!token || !repoFull || !owner) {
    return null;
  }
  return { token, repoFull, owner, runId, runUrl };
}

async function ghApi(token, method, apiPath, bodyObj = undefined) {
  const resp = await fetch(`https://api.github.com${apiPath}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "ColeMayaCloudNotifier/1.0",
      "X-GitHub-Api-Version": "2022-11-28",
      ...(bodyObj ? { "Content-Type": "application/json" } : {}),
    },
    body: bodyObj ? JSON.stringify(bodyObj) : undefined,
  });
  const text = await resp.text();
  let json = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = null;
  }
  return { ok: resp.ok, status: resp.status, json, text };
}

export function formatDualTimezone(isoString) {
  if (!isoString) return "Belirtilmedi";
  try {
    const d = new Date(isoString);
    const ny = new Intl.DateTimeFormat("tr-TR", {
      timeZone: "America/New_York",
      dateStyle: "medium",
      timeStyle: "short",
    }).format(d);
    const tr = new Intl.DateTimeFormat("tr-TR", {
      timeZone: "Europe/Istanbul",
      dateStyle: "medium",
      timeStyle: "short",
    }).format(d);
    return `${ny} (New York)  •  ${tr} (Türkiye TSİ)`;
  } catch {
    return isoString;
  }
}

/**
 * Uploads a rendered cover PNG/JPG to a public direct-image URL so Gmail's image proxy
 * renders the video cover inline inside the notification email even when the GitHub repo is Private.
 */
export async function uploadCoverImagePublic(localFilePath) {
  try {
    if (!localFilePath || !fs.existsSync(localFilePath)) return null;
    const bytes = fs.readFileSync(localFilePath);
    const ext = path.extname(localFilePath).toLowerCase() || ".jpg";
    const mime = ext === ".png" ? "image/png" : "image/jpeg";
    const fileName = `cover${ext}`;

    // Primary: Catbox direct CDN
    try {
      const fd = new FormData();
      fd.append("reqtype", "fileupload");
      fd.append("fileToUpload", new Blob([bytes], { type: mime }), fileName);
      const r = await fetch("https://catbox.moe/user/api.php", {
        method: "POST",
        body: fd,
        signal: AbortSignal.timeout(20_000),
      });
      const url = (await r.text()).trim();
      if (r.ok && url.startsWith("https://")) {
        return url;
      }
    } catch {
      // Fallback below
    }

    // Fallback: Litterbox 72h CDN
    const fd2 = new FormData();
    fd2.append("reqtype", "fileupload");
    fd2.append("time", "72h");
    fd2.append("fileToUpload", new Blob([bytes], { type: mime }), fileName);
    const r2 = await fetch(
      "https://litterbox.catbox.moe/resources/internals/api.php",
      {
        method: "POST",
        body: fd2,
        signal: AbortSignal.timeout(20_000),
      },
    );
    const url2 = (await r2.text()).trim();
    if (r2.ok && url2.startsWith("https://")) {
      return url2;
    }
    return null;
  } catch {
    return null;
  }
}

export function diagnoseErrorForOwner(errMessage = "") {
  const msg = String(errMessage || "");

  if (/invalid_grant|Token has been expired or revoked|YT_REFRESH_TOKEN/i.test(msg)) {
    return {
      needsAction: true,
      badge: "🔴 EVET — Müdahaleniz Gerekiyor",
      explanation:
        "YouTube OAuth oturum anahtarınızın (`YT_REFRESH_TOKEN`) süresi dolmuş veya iptal edilmiş. Bilgisayarınızda `npm run yt:login` komutunu çalıştırıp yeni `YT_REFRESH_TOKEN` değerini GitHub deponuzun Secrets bölümüne güncellemeniz gerekiyor.",
    };
  }

  if (/API_KEY_INVALID|API key not valid|GEMINI_API_KEY bulunamadi/i.test(msg)) {
    return {
      needsAction: true,
      badge: "🔴 EVET — Müdahaleniz Gerekiyor",
      explanation:
        "Google Gemini API anahtarınız (`GEMINI_API_KEY`) eksik veya geçersiz görünüyor. Google AI Studio üzerinden anahtarınızı kontrol edip GitHub Secrets içinde güncelleyin.",
    };
  }

  if (/uploadLimitExceeded|quotaExceeded/i.test(msg)) {
    return {
      needsAction: false,
      badge: "🟡 HAYIR — Otomatik Düzelecek (Günlük YouTube Kotası)",
      explanation:
        "YouTube Data API günlük yükleme/kota sınırına ulaşıldı. Sizin bir şey yapmanıza gerek yoktur; kota Pasifik saatiyle gece yarısı otomatik sıfırlanır ve sonraki vardiyalar kendiliğinden devam eder.",
    };
  }

  if (/HTTP 503|HTTP 429|RESOURCE_EXHAUSTED|ETIMEDOUT|ECONNRESET|socket timeout/i.test(msg)) {
    return {
      needsAction: false,
      badge: "🟢 HAYIR — Otomatik Düzelecek (Geçici Sunucu Yoğunluğu)",
      explanation:
        "Dış servislerde (Gemini / Wikimedia / Ağ) anlık yoğunluk veya zaman aşımı yaşandı. Müdahalenize gerek yoktur; bir sonraki yayın vardiyasında sistem otomatik olarak çalışmaya devam edecektir.",
    };
  }

  return {
    needsAction: true,
    badge: "🟡 KONTROL ÖNERİLİR — Teknik Üretim Hatası",
    explanation:
      "Üretim adımlarından birinde beklenmeyen bir hata oluştu. Aşağıdaki teknik hata özetini ve GitHub Actions çalışma günlüğünü inceleyebilirsiniz.",
  };
}

/**
 * 1) Sends "Video Production Started" email with Topic, Format (Shorts vs Main), Content Summary, and Target Time.
 * Returns created GitHub Issue number (or null if running locally without GITHUB_TOKEN).
 */
export async function notifyProductionStarted({
  slotKey,
  isShort,
  targetPublishISO,
  topicPlan,
}) {
  const ctx = getGitHubContext();
  if (!ctx) return null;

  const formatLabel = isShort
    ? "📱 DİKEY YOUTUBE SHORTS (9:16 • #Shorts)"
    : "🖥️ ANA YATAY BELGESEL (16:9 • Prime-Time)";
  const shortBadge = isShort ? "📱 Shorts" : "🖥️ Ana Video";
  const trHeadline =
    topicPlan.turkishTitle || topicPlan.selectedHeadline || "Yeni Gündem Dosyası";
  const trSummary =
    topicPlan.turkishSummary || topicPlan.angleSummary || "İçerik hazırlanıyor.";

  const title = `🎬 [ÜRETİM BAŞLADI] ${shortBadge} (${slotKey.toUpperCase()}) — ${trHeadline}`.slice(
    0,
    240,
  );

  const body = [
    `Merhaba @${ctx.owner}, **Cole & Maya** bulut stüdyosu yeni bir video üretimine başladı!`,
    ``,
    `### 📋 Üretim Kimlik Kartı`,
    `| Alan | Detay |`,
    `| :--- | :--- |`,
    `| **Video Türü** | **${formatLabel}** |`,
    `| **Vardiya Kodu** | \`${slotKey.toUpperCase()}\` |`,
    `| **Hedef Yayın Saati** | ${formatDualTimezone(targetPublishISO)} |`,
    `| **Seçilen ABD Gündemi** | ${topicPlan.selectedHeadline || "-"} |`,
    `| **İlgilenmeniz Gereken Durum** | 🟢 **Hayır** — Seslendirme, kurgu ve render bulutta otomatik ilerliyor. |`,
    ``,
    `### 🧠 Videonun Konusu ve İçerik Özeti`,
    `> ${trSummary}`,
    ``,
    topicPlan.historicalParallel
      ? `**🏛️ Tarihsel / Kurumsal Paralel:** ${topicPlan.historicalParallel}\n`
      : ``,
    ctx.runUrl ? `🔗 **Canlı Bulut Üretim Ekranı:** [GitHub Actions Çalışmasını Gör](${ctx.runUrl})` : ``,
    ``,
    `_Video render edilip YouTube'a yüklendiğinde kapak görseli ve YouTube linkiyle birlikte ikinci bildirim maili gelecektir._`,
  ]
    .filter(Boolean)
    .join("\n");

  const res = await ghApi(ctx.token, "POST", `/repos/${ctx.repoFull}/issues`, {
    title,
    body,
    assignees: [ctx.owner],
  });

  if (res.ok && res.json?.number) {
    console.log(`📧 Baslangic bildirim maili gonderildi (Issue #${res.json.number}).`);
    return res.json.number;
  }
  console.warn(`⚠️ Baslangic bildirimi gonderilemedi (${res.status}): ${res.text.slice(0, 180)}`);
  return null;
}

/**
 * 2) Sends "Video Uploaded & Scheduled" email with Inline Cover Image, Title, Topic, Duration, and Links.
 */
export async function notifyProductionSucceeded({
  issueNumber,
  slotKey,
  isShort,
  topicPlan,
  scriptJson,
  receipt,
  durationSec,
  videoBytes,
  coverImagePath,
}) {
  const ctx = getGitHubContext();
  if (!ctx) return;

  const coverUrl = await uploadCoverImagePublic(coverImagePath);
  const formatLabel = isShort
    ? "📱 DİKEY YOUTUBE SHORTS (9:16 • #Shorts)"
    : "🖥️ ANA YATAY BELGESEL (16:9 • Full HD + Özel Kapak)";
  const shortBadge = isShort ? "📱 Shorts" : "🖥️ Ana Video";
  const durMin = Math.floor(durationSec / 60);
  const durRem = Math.round(durationSec % 60);
  const durText =
    durMin > 0 ? `${durMin} dk ${durRem} sn (${durationSec.toFixed(1)}s)` : `${durationSec.toFixed(1)} saniye`;
  const sizeMB = (videoBytes / (1024 * 1024)).toFixed(1);
  const trSummary =
    topicPlan?.turkishSummary || topicPlan?.angleSummary || "";

  const attentionText =
    !isShort && receipt && !receipt.thumbnailApplied
      ? "🟡 **Küçük Not:** Video başarıyla yüklendi ve zamanlandı ancak özel kapak görseli API üzerinden uygulanamadı (YouTube Studio'dan tek tıkla seçebilirsiniz)."
      : "🟢 **HAYIR — Her şey kusursuz tamamlandı.** Video YouTube kanalınıza yüklendi ve yayın saatine kuruldu.";

  const imgWidth = isShort ? 300 : 560;
  const coverSection = coverUrl
    ? [
        `### 🖼️ Üretilen Video Kapağı`,
        `<p><img src="${coverUrl}" width="${imgWidth}" alt="Cole & Maya Video Kapağı" /></p>`,
        ``,
      ].join("\n")
    : ``;

  const body = [
    `🎉 Müjde @${ctx.owner}! **${shortBadge}** üretimi tamamlandı ve **YouTube kanalınıza başarıyla yüklendi!**`,
    ``,
    coverSection,
    `### ✅ Yükleme & Yayın Özeti`,
    `| Alan | Detay |`,
    `| :--- | :--- |`,
    `| **Yükleme Durumu** | ✅ **YOUTUBE'A YÜKLENDİ VE ZAMANLANDI** |`,
    `| **Video Formatı** | **${formatLabel}** |`,
    `| **YouTube Başlığı (ABD)** | **${receipt?.title || scriptJson?.youtubeTitle || "-"}** |`,
    `| **Süre & Boyut** | ${durText} • ${sizeMB} MB |`,
    `| **Yayınlanacağı Tarih/Saat** | **${formatDualTimezone(receipt?.publishAt)}** |`,
    `| **YouTube İzleme Linki** | ${receipt?.watchUrl ? `[🎬 ${receipt.watchUrl}](${receipt.watchUrl})` : "-"} |`,
    `| **YouTube Studio Kontrol** | ${receipt?.studioUrl ? `[🛠️ YouTube Studio'da Aç](${receipt.studioUrl})` : "-"} |`,
    ``,
    `### 🛠️ İlgilenmeniz Gereken Bir Konu Var mı?`,
    attentionText,
    ``,
    `### 🧠 Videonun Konusu ve İçeriği`,
    `- **Gündem Kaynağı:** ${topicPlan?.selectedHeadline || "-"}`,
    `- **Türkçe İçerik Özeti:** ${trSummary}`,
    topicPlan?.historicalParallel
      ? `- **Tarihsel / Kurumsal Paralel:** ${topicPlan.historicalParallel}`
      : ``,
    ctx.runUrl ? `\n🔗 [GitHub Bulut Çalışma Kaydı](${ctx.runUrl})` : ``,
  ]
    .filter(Boolean)
    .join("\n");

  const doneTitle = `✅ [YÜKLENDİ] ${shortBadge} (${slotKey.toUpperCase()}) — ${receipt?.title || topicPlan?.turkishTitle || "Video Hazır"}`.slice(
    0,
    240,
  );

  if (issueNumber) {
    await ghApi(
      ctx.token,
      "POST",
      `/repos/${ctx.repoFull}/issues/${issueNumber}/comments`,
      { body },
    );
    await ghApi(ctx.token, "PATCH", `/repos/${ctx.repoFull}/issues/${issueNumber}`, {
      title: doneTitle,
      state: "closed",
    });
    console.log(`📧 Yukleme basari maili gonderildi ve Issue #${issueNumber} kapatildi.`);
  } else {
    const created = await ghApi(ctx.token, "POST", `/repos/${ctx.repoFull}/issues`, {
      title: doneTitle,
      body,
      assignees: [ctx.owner],
    });
    if (created.ok && created.json?.number) {
      await ghApi(
        ctx.token,
        "PATCH",
        `/repos/${ctx.repoFull}/issues/${created.json.number}`,
        { state: "closed" },
      );
    }
  }
}

/**
 * 3) Sends "Production Error & Action Required Diagnosis" email whenever an error occurs.
 */
export async function notifyProductionFailed({
  issueNumber,
  slotKey,
  isShort,
  topicPlan,
  errorMessage,
}) {
  const ctx = getGitHubContext();
  if (!ctx) return;

  const diag = diagnoseErrorForOwner(errorMessage);
  const shortBadge = isShort ? "📱 Shorts" : "🖥️ Ana Video";
  const formatLabel = isShort
    ? "📱 DİKEY YOUTUBE SHORTS (9:16)"
    : "🖥️ ANA YATAY BELGESEL (16:9)";

  const errTitle = `🚨 [ÜRETİM HATASI] ${shortBadge} (${slotKey.toUpperCase()}) — ${
    diag.needsAction ? "Kontrol Önerilir" : "Otomatik Telafi Edilecek"
  }`.slice(0, 240);

  const body = [
    `⚠️ Merhaba @${ctx.owner}, **${shortBadge} (\`${slotKey.toUpperCase()}\`)** vardiyasında üretim/yükleme sırasında bir hata oluştu.`,
    ``,
    `### 🛠️ İlgilenmeniz Gereken Bir Konu Var mı?`,
    `**${diag.badge}**`,
    `> ${diag.explanation}`,
    ``,
    `### 📋 Vardiya & Konu Bilgisi`,
    `| Alan | Detay |`,
    `| :--- | :--- |`,
    `| **Yükleme Durumu** | ❌ **YÜKLENEMEDİ (Üretim yarıda kesildi)** |`,
    `| **Video Formatı** | ${formatLabel} |`,
    `| **Vardiya** | \`${slotKey.toUpperCase()}\` |`,
    `| **Üzerinde Çalışılan Konu** | ${topicPlan?.turkishTitle || topicPlan?.selectedHeadline || "Konu seçimi aşamasında hata oluştu"} |`,
    ctx.runUrl
      ? `| **Hata Günlüğü (Logs)** | [🔍 GitHub Actions Kaydını İncele](${ctx.runUrl}) |`
      : ``,
    ``,
    `### 🧾 Teknik Hata Detayı`,
    "```text",
    String(errorMessage || "Bilinmeyen hata").slice(0, 1200),
    "```",
  ]
    .filter(Boolean)
    .join("\n");

  if (issueNumber) {
    await ghApi(
      ctx.token,
      "POST",
      `/repos/${ctx.repoFull}/issues/${issueNumber}/comments`,
      { body },
    );
    await ghApi(ctx.token, "PATCH", `/repos/${ctx.repoFull}/issues/${issueNumber}`, {
      title: errTitle,
      state: diag.needsAction ? "open" : "closed",
    });
    console.log(`📧 Hata teshis maili gonderildi (Issue #${issueNumber}).`);
  } else {
    const created = await ghApi(ctx.token, "POST", `/repos/${ctx.repoFull}/issues`, {
      title: errTitle,
      body,
      assignees: [ctx.owner],
    });
    if (created.ok && created.json?.number && !diag.needsAction) {
      await ghApi(
        ctx.token,
        "PATCH",
        `/repos/${ctx.repoFull}/issues/${created.json.number}`,
        { state: "closed" },
      );
    }
    console.log(`📧 Hata teshis maili yeni kayit olarak gonderildi.`);
  }
}

// CLI entrypoint for workflow-level infrastructure failures (before auto_cloud_producer.mjs starts)
if (process.argv.includes("--infra-failure")) {
  const idx = process.argv.indexOf("--infra-failure");
  const slotKey = String(process.argv[idx + 1] || "short1").toLowerCase();
  const isShort = slotKey !== "main";
  notifyProductionFailed({
    issueNumber: null,
    slotKey,
    isShort,
    topicPlan: null,
    errorMessage:
      "GitHub Actions bulut sunucusu hazırlık aşamasında (bağımlılık kurulumu veya zaman aşımı) kesintiye uğradı. Lütfen yukarıdaki bağlantıdan GitHub Actions çalışma kaydını kontrol edin.",
  }).catch((e) => {
    console.error("Infra failure notify error:", e);
  });
}
