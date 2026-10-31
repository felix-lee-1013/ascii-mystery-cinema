import random
import signal
from pathlib import Path
import shutil
import subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------- CONFIGURATION ----------------
# Mystery Random Mode: selects a random video each time without telling you which one!
RANDOM_SELECT = True
INPUT_VIDEO = "input.mp4"  # Used only if RANDOM_SELECT = False
OUTPUT_VIDEO = "ascii_hacker_animation.mp4"

OUTPUT_FPS = 30
MAX_COLUMNS = 260     # Ultra high-definition ASCII grid
CELL_WIDTH = 4        # Fine micro-cells for photographic clarity
CELL_HEIGHT = 7

# Rich 22-level density ramp with NO horizontal bar characters (eliminates scanlines!)
ASCII_CHARS = " .·:;irsXA253hMHGS#9B&@"

# Color & Clarity Settings
COLOR_MODE = "color"
CYAN_TINT = (190, 235, 255)  # B, G, R (used if COLOR_MODE == "tint")
COLOR_SATURATION = 1.0       # 1.0 = Natural, true-to-life colors
CONTRAST_BOOST = 1.0         # 1.0 = Natural grading
GLOW_STRENGTH = 0.0          # 0.0 = Crisp characters, no blurry haze
GLOW_BLUR = 2.0

# Video visibility under the ASCII matrix (0.35 = crystal clear faces, contours & text)
BG_UNDERLAY = 0.35
# ------------------------------------------------


