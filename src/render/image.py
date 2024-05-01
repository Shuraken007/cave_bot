from const import CellType as ct, MAP_SIZE
from utils import build_path, is_cell_type_mandatory

# from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

color_scheme = {
   ct.unknown              : None,
   ct.empty                : 'brightblue',
   ct.safe                 : 'yellow',
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
   "white": (255, 255, 255, 125),
   "red": (255, 0, 0, 50),
   "green": (83, 255, 77, 50),
   "brightblue": (95, 135, 255, 50),
   "orange": (255, 153, 51, 255),
   "epic": (153, 51, 255, 255),
   "yellow": (255, 255, 0, 50),
   "blue": (133, 179, 255, 50),
   "white": (255, 255, 255, 125),
   "grey": (140, 140, 140, 125),
   "light_yellow": (255, 255, 153, 125),
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
        width = width + int(b_w*shift[0]/100)
        height = height + int(b_w*shift[1]/100)

    background_part = background.crop(
        (width, height, width+foreground.width, height+foreground.height))
    img = None
    if foregound_on_background:
        img = Image.alpha_composite(background_part, foreground)
    else:
        img = Image.alpha_composite(foreground, background_part)
    background.paste(img, (width, height))

class RenderImage():
   def __init__(self, background_width, img_dir, output_dir, font_path):
      self.bg_w = background_width
      self.img_dir = img_dir
      self.out_dir = output_dir
      self.font = ImageFont.truetype(build_path(font_path), 30)

      cell_config = {
         'border_pct': 4,
         'cell_pct' : 10,
      }
      self.sizes = self.get_sizes_spec(cell_config)
      self.images = self.get_common_images()
      self.add_cells()
   #   self.font_storage = FontStorage("{}/Font".format(self.dir))

   def get_common_images(self):
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
      cell_width = self.sizes['cell_width']
      for alias, image_config in image_names.items():
         img_name = image_config['name'] + '.png'
         img_path = build_path([self.img_dir], img_name)
         img = Image.open(img_path)
         if alias == 'background':
            img = self.resize(img, None, None, self.bg_w, save_ratio=False)
         else:
            img = self.resize(img, None, cell_width, cell_width, save_ratio=True)

         images[alias] = img

      images[ct.empty] = Image.new('RGBA', (cell_width, cell_width), (0, 0, 0, 0))
      images[ct.safe] = Image.new('RGBA', (cell_width, cell_width), (0, 0, 0, 0))

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
   
   def get_sizes_spec(self, cell_config):
      border_shift = int(self.bg_w * cell_config['border_pct'] / 100)
      cell_width_with_shift = int((self.bg_w - 2*border_shift) / MAP_SIZE[0])
      cell_shift = int(cell_width_with_shift * cell_config['cell_pct'] / 100)
      cell_width = cell_width_with_shift - cell_shift

      return {
         "border_shift": border_shift,
         "cell_shift": cell_shift,
         "cell_width": cell_width
      }

   def get_cell_coords(self, i, j):
      border_shift = self.sizes['border_shift']
      cell_shift = self.sizes['cell_shift']
      cell_width = self.sizes['cell_width']

      x = border_shift + (cell_width + cell_shift) * i
      y = border_shift + (cell_width + cell_shift) * j
      return [y, x]

   def add_cells(self):
      back = self.images['background']
      for i in range(0, MAP_SIZE[0]):
         for j in range(0, MAP_SIZE[1]):
            coords = self.get_cell_coords(i, j)
            shift = [coords[0]/self.bg_w * 100, coords[1]/self.bg_w * 100]
            add_img(back, self.images['cell'], "TOPLEFT", shift, foregound_on_background=True)

   def add_text(self, img, text_spec, pos_spec):
      coords = pos_spec['coords']
      text = text_spec.get("text")
      width = pos_spec.get('width')
      height = pos_spec.get('height')
      align = pos_spec.get('align')
      color = text_spec.get("color")

      if align is not None:
         if align == 'CENTER' and width is not None:
            (_, _, w, _) = self.font.getbbox(text)
            coords[0] += (width - w) / 2
         if align == 'CENTER' and height is not None:
            (_, h1, _, h2) = self.font.getbbox(text)
            coords[1] += (height - h2) / 2

      img.draw.text(coords, text, font=self.font, fill=color)
      return

   def get_color_by_name(self, color_name, is_bright, cell_type, is_text = False):
      color = list(map_colour_alias_to_rgb[color_name])
      if is_bright and not is_cell_type_mandatory(cell_type):
         color[-1] = is_text and 170 or 125
      return color

   def render(self, user_id, bright, bot, ctx):
      back = self.images["background"].copy()
      back.draw = ImageDraw.Draw(back)
      for i in range(0, MAP_SIZE[0]):
         for j in range(0, MAP_SIZE[1]):
            cell_type = bot.view.get_cell_type(i+1, j+1)

            color_name = None
            if user_id and bot.model.get_user_record(user_id, i+1, j+1) is not None:
               cell_type = ct.empty
               color_name = 'green'

            img = self.images.get(ct(cell_type))
            
            if img and (color_name or ct(cell_type) in color_scheme):
               if not color_name:
                  color_name = color_scheme[ct(cell_type)]
               color = self.get_color_by_name(color_name, bright, cell_type)
               img = img.copy()
               self.change_color(img, (0, 0, 0, 0), color)

            coords = self.get_cell_coords(i, j)
            if img:
               shift = [coords[0]/self.bg_w * 100, coords[1]/self.bg_w * 100]
               add_img(back, img, "TOPLEFT", shift, foregound_on_background=True)

            if cell_type in [ct.unknown, ct.empty, ct.safe ]:
               pos_spec = { 
                  'coords': coords.copy(), 
                  'align': "CENTER",
                  'width': self.sizes['cell_width'],
                  'height': self.sizes['cell_width'],
               }
               color = self.get_color_by_name('grey', bright, cell_type, is_text=True)
               text_spec = { 
                  'text': f'{i+1}-{j+1}',
                  'color': tuple(color)
               }

               self.add_text(back, text_spec, pos_spec)

      return back

if __name__ == '__main__':
   render_image = RenderImage(2000, 'img', 'output', ['font', 'AlegreyaSC-Regular_384.ttf'])
   from view import View
   from model import Model
   db = Model('db')
   view = View(db)
   img = render_image.render(view)
   save_path = build_path(['output', 'img'], 'test.png', mkdir=True)
   img.save(save_path)