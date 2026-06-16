const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const frameDir = "/private/tmp/baby-ai-jobhunter-frames";
const outDir = "/Users/mellisa/Documents/job-hunter/output";
const outVideo = path.join(outDir, "宝宝AI_jobhunter_高级脱敏产品片.mp4");
const width = 1080;
const height = 1920;
const fps = 24;
const duration = 60;
const totalFrames = fps * duration;

async function main() {
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.setContent(`<!doctype html>
    <html>
      <body style="margin:0;background:#000">
        <canvas id="canvas" width="${width}" height="${height}"></canvas>
      </body>
    </html>`);

  await page.exposeFunction("readFrameAsDataUrl", (index) => {
    const framePath = path.join(frameDir, `frame_${String(index).padStart(5, "0")}.png`);
    const bytes = fs.readFileSync(framePath);
    return `data:image/png;base64,${bytes.toString("base64")}`;
  });

  const videoBase64 = await page.evaluate(async ({ fps, totalFrames }) => {
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const videoStream = canvas.captureStream(fps);
    const audioContext = new AudioContext();
    const audioDestination = audioContext.createMediaStreamDestination();
    const master = audioContext.createGain();
    master.gain.value = 0.045;
    master.connect(audioDestination);

    const createTone = (frequency, gainValue) => {
      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();
      oscillator.type = "sine";
      oscillator.frequency.value = frequency;
      gain.gain.value = gainValue;
      oscillator.connect(gain);
      gain.connect(master);
      oscillator.start();
      return { oscillator, gain };
    };

    createTone(55, 0.38);
    createTone(110, 0.16);
    createTone(220, 0.035);

    const stream = new MediaStream([
      ...videoStream.getVideoTracks(),
      ...audioDestination.stream.getAudioTracks(),
    ]);
    const mimeType = MediaRecorder.isTypeSupported("video/mp4")
      ? "video/mp4"
      : MediaRecorder.isTypeSupported("video/webm;codecs=vp9")
      ? "video/webm;codecs=vp9"
      : "video/webm";
    const recorder = new MediaRecorder(stream, {
      mimeType,
      videoBitsPerSecond: 10_000_000,
    });
    const chunks = [];
    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size) chunks.push(event.data);
    };

    const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const drawFrame = async (index) => {
      const dataUrl = await window.readFrameAsDataUrl(index);
      const image = new Image();
      image.src = dataUrl;
      await image.decode();
      ctx.drawImage(image, 0, 0);
    };

    await drawFrame(0);
    recorder.start();

    for (let i = 0; i < totalFrames; i += 1) {
      await drawFrame(i);
      await wait(1000 / fps);
    }

    recorder.stop();
    await new Promise((resolve) => {
      recorder.onstop = resolve;
    });

    const blob = new Blob(chunks, { type: mimeType });
    const arrayBuffer = await blob.arrayBuffer();
    let binary = "";
    const bytes = new Uint8Array(arrayBuffer);
    const chunkSize = 0x8000;
    for (let i = 0; i < bytes.length; i += chunkSize) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
    }
    return btoa(binary);
  }, { fps, totalFrames });

  fs.writeFileSync(outVideo, Buffer.from(videoBase64, "base64"));
  await browser.close();
  console.log(outVideo);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
