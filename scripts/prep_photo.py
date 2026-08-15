from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


def remove_background(image: Image.Image) -> Image.Image:
    try:
        from rembg import remove

        return remove(image)
    except Exception:
        return image.convert("RGBA")


def boost_contrast(image: Image.Image) -> Image.Image:
    try:
        import cv2
        import numpy as np

        rgb = np.array(image.convert("RGB"))
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        boosted = cv2.merge((clahe.apply(l_channel), a_channel, b_channel))
        return Image.fromarray(cv2.cvtColor(boosted, cv2.COLOR_LAB2RGB)).convert("RGBA")
    except Exception:
        gray = ImageOps.grayscale(image)
        gray = ImageOps.autocontrast(gray)
        gray = ImageEnhance.Contrast(gray).enhance(1.7)
        return Image.merge("RGBA", (gray, gray, gray, image.getchannel("A")))


def prep_photo(source: Path, output: Path) -> None:
    image = Image.open(source).convert("RGBA")
    image = remove_background(image)
    image = boost_contrast(image)

    white = Image.new("RGBA", image.size, (255, 255, 255, 255))
    white.alpha_composite(image)
    output.parent.mkdir(parents=True, exist_ok=True)
    white.convert("RGB").save(output, quality=95)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a portrait for monochrome ASCII SVG rendering.")
    parser.add_argument("--input", default="assets/profile.jpg", help="Source portrait path.")
    parser.add_argument("--output", default="assets/profile-prepped.jpg", help="Prepared portrait output path.")
    args = parser.parse_args()
    prep_photo(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
