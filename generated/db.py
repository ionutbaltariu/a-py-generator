from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
Base = declarative_base()

DB_TYPE = 'mysql+mysqlconnector'
DB_USER = 'user'
DB_USER_PASS = 'pass'
DB_HOST = 'db'
DB_PORT = '3306'
DB_INSTANCE = 'generic_db_name'

connection_string = f"{DB_TYPE}://{DB_USER}:{DB_USER_PASS}@{DB_HOST}:{DB_PORT}/{DB_INSTANCE}"

engine = create_engine(connection_string, echo=True, isolation_level="READ UNCOMMITTED")
Session = sessionmaker()