This Python project generates calendar data and visualizations for a specified year (2026 in this code). It consists of two main functionalities:

1. **Generating a CSV Calendar**
   - The code creates a CSV file with each day of the given year.
   - The CSV contains columns:
     - `date` in ISO format (YYYY-MM-DD)
     - `month` as a zero-padded number (01-12)
     - `day_of_month` zero-padded (01-31)
     - `day_of_week_str` abbreviated weekday name (e.g., Mon, Tue)
     - `day_of_week_int` integer representing the day of the week, where Sunday=0, Monday=1, ... Saturday=6.
   - This CSV can be used for general data processing or integration with other tools.

2. **Generating a PNG Image Calendar**
   - Creates a high-resolution A0-sized landscape calendar image with a grid representing months and days.
   - Each month forms a row; each day (1-31) forms columns across the width.
   - Days are rendered in boxes showing day number and day of week.
   - Special highlights:
     - Background shading for U.S. and Italian public holidays (using the `holidays` package).
     - Different colors for weekends.
     - Marks daylight saving time changes for Chicago (US Central Time) and Rome (Italy) with annotations.
   - Uses the Pillow library for image creation and drawing, custom fonts for styling, and `zoneinfo` for timezone/DST awareness.
   - The resulting image is saved as a PNG file named like `cal-2026-96dpi.png`.

**Notable details:**
- Hardcoded year 2026 for generating calendars.
- Uses a relatively high resolution (96 dpi) and very large A0 paper size to generate a detailed calendar image.
- Relies on external fonts located on the user's machine (Lato family in Dropbox).
- The calendar combines US and Italian holidays as examples.
- Includes handling for days that don't exist in each month (skips invalid days).
- Weekend days are shaded differently from weekdays.
- Daylight saving time transitions for US and Italy are indicated visually.

**In summary:**  
This project produces both a detailed CSV file and a high-quality graphical calendar image for a specified year, enriched with holiday markings and daylight saving time annotations for US and Italian time zones. It can serve as a foundation for calendar-based visualizations, print layouts, or further calendar data processing.
