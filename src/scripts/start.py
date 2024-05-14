from discord import Intents

from ..bot.bot import MyBot
from ..config import Config

def get_intents():
   intents = Intents.default()
   intents.message_content = True
   intents.members = True
   return intents

# @tasks.loop(hours=1)
# async def restart_on_monday():
#    utc = timezone.utc
#    bot.now_day = datetime.now(tz=utc).weekday()

#    if bot.now_day == 0 and bot.prev_day is not None and bot.prev_day == 6:
#       await restart()
#       print('restarted')

   bot.prev_day = bot.now_day

if __name__ == '__main__':
   config = Config()

   intents = get_intents()

   command_prefix='!'

   initial_extensions = ['src.bot.cogs.super_admin', 'src.bot.cogs.admin', 'src.bot.cogs.user']
   # initial_extensions = ['src.bot.cogs.super_admin']
   # initial_extensions = []
   bot = MyBot(
      config = config, 
      initial_extensions = initial_extensions, 
      command_prefix=command_prefix, 
      intents=intents
   )
   bot.run()