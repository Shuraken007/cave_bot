from PIL import Image, ImageDraw
import discord
from .color_util import get_brightness
from ..bot.bot_util import pil_image_to_dfile

class RenderTheme:
   def __init__(self, db_process):
      self.db_process = db_process

   def color_from_config(self, color):
      color = color.copy()
      color[-1] = int(color[-1] / 100 * 255)
      return tuple(color)

   def get_colors(self, scheme):
      colors = []
      exclude = ['border', 'text', 'cell']
      for k, v in scheme.__dict__.items():
         if not 'color' in k:
            continue
         is_exclude = False
         for e in exclude:
            if e in k:
               is_exclude = True
               break
         if is_exclude:
            continue
         
         color = self.color_from_config(v)
         if color not in colors:
            colors.append(color)

      colors.sort(key=get_brightness)
      
      return colors
   
   def get_theme_img(self, scheme):
      colors = self.get_colors(scheme)
      w, h = 50, 50
      total_length = len(colors) * w

      bg_color = scheme.background_color.copy()
      bg_color[-1] = 100
      bg_color = self.color_from_config(bg_color)

      img = Image.new('RGBA', (total_length, h), bg_color)
      overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
      draw = ImageDraw.Draw(overlay)

      x, y = 0, 0
      for color in colors:
         draw.rectangle((x, y, x+w, y+h), fill=color, width=1)
         x += w
      
      img = Image.alpha_composite(img, overlay)

      return img

   def render(self, user_id, name, report):
      scheme = self.db_process.search_color_schemes(user_id, name)
      if scheme is None:
         report.err.add('scheme not founded')
         return
      
      img = self.get_theme_img(scheme)
      file = pil_image_to_dfile(img, f'{scheme.name}.png')
      embed = discord.Embed(title=f'{scheme.name}')
      embed.set_image(url=f"attachment://{scheme.name}.png")

      report.embed_and_files.add(embed, file)
