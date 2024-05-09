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

# add environment variables
   Add file `.env` near with current README.md
   ```
      # .env
      DISCORD_TOKEN=DSDlsCi...8sl8
      ADMIN_ID=78965132...8599
      ...
   ```
   * DISCORD_TOKEN=DSDlsCi...8sl8
   You should got TOKEN on prev step. 
   * ADMIN_ID=78965132...8599
   id of discord user
   he will become superadmin - can add and remove other admins
   admins can manipulate with other users data - check / remove it
   add / remove bans
   * ALLOWED_CHANNEL_IDS="123...7981,458...2398"
   channels, where bot can send messages
   * SCAN_ALLOWED_CHANNEL_IDS="123...7981,458...2398"
   channels, where bot can scan and parse messages

## database environment
   * first way - user sqlite3 - lightweight db, fastest easiest way
   ```
      DB_DIALECT = "sqlite"
      DB_DIR = "db"
   ```
   where DB_DIR - relative path to folder, where files would store
   "db" - this folder would located near `README`
   * Second way - use postgres. Install postgres server and create user + password,
   see below.
   ```
   DB_DIALECT = "postgresql"
   DB_DRIVER = "psycopg2"
   DB_USERNAME = "jonny"
   DB_PWD = "12345"
   DB_HOST = "localhost"
   DB_PORT = 5632
   ```
   <!-- port not required - optionally -->

# setup project on your system
required: 

   * postgresql if you not selected sqlite3
   [https://www.postgresql.org/download/]
      - ubuntu install: `sudo apt-get install postgresql`
   * python 3.9+
   * poetry - python manager
      https://python-poetry.org/docs/#installing-with-the-official-installer

   * create virtual environment - folder where all libs will loaded locally only for this project `poetry env use python3` - where python3 - your current python alias (python 3.10 as example)
   * install all python packages / dependencies
   `poetry install`

# possible postgress problems on ubuntu
   * if python package psycopg2 failed to install, probably you need `sudo apt-get install libpq-dev`
   * check, that postgress server started:
   `psql`
   * if you see error:
   `error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432`
   then start server manually: `sudo service postgresql start`
      
# work with postgress from command line
   * `sudo -u postgres psql`
      login to postgress shell in admin mode
   * `CREATE USER jonny WITH ENCRYPTED PASSWORD '12345';`
      user + password
   * `ALTER USER jonny CREATEDB;`
      give required permissions, bot created databases himself

# run project & scripts
   * run main.py via poetry: 
   `poetry run python3 src/main.py`
   * drop databases
   `poetry run python3 src/db_drop.py`
   * run tests
   `poetry run pytest`
   * run tests parallel
   `poetry run pytest -n auto`
   * run specific test
   `poetry run pytest -k 'delete'`