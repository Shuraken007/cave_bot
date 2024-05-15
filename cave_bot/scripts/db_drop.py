from ..db_init import Db
from ..model import generate_models, get_table_names
from ..config import Config

def main():
   config = Config()
   table_names = get_table_names()
   models = generate_models(table_names)
   db = Db(models, config.db_connection_str)
   db.drop_tables()
   print('dropped')

if __name__ == '__main__':
   main()