from app import db, ma
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


# Define Bracket model
class Bracket(db.Model):
    __tablename__ = 'bracket'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(), db.ForeignKey('user.public_id'),  index=True, unique=True)
    grp_a_1 = db.Column(db.Integer(), nullable=False)
    grp_a_2 = db.Column(db.Integer(), nullable=False)
    grp_b_1 = db.Column(db.Integer(), nullable=False)
    grp_b_2 = db.Column(db.Integer(), nullable=False)
    grp_c_1 = db.Column(db.Integer(), nullable=False)
    grp_c_2 = db.Column(db.Integer(), nullable=False)
    grp_d_1 = db.Column(db.Integer(), nullable=False)
    grp_d_2 = db.Column(db.Integer(), nullable=False)
    grp_e_1 = db.Column(db.Integer(), nullable=False)
    grp_e_2 = db.Column(db.Integer(), nullable=False)
    grp_f_1 = db.Column(db.Integer(), nullable=False)
    grp_f_2 = db.Column(db.Integer(), nullable=False)
    grp_g_1 = db.Column(db.Integer(), nullable=False)
    grp_g_2 = db.Column(db.Integer(), nullable=False)
    grp_h_1 = db.Column(db.Integer(), nullable=False)
    grp_h_2 = db.Column(db.Integer(), nullable=False)
    r16_1 = db.Column(db.Integer(), nullable=True)
    r16_2 = db.Column(db.Integer(), nullable=True)
    r16_3 = db.Column(db.Integer(), nullable=True)
    r16_4 = db.Column(db.Integer(), nullable=True)
    r16_5 = db.Column(db.Integer(), nullable=True)
    r16_6 = db.Column(db.Integer(), nullable=True)
    r16_7 = db.Column(db.Integer(), nullable=True)
    r16_8 = db.Column(db.Integer(), nullable=True)
    r8_1 = db.Column(db.Integer(), nullable=True)
    r8_2 = db.Column(db.Integer(), nullable=True)
    r8_3 = db.Column(db.Integer(), nullable=True)
    r8_4 = db.Column(db.Integer(), nullable=True)
    r4_1 = db.Column(db.Integer(), nullable=True)
    r4_2 = db.Column(db.Integer(), nullable=True)
    r2_1 = db.Column(db.Integer(), nullable=True)
    r2_2 = db.Column(db.Integer(), nullable=True)



# Define BracketSchema
class BracketSchema(ma.ModelSchema):
    class Meta:
        model = Bracket
        ordered = True
