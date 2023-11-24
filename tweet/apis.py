from flask import Blueprint, request
from tweet.models import Tweet, TweetSchema
from marshmallow import ValidationError
from db import db
import jwt, datetime, os
from utils.jwt import decode_jwt
from auth.models import User
from datetime import datetime

tweet_bp = Blueprint("tweet", __name__)


@tweet_bp.route("", methods=["POST"])
def tweet():
    data = request.get_json()
    schema = TweetSchema()

    try:
        schema.load(data)
    except ValidationError as err:
        return {"error": err.messages}, 400

    authorization_header = request.headers.get("Authorization")
    print(authorization_header)

    if not authorization_header:
        return {"error": "Not authorized"}, 401
    token = authorization_header.split(" ")[1]
    print(token)
    try:
        token_data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms="HS256")
        print(token_data)
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401

    user_id = token_data["user_id"]

    tweet = Tweet(published_at=datetime.now(), tweet=data["tweet"], user_id=user_id)

    if len(tweet.tweet) > 150:
        return {"error": "Tweet cannot be more than 150 characters"}, 400

    db.session.add(tweet)
    db.session.commit()
    return {
        "id": tweet.id,
        "published_at": tweet.published_at,
        "tweet": tweet.tweet,
    }
