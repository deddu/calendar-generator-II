import csv
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import zoneinfo
import holidays

def generate_png_calendar(year):
    year = 2026
    
    # colors
    c_us_holiday = (179, 216, 209, 0)
    c_it_holiday = (149, 191, 191, 0)
    c_weekend = (161, 224, 224, 0)
    
    # resolution settings
    dpi = 96  # Adjust the DPI if needed (72 or 96 are usual screen, 300 for quality print)
    width_mm, height_mm = 1189, 841  # A0 landscape dimensions in mm
    
    # Convert mm to pixels
    dpi_px_ratio = dpi / 25.4
    width_px = int(width_mm * dpi_px_ratio )
    height_px = int(height_mm * dpi_px_ratio)
    
    # we split the width in 33 (31 days + 1 padding on each side)
    day_w_px = int(width_px/33)
    # we split the width in 14 (12 months+ 1 padding on each side)
    day_h_px = int(height_px/14)
    
    
    # font selection. Note that you those scale to match the dpis!
    
    fsL = int(60 / 72 * dpi)
    fsM = int(28 / 72 * dpi)
    fsS = int(22 / 72 * dpi)
    fsXS = int(12/72 * dpi)
    
    f_y =ImageFont.truetype("/Users/dre/Dropbox/design/fonts/Lato/Lato-Black.ttf", fsL)
    f_m =ImageFont.truetype("/Users/dre/Dropbox/design/fonts/Lato/Lato-Regular.ttf", fsM)
    f_dom =ImageFont.truetype("/Users/dre/Dropbox/design/fonts/Lato/Lato-Black.ttf", fsM)
    f_dow =ImageFont.truetype("/Users/dre/Dropbox/design/fonts/Lato/Lato-Hairline.ttf", fsS)
    f_holiday =ImageFont.truetype("/Users/dre/Dropbox/design/fonts/Lato/Lato-Hairline.ttf", fsXS)
    
    
    
    us_holidays = holidays.country_holidays('US')
    it_holidays = holidays.country_holidays('IT')
    
    # daylight time saving
    us_tz= zoneinfo.ZoneInfo('America/Chicago')
    it_tz= zoneinfo.ZoneInfo('Europe/Rome')
    prev_us_dst= us_tz.dst(datetime(year,1,1)) 
    prev_it_dst = it_tz.dst(datetime(year,1,1))
    
    
    
    #Create a blank image with A0 dimensions in landscape
    image = Image.new('RGB', (width_px, height_px), color='white')
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, width_px - 1, height_px - 1], outline="black", width=5)
    
    
    
    # day boxes
    for j in range(0,13):
        for i in range(0,32):
            #date
            try :
                # this will crash and skip the loop for non existing days :) 
                d = datetime(year, j, i)
    
                
                # box
                min_x = i*day_w_px
                max_x = (i+1)*day_w_px
                min_y = j*(day_h_px)
                max_y = (j+1)*day_h_px
    
                # text positions
                d_x = min_x + int(0.35*day_w_px)
                d_y = min_y + int(0.3*day_w_px)
                dow_x = min_x + int(0.35*day_w_px)
                dow_y = min_y + int(0.1*day_w_px)
                h_x = min_x + int(0.1*day_w_px)
                h_y = min_y + int(0.9*day_h_px)
                dst_x = dow_x + int(0.35*day_w_px)
                dst_y = dow_y
                            # Get text content
                day_text = f"{d.day}"
                dow_text = f"{d.strftime('%a')}"
                
                # Calculate bounding box of the text
                bbox_day = draw.textbbox((0, 0), day_text, font=f_dom)
                bbox_dow = draw.textbbox((0, 0), dow_text, font=f_dow)
                
                # Dimensions of the text
                tw_day = bbox_day[2] - bbox_day[0]
                th_day = bbox_day[3] - bbox_day[1]
                
                tw_dow = bbox_dow[2] - bbox_dow[0]
                th_dow = bbox_dow[3] - bbox_dow[1]
                
                # Centered positions within the box
                cx = (min_x + max_x) // 2
                cy = (min_y + max_y) // 2

              
                # if sat or sun or holiday shade bg
                if d in it_holidays:
                    draw.rectangle([min_x, min_y, max_x, max_y], outline="black", fill=c_it_holiday)
                    draw.text((h_x, h_y), f"IT - {it_holidays.get(d)}", fill="black", font=f_holiday, align='left' )
                elif d in us_holidays:
                    draw.rectangle([min_x, min_y, max_x, max_y], outline="black", fill=c_us_holiday)
                    draw.text((h_x, h_y), f"US - {us_holidays.get(d)}", fill="black", font=f_holiday, align='left' )
                elif d.weekday() >= 5:
                    draw.rectangle([min_x, min_y, max_x, max_y], outline="black", fill=c_weekend)
                else:
                    draw.rectangle([min_x, min_y, max_x, max_y], outline="black")
        
        
                # if the timezone changed write so
                curr_us_dst = us_tz.dst(d) 
                curr_it_dst = it_tz.dst(d)
                
                if (curr_us_dst - prev_us_dst) :
                    change_sign ="+1" if (curr_us_dst - prev_us_dst) < timedelta(0) else "-1"
                    draw.text((dst_x, dst_y), f"US - {change_sign}", fill="black", font=f_holiday, align='left' )
                if (curr_it_dst - prev_it_dst) :
                    change_sign ="+1" if (curr_it_dst - prev_it_dst) < timedelta(0) else "-1"
                    draw.text((dst_x, dst_y), f"IT - {change_sign}", fill="black", font=f_holiday, align='left' )
    
                prev_us_dst = curr_us_dst 
                prev_it_dst = curr_it_dst
                
                
                
                draw.text((cx - tw_dow // 2, dow_y), dow_text, fill="black", font=f_dow)
                draw.text((cx - tw_day // 2, d_y), day_text, fill="black", font=f_dom)
        
                # month print
                if i ==  1:
                  draw.text((0.4 * day_w_px, min_y), f"{d.strftime('%b')}", fill="black", font=f_m, align='left')  
            except ValueError:
                pass
    draw.text((day_w_px*.4, day_h_px*0.6), f"{year}", fill="black", font=f_y, align='left')  
    
    
    # Step 4: Save the image
    image.save(f'cal-{year}-{dpi}dpi.png')
    



# Function to generate the calendar for a given year
def generate_csv_calendar(year):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    current_date = start_date
    calendar_data = []

    while current_date <= end_date:
        date_iso = current_date.date().isoformat()
        month = f"{current_date.month:02}"  # format month as 2 digits
        day_of_month = f"{current_date.day:02}"  # format day as 2 digits
        day_of_week_str = current_date.strftime("%a")  # abbreviated weekday name
        day_of_week_int = current_date.weekday()  # 0 is Monday, 6 is Sunday

        # Adjusting to Sunday = 0, Monday = 1, ..., Saturday = 6
        day_of_week_int = (day_of_week_int + 1) % 7

        calendar_data.append([date_iso, month, day_of_month, day_of_week_str, day_of_week_int])

        # Move to the next day
        current_date += timedelta(days=1)

    return calendar_data

# Write the calendar data to a CSV file
def write_calendar_to_csv(year, filename):
    calendar_data = generate_csv_calendar(year)
    headers = ['date', 'month', 'day_of_month', 'day_of_week_str', 'day_of_week_int']

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write the header
        writer.writerows(calendar_data)  # Write the calendar rows

if __name__ == "__main__":
    year=2026
    write_calendar_to_csv(year, f'{year}.csv')
    generate_png_calendar(year)
