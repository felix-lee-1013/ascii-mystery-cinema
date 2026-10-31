// ASCII Mystery Cinema Engine
const VIDEO_PLAYLIST = [
  { file: "1004 copy.mp4", title: "1004" },
  { file: "ARMYENGENE copy.mp4", title: "ARMY & ENGENE" },
  { file: "James copy.mp4", title: "James" },
  { file: "Ohm First copy.mp4", title: "Ohm First" },
  { file: "So close to “Say The Name Seven….” 😭 copy.mp4", title: "So close to Say The Name Seventeen" },
  { file: "Spell hhu.mp4", title: "Spell HHU" },
  { file: "Sunghoon copy.mp4", title: "Sunghoon" },
  { file: "howoo copy 2.mp4", title: "Hoshi & Woozi (Howoo)" },
  { file: "i-land 4 copy.mp4", title: "I-LAND 4" },
  { file: "input.mp4", title: "Jungkook (Input)" },
  { file: "jumark copy.mp4", title: "Jumark" }
];

// Rich 22-level density ramp with NO horizontal bars (eliminates scanline stripes!)
const ASCII_CHARS = " .·:;irsXA253hMHGS#9B&@";

// DOM Elements
const video = document.getElementById("videoElement");
const canvas = document.getElementById("asciiCanvas");
const ctx = canvas.getContext("2d", { alpha: false });
const startOverlay = document.getElementById("startOverlay");
const nextBtn = document.getElementById("nextBtn");
const revealBtn = document.getElementById("revealBtn");
const hiddenState = document.getElementById("hiddenState");
const revealedState = document.getElementById("revealedState");
const videoTitleDisplay = document.getElementById("videoTitleDisplay");
const mysterySubtitle = document.getElementById("mysterySubtitle");
const themeGroup = document.getElementById("themeGroup");
const detailSlider = document.getElementById("detailSlider");
const detailVal = document.getElementById("detailVal");
const claritySlider = document.getElementById("claritySlider");
const clarityVal = document.getElementById("clarityVal");
const playPauseBtn = document.getElementById("playPauseBtn");
const muteBtn = document.getElementById("muteBtn");
const volumeSlider = document.getElementById("volumeSlider");
const fullscreenBtn = document.getElementById("fullscreenBtn");
const videoUpload = document.getElementById("videoUpload");

// Offscreen canvas for fast sampling
const offCanvas = document.createElement("canvas");
const offCtx = offCanvas.getContext("2d", { willReadFrequently: true });

// State
let currentVideoIndex = -1;
let currentTheme = "color";
let targetColumns = 180;
let clarityUnderlay = 0.35;
let isPlaying = false;
let isRevealed = false;
let animFrameId = null;

// Initialize
function init() {
  setupEventListeners();
  loadRandomVideo();
}

function loadRandomVideo() {
  let nextIndex;
  do {
    nextIndex = Math.floor(Math.random() * VIDEO_PLAYLIST.length);
  } while (VIDEO_PLAYLIST.length > 1 && nextIndex === currentVideoIndex);

  currentVideoIndex = nextIndex;
  const current = VIDEO_PLAYLIST[currentVideoIndex];

  // Reset Mystery UI
  isRevealed = false;
  hiddenState.style.display = "flex";
  revealedState.style.display = "none";
  mysterySubtitle.innerHTML = `🎲 Mystery Video <span>#${currentVideoIndex + 1}</span>`;
  videoTitleDisplay.textContent = current.title;

  // Load Video source
  video.src = encodeURI(current.file);
  video.load();

  if (isPlaying) {
    video.play().catch(() => {});
  }
}

