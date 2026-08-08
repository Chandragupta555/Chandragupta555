import os
import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main():
    default_input_path = os.path.join("assets", "source", "source-photo.jpg")

    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = default_input_path

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    output_dir = os.path.dirname(input_path) if os.path.dirname(input_path) else os.path.join("assets", "source")
    output_path = os.path.join(output_dir, "source-prepped.png")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading input image from '{input_path}'...")
    try:
        img_input = Image.open(input_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)

    print("Removing background with rembg...")
    img_nobg = remove(img_input)

    print("Compositing subject onto pure white background...")
    background = Image.new("RGBA", img_nobg.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(background, img_nobg)

    print("Converting to grayscale...")
    gray_img = composited.convert("L")
    gray_np = np.array(gray_img)

    print("Applying CLAHE local contrast enhancement...")
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_np = clahe.apply(gray_np)

    print(f"Saving prepped image to '{output_path}'...")
    result_img = Image.fromarray(clahe_np)
    result_img.save(output_path)
    print("Done!")


if __name__ == "__main__":
    main()
