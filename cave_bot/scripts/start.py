from discord import Intents

from ..bot.bot import MyBot
from ..config import Config

def get_intents():
   intents = Intents.default()
   intents.message_content = True
   intents.members = True
   return intents

def main():
   config = Config()

   intents = get_intents()

   command_prefix='!'

   initial_extensions = ['cave_bot.bot.cogs.super_admin', 'cave_bot.bot.cogs.admin', 'cave_bot.bot.cogs.user']
   bot = MyBot(
      config = config, 
      initial_extensions = initial_extensions, 
      command_prefix=command_prefix, 
      intents=intents
   )
   bot.run()

if __name__ == '__main__':
   main()