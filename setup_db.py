from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('postgresql+psycopg2://andrewraftery:password@127.0.0.1:5432/template1')
session = sessionmaker(bind=engine)()
session.connection().connection.set_isolation_level(0)
session.execute('CREATE DATABASE cs50_project')
session.connection().connection.set_isolation_level(1)