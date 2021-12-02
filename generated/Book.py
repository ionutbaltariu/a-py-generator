import sqlalchemy
from db import Base


class Book(Base):
	__tablename__ = 'Books'
	isbn = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
	title = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
	year_of_publishing = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)


