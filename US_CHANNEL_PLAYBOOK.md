# US Stickman Slapstick Studio - Daily 10-Min Production Playbook

## 1. US Channel Setup Checklist (No VPN!)
- **Upload IP:** Always upload from your normal, clean residential connection (never use free/shared VPNs).
- **Channel Settings -> Basic Info:**
  - **Video Language:** `English (United States)`
  - **Title & Description Language:** `English (United States)`
  - **Category:** `Film & Animation` (exact category used by Alan Becker & Pencilmation)
  - **Made for Kids (COPPA):** Select **"No, it's not made for kids"** IF targeting general teen/adult slapstick audience (higher RPM + personalized ads + comments enabled). Avoid nursery-rhyme themes so YouTube keeps full ad monetization active.

## 2. High-CTR US Title Formulas (Zero-Dialogue Universal Hooks)
- `Stickman vs GIANT ANT! (Full Compilation)`
- `LVL 1 Picnic vs LVL 999 Mutant Ant!`
- `Stickman vs THE IMPOSSIBLE BUNKER! (3 Episodes)`
- `Don't Touch Stickman's Burger! (Animation)`

## 3. Daily 10-Minute Episode Formula (`10:05` = `18,150` frames @ 30fps)
Top US non-verbal cartoon channels structure every 10-minute upload as a **3-Act Anthology**:
1. **00:00 - 03:20 (Act 1 - Brand New Lead Story):** Today's main hook matching the Thumbnail & Title (e.g., *Stickman vs Giant Ant*).
   - *Mid-Roll Ad Slot #1 placed cleanly on the Act 2 Chapter Card (`03:20`).*
2. **03:20 - 06:40 (Act 2 - Escalation / Sister Story):** Second mini-episode in the same universe.
   - *Mid-Roll Ad Slot #2 placed cleanly on the Act 3 Chapter Card (`06:40`).*
3. **06:40 - 10:05 (Act 3 - Finale & Cliffhanger):** Third mini-episode ending on a cliffhanger to drive binge-watching to the next video.

## 4. Quick Commands
```powershell
# Open live interactive Studio preview
npm run dev

# Export US YouTube Thumbnail (1280x720 PNG)
npx remotion still Thumbnail-US out/thumbnail.png

# Export Pilot Episode (1080p MP4)
npx remotion render Episode01-Pilot out/episode01-pilot.mp4

# Export Full 10-Minute Episode (1080p MP4)
npx remotion render Episode-10Min-Daily out/daily-10min.mp4
```
