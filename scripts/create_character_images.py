# Creates the character images the window shows (one per entry in COLORS) from data\claude_bot.jpg, with a transparent background.
# Usage: python scripts\create_character_images.py

# =========================================
# Imports and defines
# =========================================
from pathlib import Path
from PIL import Image

PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCE_IMAGE = PROJECT_DIR / "data" / "claude_bot_original.jpg"
COLORS = {
    "orange": (218, 119, 87),
    "red": (215, 35, 35),
    "green": (40, 175, 70),
}
# Orange has much more red than blue; the light background and black eyes have about the same of both
ORANGE_RED_MINUS_BLUE = 60
# The eyes are black; any pixel brighter than this that is not orange is background (including the JPG blur at the edges)
EYES_MAX_BRIGHTNESS = 100

# =========================================
# Classes and functions
# =========================================
def create_character_images():
    """Saves one see-through PNG per entry in COLORS, e.g. data\\claude_bot_red.png."""
    source = Image.open(SOURCE_IMAGE).convert("RGBA")
    for color_name, new_color in COLORS.items():
        image = source.copy()
        paint_character(image, new_color)
        output_path = SOURCE_IMAGE.with_name(f"{SOURCE_IMAGE.stem}_{color_name}.png")
        image.save(output_path)
        print(f"saved {output_path}")

def paint_character(image, new_color):
    """Paints the orange body with the new color, keeps the black eyes and makes everything else transparent, in place."""
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if red - blue > ORANGE_RED_MINUS_BLUE:
                pixels[x, y] = (*new_color, 255)
            elif max(red, green, blue) > EYES_MAX_BRIGHTNESS:
                pixels[x, y] = (0, 0, 0, 0)

# =========================================
# Main
# =========================================
def main():
    create_character_images()

if __name__ == "__main__":
    main()