function setupEventListeners() {
  // Start Overlay (Enables unmuted autoplay on mobile browsers)
  startOverlay.addEventListener("click", () => {
    startOverlay.style.opacity = "0";
    setTimeout(() => startOverlay.style.display = "none", 300);
    video.play().then(() => {
      isPlaying = true;
      playPauseBtn.textContent = "⏸ Pause";
      startRendering();
    }).catch(err => {
      console.log("Autoplay error:", err);
    });
  });

  // Next Video
  nextBtn.addEventListener("click", () => {
    loadRandomVideo();
  });

  // Reveal Answer
  revealBtn.addEventListener("click", () => {
    isRevealed = true;
    hiddenState.style.display = "none";
    revealedState.style.display = "flex";
  });

  // Theme selection
  themeGroup.addEventListener("click", (e) => {
    const pill = e.target.closest(".pill");
    if (!pill) return;
    document.querySelectorAll(".pill").forEach(p => p.classList.remove("active"));
    pill.classList.add("active");
    currentTheme = pill.dataset.theme;
  });

  // Detail Slider
  detailSlider.addEventListener("input", (e) => {
    targetColumns = parseInt(e.target.value, 10);
    const label = targetColumns >= 210 ? "Ultra" : targetColumns >= 150 ? "High" : "Fast";
    detailVal.textContent = `${label} (${targetColumns} cols)`;
  });

  // Clarity Underlay Slider
  claritySlider.addEventListener("input", (e) => {
    clarityUnderlay = parseInt(e.target.value, 10) / 100.0;
    clarityVal.textContent = `${e.target.value}%`;
  });

  // Play / Pause
  playPauseBtn.addEventListener("click", togglePlay);
  canvas.addEventListener("click", togglePlay);

  // Mute / Unmute
  muteBtn.addEventListener("click", () => {
    video.muted = !video.muted;
    muteBtn.textContent = video.muted ? "🔇 Muted" : "🔊 Sound On";
  });

  // Volume slider
  volumeSlider.addEventListener("input", (e) => {
    video.volume = parseFloat(e.target.value);
    video.muted = video.volume === 0;
    muteBtn.textContent = video.muted ? "🔇 Muted" : "🔊 Sound On";
  });

  // Fullscreen
  fullscreenBtn.addEventListener("click", () => {
    const container = document.getElementById("canvasContainer");
    if (!document.fullscreenElement) {
      container.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  });

  // Custom Video Upload from Phone / Computer
  videoUpload.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const fileUrl = URL.createObjectURL(file);
    video.src = fileUrl;
    video.load();

    isRevealed = true;
    hiddenState.style.display = "none";
    revealedState.style.display = "flex";
    mysterySubtitle.innerHTML = `📁 Custom Video`;
    videoTitleDisplay.textContent = file.name;

    video.play().then(() => {
      isPlaying = true;
      playPauseBtn.textContent = "⏸ Pause";
      startOverlay.style.display = "none";
      startRendering();
    });
  });

  video.addEventListener("play", () => {
    isPlaying = true;
    playPauseBtn.textContent = "⏸ Pause";
    startRendering();
  });

  video.addEventListener("pause", () => {
    isPlaying = false;
    playPauseBtn.textContent = "▶ Play";
  });
}

function togglePlay() {
  if (video.paused) {
    video.play();
  } else {
    video.pause();
  }
}

// Rendering Loop
function startRendering() {
  if (animFrameId) cancelAnimationFrame(animFrameId);

  function render() {
    if (!video.paused && !video.ended && video.videoWidth > 0) {
      drawAsciiFrame();
    }
    animFrameId = requestAnimationFrame(render);
  }
  animFrameId = requestAnimationFrame(render);
}

function drawAsciiFrame() {
  const vWidth = video.videoWidth;
  const vHeight = video.videoHeight;
  if (!vWidth || !vHeight) return;

  // Set display canvas resolution matching source aspect ratio
  if (canvas.width !== vWidth || canvas.height !== vHeight) {
    canvas.width = vWidth;
    canvas.height = vHeight;
  }

  // Calculate ASCII grid based on targetColumns
  const cols = targetColumns;
  // Account for character cell aspect ratio (~ 1 : 1.8)
  const cellW = vWidth / cols;
  const cellH = cellW * 1.75;
  const rows = Math.max(1, Math.floor(vHeight / cellH));

  // Downsample frame to character grid for brightness & color sampling
  offCanvas.width = cols;
  offCanvas.height = rows;
  offCtx.drawImage(video, 0, 0, cols, rows);
  const frameData = offCtx.getImageData(0, 0, cols, rows).data;

  // 1. Draw smooth background underlay directly from video
  ctx.globalAlpha = 1.0;
  ctx.fillStyle = "#07090e";
  ctx.fillRect(0, 0, vWidth, vHeight);

  if (clarityUnderlay > 0) {
    ctx.globalAlpha = clarityUnderlay;
    ctx.drawImage(video, 0, 0, vWidth, vHeight);
  }

  // 2. Render ASCII glyphs on top
  ctx.globalAlpha = 1.0;
  const fontSize = Math.max(8, Math.round(cellH * 0.95));
  ctx.font = `bold ${fontSize}px "Fira Code", monospace`;
  ctx.textBaseline = "top";
  ctx.textAlign = "left";

  const numChars = ASCII_CHARS.length;
  const charSpacing = cellW;
  const rowSpacing = cellH;

  for (let r = 0; r < rows; r++) {
    const rowOffset = r * cols * 4;
    const y = r * rowSpacing;

    for (let c = 0; c < cols; c++) {
      const idx = rowOffset + c * 4;
      const red = frameData[idx];
      const green = frameData[idx + 1];
      const blue = frameData[idx + 2];

      // Perceived luminance
      const lum = 0.299 * red + 0.587 * green + 0.114 * blue;
      const charIndex = Math.min(numChars - 1, Math.floor((lum * numChars) / 256));

      // Skip empty space characters to keep background clean
      if (charIndex === 0) continue;

      const char = ASCII_CHARS[charIndex];
      const x = c * charSpacing;

      // Color Themes
      if (currentTheme === "color") {
        ctx.fillStyle = `rgb(${red}, ${green}, ${blue})`;
      } else if (currentTheme === "cyan") {
        ctx.fillStyle = `rgb(190, 235, 255)`;
      } else if (currentTheme === "matrix") {
        ctx.fillStyle = `rgb(57, 255, 20)`;
      } else if (currentTheme === "sunset") {
        ctx.fillStyle = `rgb(255, 42, 133)`;
      }

      ctx.fillText(char, x, y);
    }
  }
}

// Start
window.addEventListener("DOMContentLoaded", init);
