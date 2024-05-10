from ..db_init import Db
from ..model import generate_models, get_table_names

if __name__ == '__main__':
   table_names = get_table_names()
   models = generate_models(table_names)
   db = Db(models)
   db.drop_tables()
   print('dropped')
