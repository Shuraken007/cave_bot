#!/usr/bin/env python


import math
from PIL import Image

# A map of rgb points in your distribution
# [distance, (r, g, b)]
# distance is percentage from left edge
map_colour_alias_to_rgb = {
   "dark_red": [128, 0, 0, 50],
   "red": [255, 0, 0, 50],
   "orange": [255, 153, 51, 255],
   "dark_yellow": [255, 175, 0, 50],
   "yellow": [255, 255, 0, 50],
   "green": [83, 255, 77, 50],
   "dark_green": [95, 135, 95, 50],
   "medium_green": [95, 175, 95, 50],
   "high_green": [95, 175, 0, 50],
}

heatmap_config = [
    [0.0, 'dark_red'],
    [0.1, 'red'],
    [0.2, 'orange'],
   #  [0.4, 'dark_yellow'],
   #  [0.49, 'yellow'],
    [0.5, 'dark_green'],
    [0.7, 'high_green'],
    [1.0, 'green'],
]

heatmap = []
for config in heatmap_config:
   record = []
   progress, color_name = config
   color = map_colour_alias_to_rgb[color_name]

   record.append(progress)

   norm_color = [ x / 255 for x in color[0:3]]
   record.append(norm_color)

   heatmap.append(record)

def gaussian(x, a, b, c, d=0):
    return a * math.exp(-(x - b)**2 / (2 * c**2)) + d

def get_gradient_color(progres, width):
   width = float(width)
   x = int(progres * width)
   r = sum([gaussian(x, p[1][0], p[0] * width, width/(len(heatmap))) for p in heatmap])
   g = sum([gaussian(x, p[1][1], p[0] * width, width/(len(heatmap))) for p in heatmap])
   b = sum([gaussian(x, p[1][2], p[0] * width, width/(len(heatmap))) for p in heatmap])
   r, g, b = min(1.0, r), min(1.0, g), min(0.2, b)
   r, g, b = [int(256*v) for v in (r, g, b)]
   return [r, g, b]

if __name__ == '__main__':
   width, height = 1000, 200
   im = Image.new('RGB', (width, height))
   ld = im.load()

   for x in range(width):
      r, g, b = get_gradient_color(x / width , width)
      for y in range(im.size[1]):
         ld[x, y] = r, g, b

   im.save('grad.png')