import html
import os
import sys
import numpy as np
from PIL import Image


def main():
    default_input_path = os.path.join("assets", "source", "source-prepped.png")
    default_output_path = os.path.join("assets", "generated", "avi-ascii.svg")

    input_path = sys.argv[1] if len(sys.argv) > 1 else default_input_path
    output_path = sys.argv[2] if len(sys.argv) > 2 else default_output_path

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Loading prepped image from '{input_path}'...")
    try:
        img = Image.open(input_path).convert("L")
    except Exception as e:
        print(f"Error loading image '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)

    img_w, img_h = img.size
    print(f"Original image size: {img_w}x{img_h}")

    # Grid configuration
    cols = 100
    char_aspect = 0.5  # character cell width:height ratio
    img_aspect = img_w / img_h
    rows = int(round(cols * char_aspect / img_aspect))
    print(f"Downsampling to grid: {cols} columns x {rows} rows")

    # Downsample image
    img_resized = img.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = np.array(img_resized)

    # Density ramp (bright to dark)
    # Brightness 255 -> index 0 (' ')
    # Brightness 0 -> index 12 ('@')
    ramp = " .`:-=+*cs#%@"
    ramp_len = len(ramp)

    ascii_rows = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            b = pixels[r, c]
            idx = int(round((255 - b) / 255.0 * (ramp_len - 1)))
            idx = max(0, min(idx, ramp_len - 1))
            row_chars.append(ramp[idx])
        ascii_rows.append("".join(row_chars))

    # Dimensions for SVG rendering
    view_width = 370.0
    char_w = view_width / cols
    line_h = char_w / char_aspect
    view_height = round(rows * line_h, 2)
    font_size = round(line_h, 2)

    # Animation timing configuration
    row_delay = 0.04  # Delay (seconds) between row starts
    row_dur = 0.35  # Duration (seconds) for each row's wipe

    # Build SVG content
    svg_lines = []
    svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg_lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_width} {view_height}" '
        f'width="{view_width}" height="{view_height}">'
    )
    svg_lines.append("  <defs>")
    svg_lines.append("    <style>")
    svg_lines.append("      .ascii-text {")
    svg_lines.append('        font-family: Consolas, "Courier New", ui-monospace, monospace;')
    svg_lines.append(f"        font-size: {font_size}px;")
    svg_lines.append("        fill: #c9c9c9;")
    svg_lines.append("        white-space: pre;")
    svg_lines.append("      }")
    svg_lines.append("    </style>")

    # Clip paths for row wipe animations
    for i in range(rows):
        t_start = i * row_delay
        y_pos = round(i * line_h, 2)
        h_val = round(line_h, 2)
        svg_lines.append(f'    <clipPath id="clip-row-{i}">')
        svg_lines.append(f'      <rect x="0" y="{y_pos}" width="0" height="{h_val}">')
        svg_lines.append(
            f'        <animate attributeName="width" from="0" to="{view_width}" '
            f'begin="{t_start:.2f}s" dur="{row_dur:.2f}s" fill="freeze" />'
        )
        svg_lines.append("      </rect>")
        svg_lines.append("    </clipPath>")
    svg_lines.append("  </defs>")

    # Text elements
    svg_lines.append("  <g>")
    for i in range(rows):
        y_baseline = round((i + 0.82) * line_h, 2)
        escaped_text = html.escape(ascii_rows[i])
        svg_lines.append(
            f'    <text xml:space="preserve" x="0" y="{y_baseline}" class="ascii-text" '
            f'textLength="{view_width}" lengthAdjust="spacingAndGlyphs" '
            f'clip-path="url(#clip-row-{i})">{escaped_text}</text>'
        )
    svg_lines.append("  </g>")

    # Riding cursor rects
    svg_lines.append("  <g>")
    cursor_w = round(char_w, 2)
    for i in range(rows):
        t_start = i * row_delay
        y_pos = round(i * line_h, 2)
        h_val = round(line_h, 2)
        svg_lines.append(
            f'    <rect x="0" y="{y_pos}" width="{cursor_w}" height="{h_val}" fill="#c9c9c9" opacity="0">'
        )
        svg_lines.append(
            f'      <animate attributeName="x" from="0" to="{view_width}" '
            f'begin="{t_start:.2f}s" dur="{row_dur:.2f}s" fill="freeze" />'
        )
        svg_lines.append(
            f'      <set attributeName="opacity" to="1" begin="{t_start:.2f}s" dur="{row_dur:.2f}s" />'
        )
        svg_lines.append("    </rect>")
    svg_lines.append("  </g>")

    svg_lines.append("</svg>")

    svg_content = "\n".join(svg_lines) + "\n"

    print(f"Writing SVG to '{output_path}'...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Successfully generated ASCII SVG: {output_path}")


if __name__ == "__main__":
    main()
