from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID,ARRAY
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database import Base
from sqlalchemy_utils import UUIDType

import uuid
# from uuid import UUID


# Create SQLAlchemy models from the Base class
class User(Base):
 __tablename__ = "users"
 # Create model attributes/columns
 id = Column(Integer, primary_key=True, index=True)
 username = Column(String)
 email = Column(String, unique=True, index=True)
 password = Column(String)
 place=Column(String)

class review(Base):
   __tablename__ ="review_table"
   id = Column(UUID(as_uuid=True), primary_key=True, default =uuid.uuid4)
   url=Column(String)
   username = Column(String)
   data = Column(String)
   status = Column(Integer)


   