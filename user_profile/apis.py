from flask import Blueprint, request
import jwt, os
from auth.models import User
from tweet.models import Tweet
from follow.models import Follow

user_bp = Blueprint("user", __name__)


@user_bp.route("", methods=["GET"])
def profile():
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        return {"error": "Not authorized"}, 401

    token = authorization_header.split(" ")[1]
    try:
        token_data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms="HS256")
        print(token_data)
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401

    user_id = token_data["user_id"]
    user = User.query.filter_by(user_id=user_id).first()

    tweets = (
        Tweet.query.filter_by(user_id=user_id)
        .order_by(Tweet.published_at.desc())
        .limit(10)
        .all()
    )
    tweet_list = []

    for tweet in tweets:
        tweet_dict = {
            "id": tweet.id,
            "published_at": tweet.published_at,
            "tweet": tweet.tweet,
        }
        tweet_list.append(tweet_dict)

    return {
        "user_id": user.user_id,
        "username": user.username,
        "bio": user.bio,
        "following": Follow.query.filter(user_id == Follow.follower_id).count(),
        "followers": Follow.query.filter(user_id == Follow.following_id).count(),
        "tweets": tweet_list,
    }
