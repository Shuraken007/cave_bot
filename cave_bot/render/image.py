from PIL import Image, ImageDraw, ImageFont

from ..const import CellType as ct, \
   cell_max_amount, cell_description, cell_aliases_config, CleanMap, \
   MapType
from ..utils import build_path
from .color_util import is_text_black
from .img_storage import ImageStorage
from ..reaction import Reactions

color_scheme = {
   ct.unknown              : None,
   ct.empty                : 'brightblue',
   ct.demon_hands          : 'red',
   ct.demon_head           : 'red',
   ct.demon_tail           : 'red',
   ct.spider               : 'red',
   ct.idle_reward          : 'blue',
   ct.summon_stone         : 'epic',
   ct.amulet_of_fear       : 'orange',
   ct.demon_skull          : 'orange',
   ct.golden_compass       : 'orange',
   ct.lucky_bones          : 'orange',
   ct.scepter_of_domination: 'orange',
   ct.spiral_of_time       : 'orange',
   ct.token_of_memories    : 'orange',
}

map_colour_alias_to_rgb = {
   "white": [255, 255, 255, 125],
   "black": [0, 0, 0, 125],
   "red": [255, 0, 0, 50],
   "green": [83, 255, 77, 50],
   "brightblue": [95, 135, 255, 50],
   "orange": [255, 153, 51, 255],
   "epic": [153, 51, 255, 255],
   "yellow": [255, 255, 0, 50],
   "blue": [133, 179, 255, 50],
   "white": [255, 255, 255, 125],
   "grey": [140, 140, 140, 125],
   "light_yellow": [255, 255, 153, 125],
}

def add_img(background, foreground, align, shift=None, foregound_on_background=True):
   width, height = None, None
   b_w = background.width
   b_h = background.height
   f_w = foreground.width
   f_h = foreground.height
   if align == "CENTER":
      width = (b_w - f_w) // 2
      height = (b_h - f_h) // 2
   elif align == "CENTERRIGHT":
      width = b_w - f_w
      height = (b_h - f_h) // 2
   elif align == "TOPLEFT":
      width = 0
      height = 0
   elif align == "TOPRIGHT":
      width = b_w-f_w
      height = 0
   if shift:
      width = width + int(shift[0])
      height = height + int(shift[1])

   background_part = background.crop(
      (width, height, width+foreground.width, height+foreground.height))
   img = None
   if foregound_on_background:
      img = Image.alpha_composite(background_part, foreground)
   else:
      img = Image.alpha_composite(foreground, background_part)
   background.paste(img, (width, height))
   img.close()

class ImageCache:
   def __init__(self, map_type, font_descr, font_cell, sizes, images):
      self.map_type = map_type
      self.font_descr = font_descr
      self.font_cell = font_cell
      self.sizes = sizes
      self.images = images

