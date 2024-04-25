from const import FieldType as f, MAP_SIZE
from utils import build_path

from PIL import Image, ImageDraw

map_colour_alias_to_rgb = {
   "white": (255, 255, 255),
   "red": (255, 0, 0),
   "green": (83, 255, 77),
   "orange": (255, 153, 51),
   "epic": (153, 51, 255),
   "yellow": (255, 255, 0),
   "blue": (133, 179, 255),
   "white": (255, 255, 255),
   "grey": (140, 140, 140),
   "light_yellow": (255, 255, 153),
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
   def __init__(self, background_width, img_dir, output_dir):
      self.bg_w = background_width
      self.img_dir = img_dir
      self.out_dir = output_dir
      
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
         f.demon_head : {"name": "DevilHeadTrap"},  
         f.demon_hands : {"name": "HandTrap"},  
         f.demon_tail : {"name": "TailTrap"},  
         f.spider : {"name": "SpiderTrap"},  
         f.summon_stone : {"name": "Icon9"},  
         f.idle_reward : {"name": "Icon9"},  
         f.amulet_of_fear : {"name": "Icon21"},  
         f.lucky_bones : {"name": "Icon22"},  
         f.scepter_of_domination : {"name": "Icon32"},  
         f.spiral_of_time : {"name": "Icon37"},  
         f.demon_skull : {"name": "Icon40"},  
         f.token_of_memories : {"name": "Icon46"},  
         f.golden_compass : {"name": "Icon48"},  
      }

      images = {}
      for alias, image_config in image_names.items():
         img_name = image_config['name'] + '.png'
         img_path = build_path([self.img_dir], img_name)
         img = Image.open(img_path)
         if alias == 'background':
            img = self.resize(img, None, None, self.bg_w, save_ratio=False)
         else:
            width = self.sizes['cell_width']
            img = self.resize(img, None, width, width, save_ratio=True)

         images[alias] = img

      return images

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
      return [x, y]

   def add_cells(self):
      back = self.images['background']
      for i in range(0, MAP_SIZE[0]):
         for j in range(0, MAP_SIZE[1]):
            coords = self.get_cell_coords(i, j)
            shift = [coords[0]/self.bg_w * 100, coords[1]/self.bg_w * 100]
            add_img(back, self.images['cell'], "TOPLEFT", shift, foregound_on_background=True)

   def render(self, field):
      back = self.images["background"].copy()
      for i in range(0, MAP_SIZE[0]):
         for j in range(0, MAP_SIZE[1]):
            values = field.fields[i][j]
            field_type = values.index(max(values))
            if field_type == f.unknown:
                continue
            img = self.images[f(field_type)]
            coords = self.get_cell_coords(i, j)
            shift = [coords[0]/self.bg_w * 100, coords[1]/self.bg_w * 100]
            add_img(back, img, "TOPLEFT", shift, foregound_on_background=True)

      return back

if __name__ == '__main__':
   render_image = RenderImage(2000, 'img', 'output')
   from field import Field
   from db import Db
   db = Db('db')
   field = Field(db)
   img = render_image.render(field)
   save_path = build_path(['output', 'img'], 'test.png', mkdir=True)
   img.save(save_path)