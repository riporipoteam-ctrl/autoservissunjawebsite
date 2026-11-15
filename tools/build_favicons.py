"""Build faithful, compact Šunja favicons from the ORIGINAL shop logo.

This is deliberately a crop of the owner's blue mechanic/gear emblem, not an
AI-redrawn logo or a scaled-down copy of the long horizontal wordmark.

Run:
    python -m pip install Pillow
    python tools/build_favicons.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "sunja-logo-transparent.png"
EXPORTS = (48, 96, 192, 512)


def build_assets(output_dir=ROOT, source_path=SOURCE):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as original:
        source = original.convert("RGBA")
    if source.size != (785, 462):
        raise ValueError(f"Unexpected original logo dimensions: {source.size}")

    # The blue gear, car and mechanic pictogram at the LEFT of the actual
    # original logo. The full 'Šunja Auto Servis' wordmark belongs in the
    # header, not at the 16–48 px sizes used by browser tabs and Google.
    mark = source.crop((37, 135, 225, 326))
    # A high-contrast white square with a restrained blue border remains
    # legible against both light browser tabs and Google's white SERPs.
    master_size = 1024
    canvas = Image.new("RGB", (master_size, master_size), "#ffffff")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (6, 6, master_size - 7, master_size - 7),
        radius=205, fill="#ffffff", outline="#0b5fa5", width=29
    )
    mark = ImageOps.contain(mark, (800, 800), Image.Resampling.LANCZOS)
    mark = mark.filter(ImageFilter.UnsharpMask(radius=1.3, percent=120, threshold=2))
    # Neutralize any transparency in the brand source onto the same white
    # background. Keep the source artwork itself otherwise untouched.
    patch = Image.new("RGBA", mark.size, "#ffffff")
    patch.alpha_composite(mark)
    corner = ((master_size - mark.width) // 2,
              (master_size - mark.height) // 2)
    canvas.paste(patch.convert("RGB"), corner)
    # Pixel-accurate sizes for Google, iOS, Android, and generic browsers.
    for size in EXPORTS:
        icon = canvas.resize((size, size), Image.Resampling.LANCZOS)
        icon.save(output_dir / f"favicon-{size}x{size}.png", "PNG", optimize=True)
    icon180 = canvas.resize((180, 180), Image.Resampling.LANCZOS)
    icon180.save(output_dir / "apple-touch-icon.png", "PNG", optimize=True)
    canvas.save(output_dir / "favicon.ico", "ICO",
                sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    return output_dir


if __name__ == "__main__":
    build_assets()
    print("Generated original-logo favicon.ico, 48/96/192/512 PNG and iOS icon.")
