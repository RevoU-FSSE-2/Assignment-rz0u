from flask import Blueprint, request
from follow.models import Follow
from db import db
import jwt, os
from follow.models import FollowSchema
from marshmallow import ValidationError


follow_bp = Blueprint("follow", __name__)


@follow_bp.route("", methods=["POST"])
def follow():
    data = request.get_json()
    schema = FollowSchema()

    try:
        schema.load(data)
    except ValidationError as err:
        return {"error": err.messages}, 400

    authorization_header = request.headers.get("Authorization")
    print(authorization_header)

    if not authorization_header:
        return {"error": "Not authorized"}, 401

    token = authorization_header.split(" ")[1]

    user_id = jwt.decode(
        token,
        os.getenv("SECRET_KEY"),
        algorithms="HS256",
    )["user_id"]
    print(user_id)

    if data["follower_id"] != user_id:
        return {"error": "Not authorized"}, 401

    if data["follower_id"] == data["following_id"]:
        return {"error": "Cannot follow yourself"}, 400

    if Follow.query.filter_by(
        follower_id=data["follower_id"], following_id=data["following_id"]
    ).first():
        Follow.query.filter_by(
            follower_id=data["follower_id"], following_id=data["following_id"]
        ).delete()
        return {"following_status": "Unfollowed"}

    follow = Follow(follower_id=data["follower_id"], following_id=data["following_id"])

    db.session.add(follow)
    db.session.commit()
    return {"following_status": "Followed"}
