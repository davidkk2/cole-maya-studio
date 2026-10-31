#!/usr/bin/env node
/**
 * Local helper: Reads local gitignored secrets/ files and prints the 4 exact
 * GitHub Actions Repository Secrets values so you can copy-paste them in 30 seconds.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

const clientRaw = JSON.parse(
  fs.readFileSync(path.join(ROOT, "secrets", "client_secret.json"), "utf8"),
);
const cfg = clientRaw.installed || clientRaw.web;
const tokenRaw = JSON.parse(
  fs.readFileSync(path.join(ROOT, "secrets", "youtube_token.json"), "utf8"),
);
const geminiKey = fs
  .readFileSync(path.join(ROOT, "secrets", "gemini_api_key.txt"), "utf8")
  .trim();

console.log("\n==============================================================");
console.log("🔐 GITHUB REPOSITORY SECRETS (Settings -> Secrets -> Actions)");
console.log("==============================================================\n");
console.log(`1) Name : GEMINI_API_KEY\n   Value: ${geminiKey}\n`);
console.log(`2) Name : YT_CLIENT_ID\n   Value: ${cfg.client_id}\n`);
console.log(`3) Name : YT_CLIENT_SECRET\n   Value: ${cfg.client_secret}\n`);
console.log(`4) Name : YT_REFRESH_TOKEN\n   Value: ${tokenRaw.refresh_token}\n`);
console.log("==============================================================\n");
