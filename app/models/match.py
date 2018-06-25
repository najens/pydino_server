from app import db, ma
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from .team import Team


# Define Match model
class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer(), primary_key=True)
    match = db.Column(db.Integer(), unique=True, nullable=False)
    team1_id = db.Column(db.Integer(), db.ForeignKey('team.id'))
    team2_id = db.Column(db.Integer(), db.ForeignKey('team.id'))
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    round = db.Column(db.String(32), nullable=False)
    title = db.Column(db.String(32), nullable=False)
    team1_score = db.Column(db.Integer(), default=0)
    team2_score = db.Column(db.Integer(), default=0)
    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])


# Define MatchSchema
class MatchSchema(ma.ModelSchema):
    class Meta:
        model = Match
        ordered = True
