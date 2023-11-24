from flask import Blueprint, request
import jwt, os
from auth.models import User
from tweet.models import Tweet
from follow.models import Follow

user_bp = Blueprint("user", __name__)


@user_bp.route("", methods=["GET"])
def profile():
    if not request.headers.get("Authorization"):
        return {"error": "Not authorized"}, 401
    user_id = jwt.decode(
        request.headers.get("Authorization"),
        os.getenv("SECRET_KEY"),
        algorithms="HS256",
    )["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    return {
        "user_id": user.user_id,
        "username": user.username,
        "bio": user.bio,
        "following": Follow.query.filter(user_id == Follow.follower_id).count(),
        "followers": Follow.query.filter(user_id == Follow.following_id).count(),
        "tweets": Tweet.query.filter_by(user_id=user_id)
        .order_by(Tweet.published_at.desc())
        .limit(10)
        .all(),
    }
