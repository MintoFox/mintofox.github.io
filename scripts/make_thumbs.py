"""
make_thumbs.py - generates thumbnails for the mintofox.net gallery.

Scans photos/, and for every image that doesn't have a matching
thumbnail in photos/thumbs/, creates one (max 400px wide, JPEG).

Run locally too if you ever want: python scripts/make_thumbs.py
(one-time deps: pip install Pillow)
"""

import os
from PIL import Image

PHOTOS_DIR = "photos"
THUMBS_DIR = os.path.join(PHOTOS_DIR, "thumbs")
MAX_WIDTH = 400
VALID_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".avif"}


def main():
    os.makedirs(THUMBS_DIR, exist_ok=True)
    made, skipped = 0, 0

    for name in sorted(os.listdir(PHOTOS_DIR)):
        src_path = os.path.join(PHOTOS_DIR, name)
        if not os.path.isfile(src_path):
            continue  # skip directories (like thumbs/)
        stem, ext = os.path.splitext(name)
        if ext.lower() not in VALID_EXTS:
            continue

        thumb_name = stem + ".jpg"
        thumb_path = os.path.join(THUMBS_DIR, thumb_name)

        if os.path.exists(thumb_path):
            skipped += 1
            continue  # already have it, don't redo work

        try:
            with Image.open(src_path) as im:
                # JPEG can't store transparency - paste onto black-ish bg
                if im.mode in ("RGBA", "LA", "P"):
                    im = im.convert("RGBA")
                    bg = Image.new("RGBA", im.size, (13, 99, 0, 255))  # minto green :3
                    im = Image.alpha_composite(bg, im).convert("RGB")
                elif im.mode != "RGB":
                    im = im.convert("RGB")

                if im.width > MAX_WIDTH:
                    ratio = MAX_WIDTH / im.width
                    im = im.resize((MAX_WIDTH, round(im.height * ratio)), Image.LANCZOS)

                im.save(thumb_path, "JPEG", quality=82, optimize=True)
                made += 1
                print(f"made  {thumb_name}")
        except Exception as e:
            print(f"FAIL  {name}: {e}")
            skipped += 1

    print(f"\ndone :3  {made} made, {skipped} skipped")


if __name__ == "__main__":
    main()
