from ..const import CellType as ct, map_cell_name_to_shortest_alias
import prettytable

class Leaderboard:
   def __init__(self, db_process):
      self.db_process = db_process

   def add_potential_winner(self, winners, user_record):
      key = f'{user_record.x}-{user_record.y}'
      if key not in winners:
         winners[key] = user_record

      if winners[key].time > user_record.time:
         winners[key] = user_record

   def is_artifact(self, cell_type):
      if cell_type in [
         ct.amulet_of_fear, ct.demon_skull, ct.golden_compass, 
         ct.lucky_bones, ct.scepter_of_domination, 
         ct.spiral_of_time, ct.token_of_memories]:
         return True
      return False

   def process_winners(self, winners, map_type):
      score_by_user_id = {}
      map_config = self.db_process.get_map_config(map_type)
      for r in winners.values():
         is_art = self.is_artifact(r.cell_type)
         cell_type_name = r.cell_type.name
         if is_art:
            cell_type_name = 'artifact'
         total_cells = getattr(map_config, cell_type_name, 1)

         score = int( map_type.value ** 2 / total_cells)

         if r.user_id not in score_by_user_id:
            score_by_user_id[r.user_id] = {}

         record = score_by_user_id[r.user_id]
         if 'score' not in record:
            record['score'] = 0
         record['score'] += score

         if cell_type_name not in record:
            record[cell_type_name] = 0
         record[cell_type_name] += 1

      return score_by_user_id

   async def scores_to_table(self, score_by_user_id, ctx):
      col_names = ['user', 'score']
      for x in ct:
         if self.is_artifact(x) or x == ct.empty:
            continue
         col_name = map_cell_name_to_shortest_alias[x.name]
         col_names.append(col_name)
      col_names.append('art')
      
      tabl = prettytable.PrettyTable(col_names)

      for user_id, score_config in score_by_user_id.items():
         user_name = await ctx.bot.get_user_name_by_id(user_id)
         score = score_config['score']
         row = [user_name, score]
         for x in ct:
            if self.is_artifact(x) or x == ct.empty:
               continue
            val = score_config.get(x.name, 0)
            row.append(val)         
         val = score_config.get('artifact', 0)
         row.append(val)
         tabl.add_row(row)

      return tabl
         
   async def show(self, user, view, map_type, ctx):
      user_records = self.db_process.get_user_record_by_map(map_type)
      winners = {}
      for user_record in user_records:
         if user_record.cell_type != view.get_cell_type(user_record.x, user_record.y):
            continue
         self.add_potential_winner(winners, user_record)
      
      score_by_user_id = self.process_winners(winners, map_type)
      tabl = await self.scores_to_table(score_by_user_id, ctx)

      msg = tabl.get_string(sortby="score", reversesort=True)
      msg_arr = msg.split('\n')
      ctx.report.msg.add(msg_arr)