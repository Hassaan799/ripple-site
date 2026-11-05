#!/usr/bin/env python3
"""Build assets/img/ from the app repo's Branding folder.

Resizes the Studio screenshots for the web, blurs the album cover in the Album shot
(album art belongs to its artists and labels), and makes the favicon, touch icon and
share image. Originals are never modified. Run from the site root:
    python3 scripts/make_images.py [path/to/Ripple]
"""
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SITE = Path(__file__).resolve().parent.parent
APP = Path(sys.argv[1]) if len(sys.argv) > 1 else SITE.parent / "Ripple"
SHOTS = APP / "Branding" / "screenshots"
OUT = SITE / "assets" / "img"
WIDTH = 1600
BG = (7, 8, 11)
# Album artwork tile in the 2000 px-wide source screenshot (left, top, right, bottom).
ALBUM_COVER = (215, 225, 830, 840)


def web(image: Image.Image, name: str) -> None:
    image = image.convert("RGB")
    if image.width > WIDTH:
        image = image.resize((WIDTH, round(image.height * WIDTH / image.width)), Image.LANCZOS)
    image.save(OUT / name, "WEBP", quality=82, method=6)


def blurred_album() -> Image.Image:
    shot = Image.open(SHOTS / "studio-album.webp").convert("RGB")
    scale = shot.width / 2000
    box = tuple(round(v * scale) for v in ALBUM_COVER)
    tile = shot.crop(box)
    # Heavy blur plus downsample/upsample so no artwork detail survives.
    small = tile.resize((max(1, tile.width // 24), max(1, tile.height // 24)), Image.BILINEAR)
    tile = small.resize(tile.size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    shot.paste(tile, box[:2])
    return shot


def font(size: int) -> ImageFont.ImageFont:
    for candidate in ["/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Helvetica.ttc"]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def share_image(icon: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", (1200, 630), BG)
    glow = Image.new("L", (1200, 630), 0)
    ImageDraw.Draw(glow).ellipse((250, 120, 950, 760), fill=70)
    canvas.paste(Image.new("RGB", (1200, 630), (90, 96, 104)), (0, 0), glow.filter(ImageFilter.GaussianBlur(120)))
    shot = Image.open(SHOTS / "studio-blob.webp").convert("RGB")
    shot = shot.resize((960, round(shot.height * 960 / shot.width)), Image.LANCZOS)
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *shot.size), radius=28, fill=255)
    canvas.paste(shot, (120, 150), mask)
    canvas.paste(icon.resize((64, 64), Image.LANCZOS), (60, 48), icon.resize((64, 64), Image.LANCZOS))
    ImageDraw.Draw(canvas).text((140, 52), "ripple", font=font(46), fill=(242, 243, 245))
    return canvas


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    web(Image.open(SHOTS / "studio-blob.webp"), "blob.webp")
    web(Image.open(SHOTS / "studio-glass-bars.webp"), "glass-bars.webp")
    web(blurred_album(), "album-blurred.webp")
    shutil.copyfile(APP / "Branding" / "ripple-mark.svg", OUT / "mark.svg")
    icon = Image.open(APP / "Branding" / "Ripple-icon.png").convert("RGBA")
    icon.resize((64, 64), Image.LANCZOS).save(OUT / "favicon.png")
    icon.resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png")
    share_image(icon).save(OUT / "og.png", optimize=True)
    for path in sorted(OUT.iterdir()):
        size = Image.open(path).size if path.suffix != ".svg" else "svg"
        print(f"{path.name}: {size}, {path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
