#!/usr/bin/env python3
"""Generate PNG PWA icons from the repository's licensed self-authored SVG assets."""
from pathlib import Path
from PIL import Image
import cairosvg, io

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"assets"
SPECS=[
 ("oaf-app-icon.svg","oaf-app-icon-192.png",192),
 ("oaf-app-icon.svg","oaf-app-icon-512.png",512),
 ("oaf-app-maskable.svg","oaf-app-maskable-512.png",512),
 ("oaf-app-icon.svg","oaf-apple-touch-icon-180.png",180),
]
def main():
    for original,output,size in SPECS:
        png=cairosvg.svg2png(url=str(ASSETS/original),output_width=size,output_height=size)
        im=Image.open(io.BytesIO(png))
        if im.size!=(size,size):
            raise ValueError(f"Invalid icon shape: {output}")
        # Installable icons should not be transparent so the OS never chooses an unwanted background.
        rgba=im.convert("RGBA")
        if rgba.getextrema()[3]!=(255,255):
            raise ValueError(f"Background is transparent: {output}")
        (ASSETS/output).write_bytes(png)
        print(f"{output}: {size} x {size}, {len(png)} bytes")
if __name__=="__main__":
    main()
