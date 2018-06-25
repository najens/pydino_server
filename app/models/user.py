from app import db, ma
import uuid
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy_utils import JSONType
from datetime import datetime
from app.models import project
from .bracket import Bracket


# Define User model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(32), server_default='')
    email = db.Column(db.String(32), index=True, unique=True, nullable=False)
    username = db.Column(
        db.String(32), index=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    salt = db.Column(
        db.String(32), nullable=True)
    picture = db.Column(db.String(150), server_default='')
    created_at = db.Column(db.DateTime(), default = datetime.utcnow)
    roles = db.relationship(
        'Role',
        cascade='all,delete',
        secondary='user_roles',
        backref=db.backref('user', lazy='dynamic')
    )
    bracket = db.relationship(
        Bracket,
        cascade='all,delete',
        uselist=False,
        backref=db.backref('user')
    )

    def generate_public_id(self):
        """Generates random public id"""
        self.public_id = str(uuid.uuid4())


# Define OAuth model
class OAuth(db.Model):
    __tablename__ = 'oauth'
    id = db.Column(db.Integer(), primary_key=True)
    provider = db.Column(db.String(50))
    token = db.Column(MutableDict.as_mutable(JSONType))
    provider_uid = db.Column(db.String(120), nullable=False)
    uid = db.Column(db.String(), db.ForeignKey('user.public_id'))
    user = db.relationship('User')
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)


# Define Role model
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    label = db.Column(db.Unicode(255),)


# Define UserRoles model
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(
        db.String(),
        db.ForeignKey('user.public_id', ondelete='CASCADE')
    )
    role_id = db.Column(
        db.Integer(),
        db.ForeignKey('role.id', ondelete='CASCADE')
    )


# Define UserSchema
class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        ordered = True
        exclude = ('id', 'password', 'salt', 'email')

    roles = fields.Nested('RoleSchema', many=True, load=True)


# Define RoleSchema
class RoleSchema(ma.ModelSchema):
    class Meta:
        model = Role


# Define UserRolesSchema
class UserRolesSchema(ma.ModelSchema):
    class Meta:
        model = UserRoles
