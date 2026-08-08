import html
import os
import sys


def main():
    default_output_path = os.path.join("assets", "generated", "info-card.svg")
    output_path = sys.argv[1] if len(sys.argv) > 1 else default_output_path

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    is_static = os.environ.get("STATIC") == "1"

    # Dimensions
    view_width = 490
    view_height = 256

    # Colors matching neofetch terminal style
    bg_fill = "#0d1117"
    border_color = "#2a2a2a"
    accent_color = "#6fc3d0"  # Muted teal/blue key color
    text_color = "#c9c9c9"    # Light gray matching ASCII portrait tone
    dim_color = "#8b949e"     # Muted gray for punctuation/bullets
    rule_color = "#30363d"    # Divider line color

    # Lines data definition - each entry animates independently
    lines_data = [
        # Line 0: Title bar
        {
            "elements": [
                f'<text x="24" y="44" class="title-text" xml:space="preserve">'
                f'<tspan fill="{accent_color}">aaditya</tspan>'
                f'<tspan fill="{dim_color}">@</tspan>'
                f'<tspan fill="{accent_color}">github</tspan>'
                f'</text>'
            ],
        },
        # Line 1: Separator rule
        {
            "elements": [
                f'<line x1="24" y1="58" x2="466" y2="58" stroke="{rule_color}" stroke-width="1.5" stroke-dasharray="4 4" />'
            ],
        },
        # Line 2: Now
        {
            "elements": [
                f'<text x="24" y="86" class="body-text" xml:space="preserve">'
                f'<tspan fill="{accent_color}">Now      </tspan>'
                f'<tspan fill="{text_color}">BTech @ PEC Chandigarh · Building for HFT</tspan>'
                f'</text>'
            ],
        },
        # Line 3: Stack
        {
            "elements": [
                f'<text x="24" y="116" class="body-text" xml:space="preserve">'
                f'<tspan fill="{accent_color}">Stack    </tspan>'
                f'<tspan fill="{text_color}">C++ · Python · DSA</tspan>'
                f'</text>'
            ],
        },
        # Line 4: Highlights header
        {
            "elements": [
                f'<text x="24" y="146" class="body-text" xml:space="preserve">'
                f'<tspan fill="{accent_color}">Highlights:</tspan>'
                f'</text>'
            ],
        },
        # Line 5: Highlight item 1
        {
            "elements": [
                f'<text x="24" y="174" class="body-text" xml:space="preserve">'
                f'<tspan fill="{dim_color}">  - </tspan>'
                f'<tspan fill="{text_color}">Low-latency LOB engine (C++)</tspan>'
                f'</text>'
            ],
        },
        # Line 6: Highlight item 2
        {
            "elements": [
                f'<text x="24" y="202" class="body-text" xml:space="preserve">'
                f'<tspan fill="{dim_color}">  - </tspan>'
                f'<tspan fill="{text_color}">Leviathan — portfolio analytics (Python)</tspan>'
                f'</text>'
            ],
        },
        # Line 7: Highlight item 3
        {
            "elements": [
                f'<text x="24" y="230" class="body-text" xml:space="preserve">'
                f'<tspan fill="{dim_color}">  - </tspan>'
                f'<tspan fill="{text_color}">Codeforces CP</tspan>'
                f'</text>'
            ],
        },
    ]

    # Animation timing configuration
    start_delay = 0.10  # Initial delay before first line
    line_stagger = 0.15 # Delay increment per line
    anim_dur = 0.40     # Duration of fade/slide for each line

    svg_lines = []
    svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg_lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_width} {view_height}" '
        f'width="{view_width}" height="{view_height}">'
    )
    svg_lines.append("  <defs>")
    svg_lines.append("    <style>")
    svg_lines.append("      .title-text {")
    svg_lines.append('        font-family: Consolas, "Courier New", ui-monospace, monospace;')
    svg_lines.append("        font-size: 15px;")
    svg_lines.append("        font-weight: bold;")
    svg_lines.append("        white-space: pre;")
    svg_lines.append("      }")
    svg_lines.append("      .body-text {")
    svg_lines.append('        font-family: Consolas, "Courier New", ui-monospace, monospace;')
    svg_lines.append("        font-size: 13.5px;")
    svg_lines.append("        white-space: pre;")
    svg_lines.append("      }")
    svg_lines.append("    </style>")
    svg_lines.append("  </defs>")

    # Terminal card background panel
    svg_lines.append(
        f'  <rect x="1" y="1" width="{view_width - 2}" height="{view_height - 2}" '
        f'rx="8" ry="8" fill="{bg_fill}" stroke="{border_color}" stroke-width="1.5" />'
    )

    # Window control dots (macOS style window buttons)
    svg_lines.append('  <g id="window-controls">')
    svg_lines.append('    <circle cx="24" cy="20" r="5" fill="#ff5f56" />')
    svg_lines.append('    <circle cx="40" cy="20" r="5" fill="#ffbd2e" />')
    svg_lines.append('    <circle cx="56" cy="20" r="5" fill="#27c93f" />')
    svg_lines.append('  </g>')

    # Content lines with optional animation
    svg_lines.append('  <g id="card-content">')
    for i, line in enumerate(lines_data):
        if is_static:
            svg_lines.append("    <g>")
        else:
            t_start = start_delay + i * line_stagger
            svg_lines.append('    <g opacity="0" transform="translate(-10, 0)">')
            svg_lines.append(
                f'      <animate attributeName="opacity" from="0" to="1" '
                f'begin="{t_start:.2f}s" dur="{anim_dur:.2f}s" fill="freeze" />'
            )
            svg_lines.append(
                f'      <animateTransform attributeName="transform" type="translate" '
                f'from="-10 0" to="0 0" begin="{t_start:.2f}s" dur="{anim_dur:.2f}s" fill="freeze" />'
            )

        for elem in line["elements"]:
            svg_lines.append(f"      {elem}")

        svg_lines.append("    </g>")
    svg_lines.append("  </g>")

    svg_lines.append("</svg>")

    svg_content = "\n".join(svg_lines) + "\n"

    print(f"Writing info card SVG to '{output_path}' (STATIC={is_static})...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Successfully generated info card SVG: {output_path}")


if __name__ == "__main__":
    main()
