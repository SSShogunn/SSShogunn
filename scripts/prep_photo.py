#!/usr/bin/env python3
"""
Prep a photo for ASCII conversion:
  1. Remove the background with rembg so the subject is isolated.
  2. Boost local contrast with OpenCV CLAHE (gives a flat face real
     highlights/shadows).
  3. Composite onto pure white so the background maps to the blank end
     of the ASCII ramp (white -> space).

Output: assets/source-prepped.png (grayscale on white).
Usage: python scripts/prep_photo.py assets/source-photo.jpg
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep(in_path, out_path):
    with open(in_path, "rb") as f:
        input_bytes = f.read()

    # 1. background removal -> RGBA with alpha mask of the subject
    result = remove(input_bytes)
    rgba = Image.open(__import__("io").BytesIO(result)).convert("RGBA")

    # 2. composite onto white using the alpha mask, then grayscale
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("L")

    # 3. CLAHE contrast boost (only really affects the subject; the
    #    background is already flat white so it stays near-white)
    arr = np.array(composited)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(arr)

    # re-flatten background to pure white using the alpha mask so CLAHE
    # noise in flat regions doesn't sprinkle faint specks into the ramp
    alpha = np.array(rgba.split()[-1])
    boosted = np.where(alpha > 10, boosted, 255).astype(np.uint8)

    Image.fromarray(boosted).save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "assets/source-photo.jpg"
    prep(src, "assets/source-prepped.png")
