"""Re-encode the original Auto Servis Šunja intro MP4 without changing its design.

Use: python tools/build_intro_animation.py
Requires ffmpeg and Pillow>=12.0. Video is kept untouched; the new WebP
samples its original motion at 30fps, 1.2x speed, for smoother 60/120Hz
display timing than the former 24fps export.
"""
from pathlib import Path
import hashlib
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/video/sunja-logo-intro-user-uploaded-v33.mp4"
DESTINATION = ROOT / "assets/video/sunja-logo-sharp-smooth-v36.webp"
SOURCE_SHA256 = "73e0c3297813c72d219d7770e65f0b3e05f2c1a7fa6dbe96d79378118ba4ac45"
WIDTH, HEIGHT = 910, 512
SOURCE_FRAMES, OUTPUT_FRAMES = 181, 151


def build():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise RuntimeError("Original owner-uploaded MP4 changed; refusing to generate")

    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(SOURCE),
               "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
    video = subprocess.run(command, check=True, stdout=subprocess.PIPE).stdout
    stride = WIDTH * HEIGHT * 3
    if len(video) != SOURCE_FRAMES * stride:
        raise RuntimeError(
            f"Source does not contain exactly {SOURCE_FRAMES} frames at {WIDTH}x{HEIGHT}"
        )

    chosen = []
    for i in range(OUTPUT_FRAMES):
        original_frame = round(i * 1.2)
        pixels = video[original_frame * stride:(original_frame + 1) * stride]
        chosen.append(Image.frombytes("RGB", (WIDTH, HEIGHT), pixels))
    durations = [
        round((i + 1) * 1000 / 30) - round(i * 1000 / 30)
        for i in range(OUTPUT_FRAMES)
    ]
    assert sum(durations) == 5033
    chosen[0].save(DESTINATION, format="WEBP", save_all=True,
                   append_images=chosen[1:], duration=durations, loop=1,
                   quality=93, method=4)

    result = Image.open(DESTINATION)
    assert result.size == (WIDTH, HEIGHT) and result.n_frames >= 125
    total_duration = 0
    for i in range(result.n_frames):
        result.seek(i)
        result.load()
        total_duration += result.info["duration"]
    assert total_duration == 5033
    assert DESTINATION.stat().st_size < 1_500_000
    print("Sharp smooth source-frame logo animation:",
          result.size, result.n_frames, "visible frames,",
          total_duration, "ms,",
          DESTINATION.stat().st_size, "bytes, SHA256",
          hashlib.sha256(DESTINATION.read_bytes()).hexdigest())


if __name__ == "__main__":
    build()