def load_monospace_font(size=12):
    """Find a monospace font on Windows, macOS, or Linux."""
    candidates = [
        # Windows
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
        # macOS
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_glyph_atlas(chars, font, cell_w, cell_h):
    """Render each ASCII glyph once centered in its cell without edge padding."""
    atlas = np.zeros((len(chars), cell_h, cell_w), dtype=np.uint8)
    for i, char in enumerate(chars):
        image = Image.new("L", (cell_w, cell_h), 0)
        draw = ImageDraw.Draw(image)
        if hasattr(font, "getbbox"):
            bbox = font.getbbox(char)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            x_off = (cell_w - text_w) // 2 - bbox[0]
            y_off = (cell_h - text_h) // 2 - bbox[1]
        else:
            x_off, y_off = 0, 0

        draw.text((x_off, y_off), char, font=font, fill=255)
        atlas[i] = np.asarray(image)
    return atlas


def choose_video():
    """Find all source videos and pick one at random if enabled."""
    if not RANDOM_SELECT:
        source = Path(INPUT_VIDEO)
        if not source.exists():
            raise FileNotFoundError(f"Cannot find {INPUT_VIDEO!r}.")
        return source, 1

    project_dir = Path(__file__).resolve().parent
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
    ignored_prefixes = ("ascii_", "output_")

    candidates = [
        f for f in project_dir.iterdir()
        if f.is_file()
        and f.suffix.lower() in video_exts
        and not any(f.name.lower().startswith(p) for p in ignored_prefixes)
    ]

    if not candidates:
        raise FileNotFoundError(f"No video files found in {project_dir}")

    chosen = random.choice(candidates)
    return chosen, len(candidates)


def play_video_in_window(video_path, fps, title="ASCII Video Animation", audio_source=None):
    """Loop video playback with synchronized sound; Space pauses/resumes, Q/Esc exits."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Could not open video for playback: {video_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    window_name = title
    paused = False
    frame_delay = max(1, round(1000 / fps))

    # Sound playback using macOS built-in afplay
    audio_proc = None

    def start_audio():
        nonlocal audio_proc
        if audio_source and shutil.which("afplay"):
            try:
                if audio_proc and audio_proc.poll() is None:
                    audio_proc.terminate()
                audio_proc = subprocess.Popen(
                    ["afplay", str(audio_source)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                audio_proc = None

    try:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, width, height)
        start_audio()

        while True:
            if not paused:
                ok, frame = cap.read()
                if not ok:
                    # Loop video and audio
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    start_audio()
                    ok, frame = cap.read()
                if not ok:
                    break
                cv2.imshow(window_name, frame)

            key = cv2.waitKey(0 if paused else frame_delay) & 0xFF
            if key == ord(" "):
                paused = not paused
                if audio_proc and audio_proc.poll() is None:
                    try:
                        sig = signal.SIGSTOP if paused else signal.SIGCONT
                        audio_proc.send_signal(sig)
                    except Exception:
                        pass
            elif key in (ord("q"), 27):
                break
    except cv2.error:
        print("GUI window playback not supported in headless environments.")
    finally:
        if audio_proc and audio_proc.poll() is None:
            try:
                audio_proc.terminate()
                audio_proc.wait(timeout=1.0)
            except Exception:
                pass
        cap.release()
        cv2.destroyAllWindows()


def main():
    source, total_choices = choose_video()
    if RANDOM_SELECT:
        print(f"\n🎲 Mystery Video selected! ({total_choices} videos available in folder)")
        print("❓ Can you guess which video it is from the ASCII art?")
    else:
        print(f"\nLoading video: {source.name}")

    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV could not open: {source.name}")

    raw_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    raw_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Ensure dimensions are even numbers for H.264 / yuv420p compatibility
    width = raw_width - (raw_width % 2)
    height = raw_height - (raw_height % 2)

    source_fps = cap.get(cv2.CAP_PROP_FPS) or OUTPUT_FPS
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Fit ASCII grid strictly inside the target canvas without overflowing
    max_fit_columns = max(10, width // CELL_WIDTH)
    columns = min(MAX_COLUMNS, max_fit_columns)
    rows = max(1, int(round(columns * height / width * CELL_WIDTH / CELL_HEIGHT)))

    # Ensure rendered dimensions never exceed canvas bounds
    if rows * CELL_HEIGHT > height:
        rows = height // CELL_HEIGHT
        columns = max(1, int(round(rows * width / height * CELL_HEIGHT / CELL_WIDTH)))

    font = load_monospace_font(CELL_HEIGHT + 1)
    chars = ASCII_CHARS
    atlas = make_glyph_atlas(chars, font, CELL_WIDTH, CELL_HEIGHT)

    temp_video = Path("ascii_video_silent.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(temp_video), fourcc, OUTPUT_FPS, (width, height))
    if not writer.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        writer = cv2.VideoWriter(str(temp_video), fourcc, OUTPUT_FPS, (width, height))
    if not writer.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        temp_video = Path("ascii_video_silent.avi")
        writer = cv2.VideoWriter(str(temp_video), fourcc, OUTPUT_FPS, (width, height))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError("Could not create the temporary video writer.")

    frame_number = 0
    b, g, r = CYAN_TINT
    tint_vec = np.array([b, g, r], dtype=np.float32)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # Crop to even dimensions if original was odd
        if frame.shape[0] != height or frame.shape[1] != width:
            frame = frame[:height, :width]

        # 1. Grayscale & adaptive contrast (reveals eyes, lips, jawline & fine expressions)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        enhanced_gray = clahe.apply(gray)
        small_gray = cv2.resize(enhanced_gray, (columns, rows), interpolation=cv2.INTER_AREA)

        # 2. Brightness mapping
        indices = np.clip(
            (small_gray.astype(np.uint32) * len(chars)) // 256,
            0,
            len(chars) - 1,
        ).astype(np.uint8)

        # 3. Construct glyph mask
        glyphs = atlas[indices]
        glyph_mask = glyphs.transpose(0, 2, 1, 3).reshape(
            rows * CELL_HEIGHT, columns * CELL_WIDTH
        )
        mask = (glyph_mask.astype(np.float32) / 255.0)[..., np.newaxis]

        # 4. Crisp, natural color sampling with seamless underlay
        if COLOR_MODE == "color":
            color_sample = cv2.resize(
                frame,
                (columns * CELL_WIDTH, rows * CELL_HEIGHT),
                interpolation=cv2.INTER_LINEAR,
            ).astype(np.float32)

            if COLOR_SATURATION != 1.0:
                hsv = cv2.cvtColor(color_sample.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
                hsv[:, :, 1] = np.clip(hsv[:, :, 1] * COLOR_SATURATION, 0, 255)
                color_sample = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)

            # ASCII characters pop as bright highlights; background reveals clear video
            fg = mask * color_sample * 1.15
            bg = (1.0 - mask) * (color_sample * BG_UNDERLAY)
            colored = np.clip(fg + bg, 0, 255).astype(np.uint8)
        else:
            intensity = cv2.resize(
                brightness,
                (columns * CELL_WIDTH, rows * CELL_HEIGHT),
                interpolation=cv2.INTER_NEAREST,
            ).astype(np.float32) / 255.0
            fg = mask * (0.38 + 0.62 * intensity[..., np.newaxis])
            bg = (1.0 - mask) * (BG_UNDERLAY * intensity[..., np.newaxis])
            colored = np.clip((fg + bg) * tint_vec, 0, 255).astype(np.uint8)

        # 6. Optional glow (disabled by default for maximum clarity)
        if GLOW_STRENGTH > 0.0:
            glow = cv2.GaussianBlur(colored, (0, 0), sigmaX=GLOW_BLUR, sigmaY=GLOW_BLUR)
            rendered = cv2.addWeighted(colored, 1.0, glow, GLOW_STRENGTH, 0)
        else:
            rendered = colored

        # 7. Center on canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        rendered_h, rendered_w = rendered.shape[:2]
        x = max(0, (width - rendered_w) // 2)
        y = max(0, (height - rendered_h) // 2)
        canvas[y : y + rendered_h, x : x + rendered_w] = rendered

        writer.write(canvas)
        frame_number += 1

        if frame_number % 30 == 0:
            status = f"{frame_number}/{total_frames}" if total_frames else f"{frame_number}"
            print(f"Processed {status} frames")

    cap.release()
    writer.release()

    # Re-encode with FFmpeg
    playback_video = temp_video
    if shutil.which("ffmpeg"):
        command = [
            "ffmpeg", "-y",
            "-i", str(temp_video),
            "-i", str(source),
            "-map", "0:v:0",
            "-map", "1:a:0?",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            OUTPUT_VIDEO,
        ]
        subprocess.run(command, check=True)
        playback_video = Path(OUTPUT_VIDEO)
        if temp_video.exists():
            temp_video.unlink()  # Clean up temporary silent file
        print(f"\nDone! Saved: {playback_video.resolve()}")
    else:
        print("\nFFmpeg was not found. Outputting silent intermediate video.")

    print("Playing animation with sound. Press Space to pause/resume, Q or Esc to exit.")
    window_title = "ASCII Mystery Video (Guess which one!)" if RANDOM_SELECT else f"ASCII Animation - {source.name}"
    play_video_in_window(playback_video, OUTPUT_FPS, title=window_title, audio_source=source)

    if RANDOM_SELECT:
        print(f"\n🎉 Mystery revealed! The video was: \"{source.name}\"")


if __name__ == "__main__":
    main()