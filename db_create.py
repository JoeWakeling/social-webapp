from config import SQLALCHEMY_DATABASE_URI
from app import db
import os.path

# Create databases and tables
db.create_all()