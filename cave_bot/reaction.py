import enum

class Reactions(enum.IntEnum):
   fail = 0,
   ok = 1,
   user_data_equal = 2,
   user_data_deleted = 3,
   user_data_new = 4,
   user_data_changed = 5,
   user_data_wrong = 6,
   cell_new = 7,
   cell_update = 8,

r = Reactions

emoji = {
   r.ok: "✅",
   r.fail: "❌",
   r.user_data_equal: "🟰",
   r.user_data_new: "➕",
   r.user_data_changed: "♻️",
   r.user_data_deleted: "➖",
   r.user_data_wrong: "⚠️",
   r.cell_new: "🆕",
   r.cell_update: "🆙",
   "0": "0️⃣",
   "1": "1️⃣",
   "2": "2️⃣",
   "3": "3️⃣",
   "4": "4️⃣",
   "5": "5️⃣",
   "6": "6️⃣",
   "7": "7️⃣",
   "8": "8️⃣",
   "9": "9️⃣",
}

allowed_value = [r.cell_new]

def number_to_digits(number):
   return [str(x) for x in str(number)]

def process_reactions(reactions, report):
   emoji_arr = []
   for reaction, value in reactions.items():
      if reaction not in [r.ok]:
         add_reaction_to_report(reaction, value, report)

      if value > 1 and reaction not in allowed_value:
         value = 1
      
      reaction_emoji_arr = build_emoji_arr(reaction, value)
      emoji_arr.extend(reaction_emoji_arr)

   return emoji_arr

def add_reaction_to_report(reaction, value, report):
   msg = '{} ({}) - {}' \
      .format(emoji[reaction], value, reaction.name)
   report.reaction_msg.add(msg)

def build_emoji_arr(reaction, value):
   reactions = [reaction]
   if value > 1:
      reactions += number_to_digits(value) 
   
   return [emoji[x] for x in reactions]