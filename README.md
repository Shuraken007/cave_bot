# create bot
- create bot in discord with this instruction:
   https://discordpy.readthedocs.io/en/stable/discord.html
   you should get:
      * TOKEN of bot
      * generate with scopes:
         * bot
         * messages.read
      * generate with bot Text Permissions
         * send messages
         * read message history
         * attach files
- invite bot to your server and restrict it to specific channel:
   * right click on bot -> Apps -> Manage Integration -> Manage
   * block all channels
   * add required channel

# add token
   You should got TOKEN on prev step. 
   Also, add user_id for super admin role.
   Add file `.env` near with current README.md
   ```
      # .env
      DISCORD_TOKEN=DSDlsCi...8sl8
      ADMIN_ID=78965132...8599
   ```

# setup project on your system
required: 
   * python 3.9+
   * poetry - python manager
      https://python-poetry.org/docs/#installing-with-the-official-installer

* create virtual environment - folder where all libs will loaded locally only for this project `poetry env use python3` - where python3 - your current python (python 3.10 as example)
* run main.py via poetry: `poetry run python3 src/main.py`