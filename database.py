from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a database URL for SQLAlchemy
DATABASE_URL = "postgresql://uxfgsolyzhldptcqama4:WUm45xV9KWJlS8anopxZFiJoyxzMTO@b0b9ufcxpbwb4l1bkueh-postgresql.services.clever-cloud.com:5432/b0b9ufcxpbwb4l1bkueh"
# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False,
bind=engine)

# Create a Base class
Base = declarative_base()
