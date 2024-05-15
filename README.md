# create bot
Create bot in discord with this [instruction](https://discordpy.readthedocs.io/en/stable/discord.html).  
You should get `TOKEN`.
* generate with checkboxes:  
  * bot
    * messages.read  
  * Text Permissions
    * send messages
    * read message history
    * attach files

Invite bot to your server and restrict it to specific channel:
* right click on bot -> Apps -> Manage Integration -> Manage
* block all channels
* add required channel

# Configure environment variables
Add file `.env` near with current README.md
  ```
    # .env
    DISCORD_TOKEN=DSDlsCi...8sl8
    ADMIN_ID=78965132...8599
    ...
  ```
* `DISCORD_TOKEN=DSDlsCi...8sl8`  
  - You should got TOKEN on prev step. 
* `ADMIN_ID=78965132...8599`  
  - Id of discord user, he will become `superadmin`. Highest role, managing other admins, adding them, removing. While `admins` can manipulate with other users data - check / remove it, add / remove bans.
* `ALLOWED_CHANNEL_IDS="123...7981,458...2398"`
  - Channels, where bot can send messages.
* `SCAN_ALLOWED_CHANNEL_IDS="123...7981,458...2398"`
  - channels, where bot can scan and parse messages

## database environment
* select database: sqlite3, postgresql, mysql
* following env variables exists for connecting to db:
```
DB_DIALECT, DB_DRIVER  
DB_USERNAME, DB_PWD, DB_HOST, DB_PORT  
DB_DIR, DB_NAME  
```
Following string for connection would be created

`dialect+driver://user:pwd@host:port/dir/db_name`

### SQLITE3
easiest way - best for running on your own device
```
  DB_DIALECT = "sqlite"  
  DB_DIR = "db"  
  DB_NAME = "bot_cave"  
```
`sqlite3:///db/bot_cave`  
where DB_DIR - relative path to folder, where files would store  
"db" - this folder would located near `README`  
DB_NAME - optional  
### POSTGRES
Install postgres server and create user + password, see below.
```
DB_DIALECT = "postgresql"
DB_DRIVER = "psycopg2"
DB_USERNAME = "jonny"
DB_PWD = "12345"
DB_HOST = "localhost"
DB_PORT = 5632
DB_NAME = "cave3487"
```
- DB_DIR - not defined, cause works only for sqlite3
- DB_PORT - optional
- DB_NAME - optional, by default `cave.db`  
  If db defined, you connect to already existed db.   
  If db not existed - bot try to create it.  
  You must give to user (jonny) ROLE - CREATEDB, or got error about not enough access

### MYSDQL
Same as Postgres, but  
`DB_DIALECT = "mysql"`
# Setup project on your system
required: 
* selected database
  * sqlite3 alredy installed
  * postgres, mysql - google how install server / client
* python 3.9+
* poetry - python manager
  https://python-poetry.org/docs/#installing-with-the-official-installer

* create virtual environment - folder where all libs will loaded locally only for this project `poetry env use python3` - where python3 - your current python alias (python 3.10 as example)
* install all python packages / dependencies
`poetry install`

# run project & scripts
* start bot:  
`poetry run srtar`  
  or  
`poetry run python3 -m src.scripts.start`
* drop tables  
`poetry run drop`  
  or  
`poetry run python3 -m src.scripts.db_drop`  
* run tests  
`poetry run pytest`  
* run tests parallel  
`poetry run pytest -n auto`  
* run specific test  
`poetry run pytest -k 'partial_name_of_test'`  

# Quick Guide Postgres
- [install](https://www.postgresql.org/download/)
- ubuntu install: `sudo apt-get install postgresql`

## Possible postgress problems on ubuntu
* check, that postgress server started:  
`psql`
* if you see error:  
`error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432`  
then start server manually: `sudo service postgresql start`
      
## work with postgress from command line
* `sudo -u postgres psql`  
  login to postgress shell in admin mode  
* `CREATE USER jonny WITH ENCRYPTED PASSWORD '12345';`  
  user + password  
* `ALTER USER jonny CREATEDB;`  
  give required permissions, bot created databases himself  