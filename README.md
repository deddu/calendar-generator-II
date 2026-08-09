# calendar

Generates an A0 landscape calendar as a PNG (and optionally a CSV of the date
range) from a TOML config. One month per row, days 1–31 as columns, with
national holidays and daylight-saving transitions marked for one or more
countries.

## Install

Requires Python 3.12+ (uses `tomllib`, `zoneinfo`). Runtime deps are just
`pillow` and `holidays`.

```bash
uv sync          # creates the venv and installs deps from uv.lock
```

Fonts are loaded from `[fonts].dir` in the config — point it at a directory
holding the Lato family (`Lato-Black.ttf`, `Lato-Regular.ttf`,
`Lato-Hairline.ttf`).

## Usage

```bash
uv run python generate.py --start 2026                  # full calendar year
uv run python generate.py --start 2026-09               # a 12-month run from Sept
uv run python generate.py --start 2026-09 --prefix school-cal-
uv run python generate.py --start 2026 --csv            # also write the date-range CSV
uv run python generate.py --start 2026-09 --months 10   # fewer months
uv run python generate.py --start 2026 --config it.toml # different config
```

### Flags

| flag       | default        | meaning                                                            |
|------------|----------------|--------------------------------------------------------------------|
| `--start`  | current year   | start as `YYYY` (= Jan 1) or `YYYY-MM` (= day 1 of that month)     |
| `--months` | `12`           | number of months to render                                         |
| `--config` | `config.toml`  | path to a TOML config                                              |
| `--prefix` | `cal-`         | output filename prefix; PNG is `<prefix><label>-<dpi>dpi.png`      |
| `--csv`    | off            | also write `<prefix><label>.csv`                                   |

The **label** is the start year for a single-calendar-year run, or
`start-end` (e.g. `2026-2027`) when the run crosses a New Year.

## Reproducing the old variants

The previous standalone scripts are now flag combinations:

| old script           | command                                                              |
|----------------------|----------------------------------------------------------------------|
| `cal.py`             | `generate.py --start 2026 --prefix cal-`                             |
| `school_calendar.py` | `generate.py --start 2026-09 --prefix school-cal-`                   |
| `cal_nenni.py`       | `generate.py --start 2026 --prefix nenni-cal- --config it.toml`      |

`it.toml` is just `config.toml` with the `[[country]]` block for `US` removed.

## Config

`config.toml`:

```toml
dpi = 300                          # 72/96 screen, 300 print
page_mm = [1189, 841]              # A0 landscape, [width, height]

[fonts]
dir = "/path/to/fonts/Lato"
sizes = { year = 60, month = 28, dom = 28, dow = 22, holiday = 12 }

[color]
weekend = [161, 224, 224]           # cell fill for Sat/Sun
holiday_frame = 0.04               # inner frame thickness, fraction of cell width
holiday_inset = 0.05               # gap between cell border and the holiday frame

[[country]]
code = "IT"
timezone = "Europe/Rome"
color = [149, 191, 191]
prefix = ""                        # text prefix before the holiday name
border_style = "solid"             # "solid" or "dashed"

[[country]]
code = "US"
timezone = "America/Chicago"
color = [179, 216, 209]
prefix = "US - "
border_style = "dashed"
```

### Holidays

Each `[[country]]` entry drives both the holiday shading and the DST markers
for that country. Holidays are shown as a **colored inner frame** inset from
the cell border — `solid` for the first country, `dashed` for others — so two
holidays on the same day both stay visible (solid drawn first, dashed
overlaid). The holiday name is word-wrapped to fit inside the frame hole and
never overflows the cell.

### Daylight saving

DST transitions are detected per country timezone and marked with a `+1` /
`-1` annotation inside the cell.

## Output

- PNG: A0 landscape at `[dpi]`, named `<prefix><label>-<dpi>dpi.png`.
- CSV (with `--csv`): columns `date, month, day_of_month, day_of_week_str,
  day_of_week_int` (Sunday = 0 … Saturday = 6).

## Tests

```bash
uv run python test_calendar.py
```

Plain-`assert` self-checks for the date logic (`parse_start`, `month_for_row`,
`range_label`). No framework.
