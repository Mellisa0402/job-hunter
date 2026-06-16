#!/usr/bin/env python3
"""Extract clean background tiles from the Stardew material contact sheet."""
from PIL import Image
import os

sheet = Image.open('/sessions/determined-awesome-brown/mnt/job-hunter/output/stardew_material_contact_sheet.png')
w, h = sheet.size

# Grid: 4 columns x 6 rows, with ~10px border gaps
# Cols: [10-210], [230-460], [480-710], [730-960]
# Rows: [10-176], [190-392], [406-608], [622-824], [838-1040], [1054-1256]
cols = [(10, 210), (230, 460), (480, 710), (730, 960)]
rows = [(10, 176), (190, 392), (406, 608), (622, 824), (838, 1040), (1054, 1256)]

out_dir = '/sessions/determined-awesome-brown/mnt/job-hunter/output/material_tiles'
os.makedirs(out_dir, exist_ok=True)

for ri, (y1, y2) in enumerate(rows):
    for ci, (x1, x2) in enumerate(cols):
        tile = sheet.crop((x1, y1, x2, y2))
        fname = f'tile_r{ri}_c{ci}.png'
        tile.save(os.path.join(out_dir, fname))
        px = list(tile.getdata())
        avg_r = sum(p[0] for p in px) // len(px)
        avg_g = sum(p[1] for p in px) // len(px)
        avg_b = sum(p[2] for p in px) // len(px)
        print(f'{fname}: {tile.size} avg=({avg_r},{avg_g},{avg_b})')

print(f'\nDone → {out_dir}/')
