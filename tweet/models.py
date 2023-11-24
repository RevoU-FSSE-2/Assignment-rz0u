from db import db
from marshmallow import Schema, fields


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    published_at = db.Column(db.DateTime, nullable=False)
    tweet = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    user = db.relationship("User", backref=db.backref("tweets", lazy=True))


class TweetSchema(Schema):
    tweet = fields.Str(required=True)
