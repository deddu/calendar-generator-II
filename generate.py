"""Generate an A0 calendar PNG (and optionally a CSV) from a TOML config.

Reproduces the old cal.py / cal_nenni.py / school_calendar.py variants:

  python generate.py --start 2026 --prefix cal-                          # full year, IT+US
  python generate.py --start 2026 --prefix nenni-cal- --config it.toml    # IT only
  python generate.py --start 2026-09 --prefix school-cal-                 # school year
"""
import argparse
import csv
import tomllib
from datetime import datetime, timedelta

import holidays
import zoneinfo
from PIL import Image, ImageDraw, ImageFont


def parse_start(s):
    """'2026' -> 2026-01-01, '2026-09' -> 2026-09-01."""
    parts = s.split("-")
    year = int(parts[0])
    month = int(parts[1]) if len(parts) > 1 else 1
    return datetime(year, month, 1)


def month_for_row(start, r):
    """First day of the month at row r (0-indexed) counting from `start`."""
    idx = (start.month - 1) + r
    return datetime(start.year + idx // 12, idx % 12 + 1, 1)


def range_label(start, months):
    """'2026' for a single-calendar-year run, else '2026-2027'."""
    last = month_for_row(start, months - 1)
    return str(start.year) if last.year == start.year else f"{start.year}-{last.year}"


def load_config(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def dashed_rectangle(draw, box, color, width, dash=28, gap=16):
    """Draw a dashed rectangle outline; PIL has no native dashed line."""
    x0, y0, x1, y1 = box
    x = x0
    while x < x1:
        draw.line([(x, y0), (min(x + dash, x1), y0)], fill=color, width=width)
        draw.line([(x, y1), (min(x + dash, x1), y1)], fill=color, width=width)
        x += dash + gap
    y = y0
    while y < y1:
        draw.line([(x0, y), (x0, min(y + dash, y1))], fill=color, width=width)
        draw.line([(x1, y), (x1, min(y + dash, y1))], fill=color, width=width)
        y += dash + gap


def solid_frame(draw, box, color, t):
    """Solid rectangular ring of thickness t inside `box` (4 filled bars)."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y0 + t], fill=color)   # top
    draw.rectangle([x0, y1 - t, x1, y1], fill=color)    # bottom
    draw.rectangle([x0, y0, x0 + t, y1], fill=color)    # left
    draw.rectangle([x1 - t, y0, x1, y1], fill=color)    # right


def wrap_lines(draw, text, font, max_w):
    """Word-wrap `text` into lines no wider than `max_w` pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render(cfg, start, months, prefix):
    dpi = cfg["dpi"]
    width_mm, height_mm = cfg["page_mm"]
    px = dpi / 25.4
    width_px, height_px = int(width_mm * px), int(height_mm * px)
    day_w = int(width_px / 33)
    day_h = int(height_px / 14)

    fdir = cfg["fonts"]["dir"]
    sz = cfg["fonts"]["sizes"]
    fonts = {
        "year":   ImageFont.truetype(f"{fdir}/Lato-Black.ttf",     int(sz["year"]   / 72 * dpi)),
        "month":  ImageFont.truetype(f"{fdir}/Lato-Regular.ttf",   int(sz["month"]  / 72 * dpi)),
        "dom":    ImageFont.truetype(f"{fdir}/Lato-Black.ttf",     int(sz["dom"]    / 72 * dpi)),
        "dow":    ImageFont.truetype(f"{fdir}/Lato-Hairline.ttf",  int(sz["dow"]    / 72 * dpi)),
        "holiday":ImageFont.truetype(f"{fdir}/Lato-Hairline.ttf",  int(sz["holiday"]/ 72 * dpi)),
    }

    countries = cfg["country"]
    hols = [holidays.country_holidays(c["code"]) for c in countries]
    tzs = [zoneinfo.ZoneInfo(c["timezone"]) for c in countries]
    prev_dst = [tz.dst(start) for tz in tzs]
    weekend = tuple(cfg["color"]["weekend"])

    image = Image.new("RGB", (width_px, height_px), color="white")
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline="black", width=5)

    for r in range(months):
        j = r + 1  # row 0 is top padding
        m0 = month_for_row(start, r)
        for i in range(1, 32):
            try:
                d = datetime(m0.year, m0.month, i)
            except ValueError:
                continue

            min_x, max_x = i * day_w, (i + 1) * day_w
            min_y, max_y = j * day_h, (j + 1) * day_h

            # weekend fills the cell; national holidays draw a colored inner
            # frame inset from the cell border (solid IT, dashed US) so they
            # read distinctly from a plain teal weekend. Holiday-on-weekend
            # shows fill + frame.
            if d.weekday() >= 5:
                draw.rectangle([min_x, min_y, max_x, max_y], fill=weekend)
            draw.rectangle([min_x, min_y, max_x, max_y], outline="black", width=2)

            ft = max(2, int(cfg["color"].get("holiday_frame", 0.04) * day_w))
            ins = max(2, int(cfg["color"].get("holiday_inset", 0.05) * day_w))
            fbox = [min_x + ins, min_y + ins, max_x - ins, max_y - ins]
            for style in ("solid", "dashed"):  # solid first, dashed overlaid
                for k, c in enumerate(countries):
                    if c.get("border_style", "solid") != style or not hols[k].get(d):
                        continue
                    color = tuple(c["color"])
                    if style == "dashed":
                        dashed_rectangle(draw, fbox, color, ft)
                    else:
                        solid_frame(draw, fbox, color, ft)

            tx = min_x + int(0.1 * day_w)
            max_w = (max_x - ins - ft - 2) - tx          # fit within the frame hole
            line_h = int(fonts["holiday"].size * 1.15)
            for k, c in enumerate(countries):
                name = hols[k].get(d)
                if not name:
                    continue
                ly = min_y + int((0.70 + k * 0.10) * day_h)
                for ln in wrap_lines(draw, f"{c['prefix']}{name}", fonts["holiday"], max_w):
                    draw.text((tx, ly), ln, fill="black", font=fonts["holiday"], align="left")
                    ly += line_h

            for k, c in enumerate(countries):
                cur = tzs[k].dst(d)
                if cur - prev_dst[k]:
                    sign = "+1" if (cur - prev_dst[k]) < timedelta(0) else "-1"
                    draw.text(
                        (min_x + int(0.7 * day_w), min_y + int((0.22 + k * 0.06) * day_h)),
                        sign, fill="black", font=fonts["holiday"], align="left",
                    )
                prev_dst[k] = cur

            dow_text, day_text = d.strftime("%a"), f"{d.day}"
            tw_dow = draw.textbbox((0, 0), dow_text, font=fonts["dow"])[2]
            tw_day = draw.textbbox((0, 0), day_text, font=fonts["dom"])[2]
            cx = (min_x + max_x) // 2
            draw.text((cx - tw_dow // 2, min_y + int(0.1 * day_w)), dow_text, fill="black", font=fonts["dow"])
            draw.text((cx - tw_day // 2, min_y + int(0.3 * day_w)), day_text, fill="black", font=fonts["dom"])

            if i == 1:
                draw.text((0.4 * day_w, min_y), m0.strftime("%b"), fill="black", font=fonts["month"], align="left")

    label = range_label(start, months)
    draw.text((day_w * 0.4, day_h * 0.6), label, fill="black", font=fonts["year"], align="left")
    out = f"{prefix}{label}-{dpi}dpi.png"
    image.save(out)
    return out


def write_csv(start, months, path):
    nxt = (start.month - 1) + months
    end = datetime(start.year + nxt // 12, nxt % 12 + 1, 1) - timedelta(days=1)
    cur = start
    rows = []
    while cur <= end:
        rows.append([
            cur.date().isoformat(),
            f"{cur.month:02}", f"{cur.day:02}",
            cur.strftime("%a"), (cur.weekday() + 1) % 7,
        ])
        cur += timedelta(days=1)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "month", "day_of_month", "day_of_week_str", "day_of_week_int"])
        w.writerows(rows)


def main():
    p = argparse.ArgumentParser(description="Generate an A0 calendar PNG from a TOML config.")
    p.add_argument("--start", default=str(datetime.now().year),
                   help="start year or year-month, e.g. 2026 or 2026-09 (default: current year)")
    p.add_argument("--months", type=int, default=12, help="months to render (default 12)")
    p.add_argument("--config", default="config.toml", help="path to config.toml")
    p.add_argument("--prefix", default="cal-", help="output filename prefix")
    p.add_argument("--csv", action="store_true", help="also write a CSV of the date range")
    args = p.parse_args()

    cfg = load_config(args.config)
    start = parse_start(args.start)
    out = render(cfg, start, args.months, args.prefix)
    print(f"wrote {out}")
    if args.csv:
        csv_path = f"{args.prefix}{range_label(start, args.months)}.csv"
        write_csv(start, args.months, csv_path)
        print(f"wrote {csv_path}")


if __name__ == "__main__":
    main()
