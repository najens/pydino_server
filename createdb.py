#!/usr/bin/env python
from app import db

# Create db tables from sqlalchemy models
db.create_all()
