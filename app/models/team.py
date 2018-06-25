from app import db, ma
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


# Define Team model
class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    iso_2 = db.Column(db.CHAR(2), nullable=False)
    group = db.Column(db.CHAR(1), nullable=False)
    MP = db.Column(db.Integer(), default=0)
    W = db.Column(db.Integer(), default=0)
    D = db.Column(db.Integer(), default=0)
    L = db.Column(db.Integer(), default=0)
    GF = db.Column(db.Integer(), default=0)
    GA = db.Column(db.Integer(), default=0)
    GD = db.Column(db.Integer(), default=0)
    Pts = db.Column(db.Integer(), default=0)


# Define TeamSchema
class TeamSchema(ma.ModelSchema):
    class Meta:
        model = Team
        ordered = True
