from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, Column, DateTime, BigInteger

from const import CellType

class Week(DeclarativeBase):
    pass

class Const(DeclarativeBase):
    pass

cell_spec = {
   '__tablename__': 'cell',
   'x': Column(Integer, primary_key = True),
   'y': Column(Integer, primary_key = True),   
}
for cell_type in CellType:
   cell_spec[cell_type.name] = Column(Integer, default=0)

Cell = type('Cell', (Week,), cell_spec)

class UserRecord(Week):
   __tablename__ = 'user_record'
   user_id       = Column(BigInteger, primary_key = True)
   x             = Column(Integer, primary_key = True)
   y             = Column(Integer, primary_key = True)
   cell_type     = Column(Integer)

class LastScan(Const):
   __tablename__ = 'last_scan'
   id            = Column(Integer, default = 1, primary_key = True)
   last_scan     = Column(DateTime(timezone=True))

class UserRole(Const): 
   __tablename__ = 'user_role'
   id       = Column(BigInteger, primary_key = True)
   role     = Column(Integer)