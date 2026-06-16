const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");
const { chromium } = require("playwright");

const root = "/Users/mellisa/Documents/job-hunter";
const runtimeNodeModules =
  "/Users/mellisa/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const htmlPath = path.join(root, "docs/baby-ai-jobhunter-apple-film.html");
const frameDir = "/private/tmp/baby-ai-jobhunter-frames";
const outDir = path.join(root, "output");
const outPath = path.join(outDir, "宝宝AI_jobhunter_高级脱敏产品片.mp4");
const ffmpeg = "/Applications/剪映专业版.app/Contents/Resources/ffmpeg";

const width = 1080;
const height = 1920;
const fps = 24;
const duration = 60;
const totalFrames = fps * duration;

function ensureCleanDir(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
}

async function renderFrames() {
  ensureCleanDir(frameDir);
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.goto(`file://${htmlPath}`, { waitUntil: "networkidle" });

  await page.evaluate(() => {
    document.getAnimations().forEach((animation) => animation.pause());
  });

  for (let i = 0; i < totalFrames; i += 1) {
    const ms = (i / fps) * 1000;
    await page.evaluate((time) => {
      document.getAnimations().forEach((animation) => {
        animation.currentTime = time;
      });
    }, ms);

    const framePath = path.join(frameDir, `frame_${String(i).padStart(5, "0")}.png`);
    await page.screenshot({ path: framePath, fullPage: false });

    if (i % 120 === 0) {
      console.log(`rendered ${i}/${totalFrames}`);
    }
  }

  await browser.close();
}

function encodeVideo() {
  const args = [
    "-y",
    "-framerate",
    String(fps),
    "-i",
    path.join(frameDir, "frame_%05d.png"),
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-profile:v",
    "high",
    "-level",
    "4.2",
    "-movflags",
    "+faststart",
    "-r",
    String(fps),
    outPath,
  ];

  const result = spawnSync(ffmpeg, args, { stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`ffmpeg failed with status ${result.status}`);
  }
}

(async () => {
  if (!fs.existsSync(path.join(runtimeNodeModules, "playwright"))) {
    throw new Error("Playwright runtime is missing");
  }
  if (!fs.existsSync(ffmpeg)) {
    throw new Error("ffmpeg is missing");
  }

  await renderFrames();
  encodeVideo();
  console.log(outPath);
})();
