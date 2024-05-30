import sqlalchemy as sa

from ..db_init import Db
from ..model import generate_models, get_table_names
from ..config import Config
from ..utils import build_path

def main():
   config = Config()
   week_postfix, table_names = get_table_names()
   models = generate_models(table_names)

   save_db_dir_path = build_path(['db'], None, mkdir=True)
   db = Db(models, config.db_connection_str)
   print('loaded to memory')

   db_name = week_postfix
   load_engine = sa.create_engine(f"sqlite:///{save_db_dir_path}{db_name}")
   
   db.load_from_one_db_to_another(load_engine, db.load_db)
   print('loaded to remote base')

if __name__ == '__main__':
   main()