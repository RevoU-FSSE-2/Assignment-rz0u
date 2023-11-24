from db import db
from marshmallow import Schema, fields


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(255), nullable=True)


class UserRegistrationSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    bio = fields.Str(required=False)


class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
