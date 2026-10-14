# Creates colored copies of the orange character image (red, green, ...) next to the original in data\.
# Usage: python scripts\create_character_colors.py

# =========================================
# Imports and defines
# =========================================
from pathlib import Path

from PIL import Image

PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCE_IMAGE = PROJECT_DIR / "data" / "claude_bot.jpg"
NEW_COLORS = {
    "red": (215, 35, 35),
    "green": (40, 175, 70),
}
# Orange has much more red than blue; the gray background and black eyes have about the same of both
ORANGE_RED_MINUS_BLUE = 60

# =========================================
# Classes and functions
# =========================================
def create_character_colors():
    """Saves one recolored PNG per entry in NEW_COLORS, e.g. data\\claude_bot_red.png."""
    for color_name, new_color in NEW_COLORS.items():
        image = Image.open(SOURCE_IMAGE).convert("RGB")
        replace_orange_pixels(image, new_color)
        output_path = SOURCE_IMAGE.with_name(f"{SOURCE_IMAGE.stem}_{color_name}.png")
        image.save(output_path)
        print(f"saved {output_path}")

def replace_orange_pixels(image, new_color):
    """Paints every orange pixel of the image with the new color, in place."""
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            red, green, blue = pixels[x, y]
            if red - blue > ORANGE_RED_MINUS_BLUE:
                pixels[x, y] = new_color

# =========================================
# Main
# =========================================
def main():
    create_character_colors()

if __name__ == "__main__":
    main()
