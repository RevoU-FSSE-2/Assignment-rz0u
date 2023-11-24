from db import db
from marshmallow import Schema, fields


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(
        db.Integer, db.ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False
    )
    following_id = db.Column(
        db.Integer, db.ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False
    )

    follower = db.relationship(
        "User", foreign_keys=[follower_id], backref=db.backref("followers", lazy=True)
    )
    following = db.relationship(
        "User", foreign_keys=[following_id], backref=db.backref("following", lazy=True)
    )


class FollowSchema(Schema):
    id = fields.Int(dump_only=True)
    follower_id = fields.Int(required=True)
    following_id = fields.Int(required=True)
