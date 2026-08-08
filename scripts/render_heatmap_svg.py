import datetime
import json
import os
import sys

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def main():
    default_input_path = os.path.join("data", "contributions.json")
    default_output_path = os.path.join("assets", "generated", "contrib-heatmap.svg")

    input_path = sys.argv[1] if len(sys.argv) > 1 else default_input_path
    output_path = sys.argv[2] if len(sys.argv) > 2 else default_output_path

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Loading contribution data from '{input_path}'...")
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON from '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)

    days = data.get("days", [])
    stats = data.get("stats", {})
    total_contribs = stats.get("total", sum(d.get("count", 0) for d in days))

    if not days:
        print("Error: No days found in contribution data.", file=sys.stderr)
        sys.exit(1)

    # Parse and sort days chronologically
    parsed_days = []
    for d in days:
        try:
            dt = datetime.datetime.strptime(d["date"], "%Y-%m-%d")
            parsed_days.append((dt, d))
        except Exception:
            continue

    parsed_days.sort(key=lambda x: x[0])
    if not parsed_days:
        print("Error: Could not parse dates in contribution data.", file=sys.stderr)
        sys.exit(1)

    start_dt = parsed_days[0][0]
    sunday_offset = (start_dt.weekday() + 1) % 7  # Mon=0..Sun=6 -> Sun=0..Sat=6

    # Dimensions
    view_width = 860
    view_height = 196
    bg_fill = "#0d1117"
    border_color = "#2a2a2a"

    # Layout geometry
    x_grid_start = 34
    y_grid_start = 46
    box_size = 12
    box_gap = 3
    box_pitch = box_size + box_gap  # 15px

    # Animation timing configuration
    start_delay = 0.05  # Initial delay before animation starts
    stagger_delay = 0.03  # Stagger delay per diagonal index
    anim_dur = 0.30  # Duration of box slide/fade

    svg_lines = []
    svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg_lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_width} {view_height}" '
        f'width="{view_width}" height="{view_height}">'
    )
    svg_lines.append("  <defs>")
    svg_lines.append("    <style>")
    svg_lines.append("      .label-text {")
    svg_lines.append('        font-family: Consolas, "Courier New", ui-monospace, monospace;')
    svg_lines.append("        font-size: 11px;")
    svg_lines.append("        fill: #8b949e;")
    svg_lines.append("        white-space: pre;")
    svg_lines.append("      }")
    svg_lines.append("      .footer-text {")
    svg_lines.append('        font-family: Consolas, "Courier New", ui-monospace, monospace;')
    svg_lines.append("        font-size: 12px;")
    svg_lines.append("        fill: #8b949e;")
    svg_lines.append("        white-space: pre;")
    svg_lines.append("      }")
    svg_lines.append("    </style>")
    svg_lines.append("  </defs>")

    # Background card panel
    svg_lines.append(
        f'  <rect x="1" y="1" width="{view_width - 2}" height="{view_height - 2}" '
        f'rx="8" ry="8" fill="{bg_fill}" stroke="{border_color}" stroke-width="1.5" />'
    )

    # Day of week labels (Mon, Wed, Fri)
    day_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    svg_lines.append('  <g id="day-labels">')
    for day_row, label_str in day_labels:
        y_pos = y_grid_start + day_row * box_pitch + 9
        svg_lines.append(f'    <text x="8" y="{y_pos}" class="label-text">{label_str}</text>')
    svg_lines.append("  </g>")

    # Month labels
    month_labels = []
    last_month = None
    for dt, d in parsed_days:
        delta_days = (dt - start_dt).days
        adjusted = delta_days + sunday_offset
        week_col = adjusted // 7
        day_row = adjusted % 7
        if dt.month != last_month:
            last_month = dt.month
            month_labels.append((week_col, dt.strftime("%b")))

    svg_lines.append('  <g id="month-labels">')
    for week_col, month_str in month_labels:
        x_pos = x_grid_start + week_col * box_pitch
        svg_lines.append(f'    <text x="{x_pos}" y="34" class="label-text">{month_str}</text>')
    svg_lines.append("  </g>")

    # Contribution Grid Boxes
    svg_lines.append('  <g id="heatmap-boxes">')
    for dt, d in parsed_days:
        delta_days = (dt - start_dt).days
        adjusted = delta_days + sunday_offset
        week_col = adjusted // 7
        day_row = adjusted % 7

        x_pos = x_grid_start + week_col * box_pitch
        final_y = y_grid_start + day_row * box_pitch
        initial_y = final_y - 6

        level = min(max(int(d.get("level", 0)), 0), len(PALETTE) - 1)
        color = PALETTE[level]

        # Diagonal stagger index
        stagger_idx = week_col + day_row
        t_start = start_delay + stagger_idx * stagger_delay

        svg_lines.append(
            f'    <rect x="{x_pos}" y="{initial_y}" width="{box_size}" height="{box_size}" '
            f'rx="2" ry="2" fill="{color}" opacity="0">'
        )
        svg_lines.append(
            f'      <animate attributeName="opacity" from="0" to="1" '
            f'begin="{t_start:.2f}s" dur="{anim_dur:.2f}s" fill="freeze" />'
        )
        svg_lines.append(
            f'      <animate attributeName="y" from="{initial_y}" to="{final_y}" '
            f'begin="{t_start:.2f}s" dur="{anim_dur:.2f}s" fill="freeze" />'
        )
        svg_lines.append("    </rect>")
    svg_lines.append("  </g>")

    # Footer section (Stats text on left, Legend on right)
    svg_lines.append('  <g id="footer">')

    # Stats text
    stats_str = f"{total_contribs} contributions in the last year"
    svg_lines.append(f'    <text x="34" y="172" class="footer-text">{stats_str}</text>')

    # Legend (Less -> More)
    legend_x_start = 705
    legend_y = 162

    svg_lines.append('    <text x="670" y="172" class="label-text">Less</text>')
    for idx, color in enumerate(PALETTE):
        lx = legend_x_start + idx * (box_size + 5)
        svg_lines.append(
            f'    <rect x="{lx}" y="{legend_y}" width="{box_size}" height="{box_size}" '
            f'rx="2" ry="2" fill="{color}" />'
        )
    svg_lines.append('    <text x="795" y="172" class="label-text">More</text>')

    svg_lines.append("  </g>")
    svg_lines.append("</svg>")

    svg_content = "\n".join(svg_lines) + "\n"

    print(f"Writing contribution heatmap SVG to '{output_path}'...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Successfully generated heatmap SVG: {output_path}")


if __name__ == "__main__":
    main()
