from flask import Blueprint, request
from tweet.models import Tweet, TweetSchema
from marshmallow import ValidationError
from db import db
import jwt, datetime, os

tweet_bp = Blueprint("tweet", __name__)


@tweet_bp.route("", methods=["POST"])
def tweet():
    data = request.get_json()
    schema = TweetSchema()
    try:
        schema.load(data)
    except ValidationError as err:
        return {"error": err.messages}, 400
    if not request.headers.get("Authorization"):
        return {"error": "Not authorized"}, 401
    user_id = jwt.decode(
        request.headers.get("Authorization"),
        os.getenv("SECRET_KEY"),
        algorithms="HS256",
    )["user_id"]
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
