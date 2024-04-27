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
   r.user_data_changed: "↔️",
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

def number_to_digits(number):
   return [str(x) for x in str(number)]

async def add_emoji(reaction, value, message):
   reactions = [reaction]
   if value > 1:
      reactions += number_to_digits(value) 
   
   for reaction in reactions:
      await message.add_reaction(emoji[reaction])