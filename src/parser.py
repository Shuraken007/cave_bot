import re
from const import cell_aliases, MAP_SIZE, CellType as ct
from reaction import Reactions as r
from image_scaner import get_safe_cells, url_to_image
from utils import is_cell_type_mandatory

MATCH_REPORT = re.compile(r"(\d+\-\d+) : ([\w' ]+)")

class Parser:
   def validate_coords(self, coords, report):
      try:
         extracted_coords = coords.split('-')

         if len(extracted_coords) != 2:
            err_msg = f'error: only {len(extracted_coords)} coords {extracted_coords}'
            report.add_error(err_msg)
            report.add_reaction(r.fail)
            return

         x = int(extracted_coords[0])
         y = int(extracted_coords[1])

         if x < 1 or x > MAP_SIZE[0] or y < 1 or y > MAP_SIZE[1]:
            err_msg = f'error: x - {x} or y - {y} failed bounds'
            report.add_error(err_msg)
            report.add_reaction(r.fail)
            return
      
         return [x, y]
      except Exception as e:
         report.add_log({'exception': str(e)})

   def validate_what(self, what, report):
      what = what.lower()
      if not what in cell_aliases:
         err_msg = f'error: unknown "what" {what}'
         report.add_error(err_msg)
         report.add_reaction(r.fail)
         return
      return ct(cell_aliases[what])
   
   def parse_msg(self, ctx, bot):
      arr = ctx.message.content.split("\n")
      i = 1
      for e in arr:
         ctx.report.set_key(f'line {i}')
         i += 1
         if match := MATCH_REPORT.match(e):
            coords = match.group(1)
            what = match.group(2).strip()

            what = self.validate_what(what, ctx.report)
            coords = self.validate_coords(coords, ctx.report)

            if what is None or coords is None:
               continue
            
            bot.controller.add(what, coords, ctx)
         else:
            ctx.report.add_log({'error': f'not match'})

      self.parse_attachments(ctx, bot)

   def parse_attachments(self, ctx, bot):
      attachments = ctx.message.attachments
      if not attachments:
         return
      counter = 0
      for data in attachments:
         counter += 1
         if 'image' not in data.content_type:
            continue
         if not data.url:
            continue
         try:
            ctx.report.set_key(f'parsing attachment {counter}')
            img = url_to_image(data.url)
            safe_cells = get_safe_cells(img, ctx.report)
            self.add_safe_cells(safe_cells, counter, ctx, bot)
         except Exception as e:
            print(e)
            ctx.report.add_log({f'exception attachment {counter}': str(e)})

   def validate_safe_cells_by_user(self, safe_cells, ctx, bot, user_cell_type_arr):
      for coords in safe_cells:
         cell_type = bot.view.get_cell_type(*coords)
         user_cell_type = bot.model.get_user_record(ctx.message.author.id, *coords)
         user_cell_type_arr.append(user_cell_type)
         if not is_cell_type_mandatory(cell_type):
            continue
         if user_cell_type is not None:
            continue

         msg = f"""{coords} - {cell_type.name} : green on attachmen, but not reported by user, cancel image processing"""
         ctx.report.add_error(msg)
         ctx.report.add_reaction(r.user_data_wrong)
         return False
      
      return True


   def add_safe_cells(self, safe_cells, counter, ctx, bot):
      if not safe_cells or len(safe_cells) < 1:
         return
      user_cell_type_arr = []
      if not self.validate_safe_cells_by_user(safe_cells, ctx, bot, user_cell_type_arr):
         return
      counter = 0
      for coords in safe_cells:
         user_cell_type = user_cell_type_arr[counter]
         if user_cell_type is None:
            bot.controller.add(ct.safe, coords, ctx)
         counter += 1