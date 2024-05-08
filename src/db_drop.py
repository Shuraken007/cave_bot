from db_init import Db
from utils import get_weekly_db_name

if __name__ == '__main__':
   db = Db(const_db_name='const', week_db_name=get_weekly_db_name())
   db.drop_db()
   print('dropped')