class RenderImage():
   def __init__(self, background_width, img_dir, output_dir, font_path, bot):
      self.bg_w = background_width
      self.img_dir = img_dir
      self.out_dir = output_dir
      self.font_path = font_path

      self.cell_config = {
         'border_pct': 4,
         'cell_pct' : 10,
      }

      self.cache = {}
      self.storage = ImageStorage()
      self.close_cache = []

   def init_cache_by_map_type(self, view):
      map_type = view.map_type
      if map_type in self.cache:
         return
      
      font_size_descr = self.get_font_size_descr(self.bg_w, map_type)
      font_size_cell = self.get_font_size_cell(self.bg_w, map_type)
      font_descr = ImageFont.truetype(build_path(self.font_path), font_size_descr)
      font_cell = ImageFont.truetype(build_path(self.font_path), font_size_cell)

      sizes = self.get_sizes_spec(self.cell_config, map_type)
      images = self.get_common_images(sizes['cell_width'])
      self.add_cells(images, map_type, sizes)
      view.set_update_tracker('image_map')

      self.cache[map_type] = ImageCache(map_type, font_descr, font_cell, sizes, images)
      return self.cache[map_type]
   
   def reset_storage(self):
      self.storage.reset()

   def close_images(self):
      # print(f'closing {len(self.close_cache)} images')
      for img in self.close_cache:
         img.close
      self.close_cache = []

   def get_font_size_descr(self, bg_w, map_type):
      return int(bg_w * (3/200))
   
   def get_font_size_cell(self, bg_w, map_type):
      return int(bg_w * (3/200) * (20 / map_type.value))

   def get_common_images(self, cell_width):
      image_names = {
         'background': {"name": "UI_elements_board_46"},  
         'cell': {"name": "CaveFrameSingle"},  
         ct.demon_head : {"name": "DevilHeadTrap"},  
         ct.demon_hands : {"name": "HandTrap"},  
         ct.demon_tail : {"name": "TailTrap"},  
         ct.spider : {"name": "SpiderTrap"},  
         ct.summon_stone : {"name": "Icon9"},  
         ct.idle_reward : {"name": "IdleRewards"},  
         ct.amulet_of_fear : {"name": "Icon21"},  
         ct.lucky_bones : {"name": "Icon22"},  
         ct.scepter_of_domination : {"name": "Icon32"},  
         ct.spiral_of_time : {"name": "Icon37"},  
         ct.demon_skull : {"name": "Icon40"},  
         ct.token_of_memories : {"name": "Icon46"},  
         ct.golden_compass : {"name": "Icon48"},  
      }

      images = {}
      for alias, image_config in image_names.items():
         img_name = image_config['name'] + '.png'
         img_path = build_path([self.img_dir], img_name)
         img = Image.open(img_path)
         if alias == 'background':
            img = self.resize(img, None, None, self.bg_w, save_ratio=False)
         else:
            img = self.resize(img, None, cell_width, cell_width, save_ratio=True)

         images[alias] = img

      images['blank'] = Image.new('RGBA', (cell_width, cell_width), (0, 0, 0, 0))

      return images

   def change_color(self, img, which, on_what):
      pixdata = img.load()
      for y in range(img.size[1]):
         for x in range(img.size[0]):
               if pixdata[x, y] == (*which,):
                  pixdata[x, y] = (*on_what,)

   def resize(self, img, recommended_w2h, recommended_height, recommended_width=None, save_ratio=True):
      recommended_w2h = recommended_w2h or (img.width / img.height)
      recommended_width = int(
         recommended_width or recommended_height * recommended_w2h)
      recommended_height = int(
         recommended_height or recommended_width / recommended_w2h)
      size = [recommended_width, recommended_height]
      if save_ratio:
         img_w2h = img.width / img.height
         if img_w2h >= recommended_w2h:
               size[1] = int(recommended_width/img_w2h)
         else:
               size[0] = int(recommended_height*img_w2h)

      img = img.resize(size)
      return img
   
   def get_sizes_spec(self, cell_config, map_type):
      border_shift = int(self.bg_w * cell_config['border_pct'] / 100)
      cell_width_with_shift = int((self.bg_w - 2*border_shift) / map_type.value)
      cell_shift = int(cell_width_with_shift * cell_config['cell_pct'] / 100)
      cell_width = cell_width_with_shift - cell_shift

      return {
         "border_shift": border_shift,
         "cell_shift": cell_shift,
         "cell_width": cell_width
      }

   def get_cell_coords(self, i, j, sizes):
      border_shift = sizes['border_shift']
      cell_shift = sizes['cell_shift']
      cell_width = sizes['cell_width']

      x = border_shift + (cell_width + cell_shift) * i
      y = border_shift + (cell_width + cell_shift) * j
      return [y, x]

   def add_cells(self, images, map_type, sizes):
      back = images['background']
      for i in range(0, map_type.value):
         for j in range(0, map_type.value):
            coords = self.get_cell_coords(i, j, sizes)
            add_img(back, images['cell'], "TOPLEFT", coords, foregound_on_background=True)

   def add_text(self, img, text_spec, pos_spec):
      coords = pos_spec['coords']
      text = text_spec.get("text")
      width = pos_spec.get('width')
      height = pos_spec.get('height')
      align = pos_spec.get('align')
      color = text_spec.get("color")
      font = text_spec.get("font")

      (_, _, w, h) = font.getmask(text).getbbox()
      if align is not None:
         if align == 'CENTER' and width is not None:
            coords[0] += int((width - w) / 2)
         if align == 'CENTER' and height is not None:
            coords[1] += int((height) / 2) - h
            pass

      img.draw.text(coords, text, font=font, fill=tuple(color))
      return (w, h)

   def get_text_color(self, img, coords, color_name=None, is_bright=False):
      pixel_color = img.getpixel(tuple(coords))
      if color_name is None:
         color_name = is_text_black(pixel_color) and 'black' or 'grey'
      color = map_colour_alias_to_rgb[color_name].copy()
      if is_bright:
         color[-1] = 170
      return color

   def get_color_by_name(self, color_name, is_bright):
      color = map_colour_alias_to_rgb[color_name].copy()
      if is_bright and color[-1] < 125:
         color[-1] = 125
      return color

   def is_cleaned(self, clean, cell_type):
      if clean >= clean.idle and cell_type in [ct.empty, ct.idle_reward]:
         return True
      
      if clean >= clean.enemy and cell_type in [ct.demon_hands ,ct.demon_head ,ct.demon_tail ,ct.spider]: 
         return True

      if clean >= clean.ss_arts and cell_type in [ct.summon_stone, ct.amulet_of_fear, ct.demon_skull, ct.golden_compass, ct.lucky_bones, ct.scepter_of_domination, ct.spiral_of_time, ct.token_of_memories]: 
         return True
      
      return False
   
   def is_hide_on_clean(self, cell_type):
      if cell_type in [ct.empty, ct.demon_hands ,ct.demon_head ,ct.demon_tail ,ct.spider]:
         return True
      return False

   def get_color_by_cell(self, cell_type, is_bright, is_known, clean):
      color_name = None
      if is_known:
         color_name = 'green'
      elif self.is_cleaned(clean, cell_type):
         if self.is_hide_on_clean(cell_type):
            color_name = None
         else:
            color_name = 'yellow'
      elif clean >= clean.enemy and cell_type == ct.unknown:
         color_name = 'blue'
      else:
         color_name = color_scheme.get(cell_type)

      if not color_name:
         return None

      return self.get_color_by_name(color_name, is_bright)

   def get_img_by_cell(self, cell_type, is_known, clean, images):
      if is_known:
         return images['blank']
      
      if cell_type in [ct.unknown, ct.empty]:
         return images['blank']
      
      if self.is_cleaned(clean, cell_type):
         return images['blank']
     
      return images.get(cell_type)

   def add_img_by_cell(self, coords, img, color, back):
      if not img:
         return
      if color:
         img = img.copy()
         self.change_color(img, (0, 0, 0, 0), color)
         self.close_cache.append(img)
         
      add_img(back, img, "TOPLEFT", coords, foregound_on_background=True)

   def add_text_by_cell(self, text, cell_type, coords, back, bright, map_type):
      if cell_type not in [ct.unknown, ct.empty]:
         return
      
      cache = self.cache[map_type]

      pos_spec = { 
         'coords': coords.copy(), 
         'align': "CENTER",
         'width': cache.sizes['cell_width'],
         'height': cache.sizes['cell_width'],
      }
      shift = cache.sizes['cell_width'] / 2
      pixel_coords = [coords[0] + shift, coords[1] + shift]
      color = self.get_text_color(back, pixel_coords, color_name = None, is_bright=bright)
      text_spec = { 
         'text': text,
         'color': color,
         'font': cache.font_cell
      }

      self.add_text(back, text_spec, pos_spec)

   def generate_map(self, user_id, bright, clean, bot, view, ctx):
      map_type = view.map_type
      cache = self.cache[map_type]

      back = cache.images["background"].copy()
      back.draw = ImageDraw.Draw(back)

      for i in range(0, map_type.value):
         for j in range(0, map_type.value):
            is_known = user_id and bot.db_process.get_user_record(user_id, i+1, j+1, map_type)
            cell_type = view.get_cell_type(i+1, j+1)
            img = self.get_img_by_cell(cell_type, is_known, clean, cache.images)
            color = self.get_color_by_cell(cell_type, bright, is_known, clean)
            coords = self.get_cell_coords(i, j, cache.sizes)
            self.add_img_by_cell(coords, img, color, back)
            self.add_text_by_cell(f'{i+1}-{j+1}', cell_type, coords, back, bright, map_type)

      self.add_descriptions(back, user_id, bot, bright, map_type)
      return back

   def render(self, user_id, bright, clean, bot, ctx):
      map_type = bot.controller.detect_user_map_type(ctx.message.author, ctx)
      if map_type == MapType.unknown:
         ctx.report.reaction.add(Reactions.fail)
         return
      
      view = bot.controller.get_view(map_type)
      self.init_cache_by_map_type(view)

      img, using_save = None, False
      
      is_view_updated = view.get_update_tracker('image_map')
      if is_view_updated:
         view.set_update_tracker('image_map')
         self.storage.reset()

      if not user_id and not is_view_updated:
         img = self.storage.get_image([bright, clean, map_type.name])
         if img:
            using_save = True

      if not img:
         img = self.generate_map(user_id, bright, clean, bot, view, ctx)

      ctx.report.msg.add(f'Map: {map_type.name}')
      ctx.report.image.add(img.copy())
      
      if not using_save and not user_id:
         self.storage.add_image([bright, clean, map_type.name], img)
      elif user_id:
         self.close_cache.append(img)

      self.close_images()

   def get_description_image(self, cell_type_name, is_bright, images):
      cell_type = None
      if cell_type_name == 'artifact':
         img = images[ct.scepter_of_domination]
      elif cell_type_name == 'empty':
         img = images['cell'].copy()
         self.close_cache.append(img)
         color = self.get_color_by_cell(ct.empty, is_bright, False, CleanMap.no_clean)
         self.change_color(img, (0, 0, 0, 0), color)
      else:
         cell_type = ct[cell_type_name]
         img = images.get(cell_type)

      return img

   def get_total_max_amount(self, founded, cell_type_or_name, map_type, bot):
      cell_name = cell_type_or_name
      if type(cell_type_or_name) == ct:
         cell_name = cell_type_or_name.name

      total_from_db = bot.controller.db_process.get_map_max_amount(
         map_type, cell_name)
      if total_from_db is None or total_from_db < founded:
         bot.controller.db_process.set_map_max_amount(
            map_type, cell_name, founded
         )
         total_from_db = founded

      return total_from_db


   def get_description_text(self, cell_type_name, user_id, bot, map_type):
      founded, total, description, name = None, None, None, None
      text = []
      if cell_type_name == 'artifact':

         found_arr = []
         for art in [ct.amulet_of_fear, ct.demon_skull, ct.golden_compass, ct.lucky_bones, ct.scepter_of_domination, ct.spiral_of_time, ct.token_of_memories]:
            found_arr.append(bot.controller.get_total_cells(art, map_type, user_id))
         founded = sum(found_arr)
         
         total = self.get_total_max_amount(founded, cell_type_name, map_type, bot)

         description = cell_description.get(cell_type_name, "")
         name = cell_type_name
      else:
         cell_type = ct[cell_type_name]
         
         founded = bot.controller.get_total_cells(cell_type, map_type, user_id)
         total = self.get_total_max_amount(founded, cell_type_name, map_type, bot)
         description = cell_description.get(cell_type, "")
         name = max(cell_aliases_config[cell_type], key=len)

      msg1 = f'{founded}/{total}'
      msg1_color =  'green' if founded >= total else 'red'
      text.append({'text': msg1.lower(), 'color': msg1_color})

      msg2 = f'  {name}'
      if description:
         msg2 += f'  [{description}]'      
      text.append({'text': msg2.lower()})

      return text

   def add_description_text(self, description_text, coords, back, is_bright, cache):
      icon_width = cache.sizes['cell_width']
      shift = icon_width * 1.2
      coords[0] += shift

      for text_config in description_text:
         text = text_config['text']
         color_name = text_config.get('color', None)

         color = self.get_text_color(back, coords, color_name, is_bright=is_bright)

         pos_spec = { 
            'coords': coords.copy(), 
            'align': "CENTER",
            'height': icon_width
         }
         text_spec = { 
            'text': text,
            'color': color,
            'font': cache.font_descr,
         }

         w, _ = self.add_text(back, text_spec, pos_spec)
         coords[0] += w*1.1

   def add_description(self, cell_type_name, coords, back, user_id, bot, is_bright, map_type):
      cache = self.cache[map_type]

      img = self.get_description_image(cell_type_name, is_bright, cache.images)
      description_text = self.get_description_text(cell_type_name, user_id, bot, map_type)
      add_img(back, img, "TOPLEFT", coords, foregound_on_background=True)
      self.add_description_text(description_text, coords, back, is_bright, cache)
      return cache.sizes['cell_width']

   def add_descriptions(self, back, user_id, bot, is_bright, map_type):
      cache = self.cache[map_type]

      base_coords = self.get_cell_coords(map_type.value, 1, cache.sizes)
      shift = cache.sizes['cell_width']
      base_coords[1] += shift

      coords = base_coords.copy()
      
      for cell_type in [ct.demon_head, ct.demon_tail, ct.demon_hands, ct.spider]:
         shift_y = self.add_description(cell_type.name, coords.copy(), back, user_id, bot, is_bright, map_type)
         coords[1] += shift_y * 1.1

      coords = base_coords.copy()
      coords[0] += int(self.bg_w / 2)

      for cell_type_name in ['artifact', ct.summon_stone.name, ct.idle_reward.name, ct.empty.name]:
         shift_y = self.add_description(cell_type_name, coords.copy(), back, user_id, bot, is_bright, map_type)
         coords[1] += shift_y * 1.1