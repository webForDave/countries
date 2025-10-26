import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# --- Configuration ---
CACHE_DIR = "cache"
IMAGE_FILENAME = "summary.png"
IMAGE_PATH = os.path.join(CACHE_DIR, IMAGE_FILENAME)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Use a path to a system font or include one in your project

def format_gdp(gdp_value):
    """Formats a large number into a readable string (e.g., $1.25 Trillion)."""
    if gdp_value is None:
        return 'N/A'
    
    gdp = float(gdp_value)
    
    # Simple formatting logic for readability
    if gdp >= 1e12:
        return f'${gdp / 1e12:,.2f} Trillion'
    elif gdp >= 1e9:
        return f'${gdp / 1e9:,.2f} Billion'
    else:
        return f'${gdp:,.0f}'


def generate_summary_image(total_countries, last_refreshed_at, top_gdp_countries):
    """
    Generates an image summarizing the data and saves it to cache/summary.png.
    """
    
    # 1. Setup Canvas and Fonts
    width, height = 800, 500
    try:
        img = Image.new('RGB', (width, height), color=(240, 248, 255))  # Alice Blue
        d = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            title_font = ImageFont.truetype(FONT_PATH, 30)
            main_font = ImageFont.truetype(FONT_PATH, 18)
            gdp_font = ImageFont.truetype(FONT_PATH, 16)
        except IOError:
            # Fallback if the specific font isn't found
            title_font = ImageFont.load_default()
            main_font = ImageFont.load_default()
            gdp_font = ImageFont.load_default()

        # 2. Draw Text Content
        x_start = 40
        y_pos = 40
        
        # Title
        d.text((x_start, y_pos), "🌍 Global Data Summary", fill=(25, 25, 112), font=title_font)
        y_pos += 60
        
        # Status Info
        d.text((x_start, y_pos), f"Total Countries: {total_countries}", fill=(0, 0, 128), font=main_font)
        y_pos += 30
        
        # Format the timestamp for display
        if isinstance(last_refreshed_at, datetime):
            timestamp_str = last_refreshed_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        else:
            timestamp_str = str(last_refreshed_at)
            
        d.text((x_start, y_pos), f"Last Refreshed: {timestamp_str}", fill=(0, 0, 128), font=main_font)
        y_pos += 50
        
        # Top 5 GDP Section Title
        d.text((x_start, y_pos), "🏆 Top 5 Estimated GDPs (USD Equivalent)", fill=(25, 25, 112), font=main_font)
        y_pos += 30
        
        # List Top Countries
        for i, country in enumerate(top_gdp_countries[:5]):
            name = country.get('name', 'N/A')
            gdp = format_gdp(country.get('estimated_gdp'))

            text_line = f"{(i+1)}. {name} — {gdp}"
            d.text((x_start + 20, y_pos), text_line, fill=(0, 0, 0), font=gdp_font)
            y_pos += 25

        # 3. Save Image
        os.makedirs(CACHE_DIR, exist_ok=True)
        img.save(IMAGE_PATH)
        return True # Success
        
    except Exception as e:
        print(f"Error generating image: {e}")
        return False # Failure