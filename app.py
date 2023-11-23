import os, jwt
from flask import Flask, request
from db import db, db_init
from marshmallow import Schema, fields, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime


app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
print(database_url)
db.init_app(app)
bcrypt = Bcrypt()


# Home
@app.route("/")
def index():
    return "Week 21 Rayhan Zou"


# Models
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.String(200), nullable=True)


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    published_at = db.Column(db.DateTime, nullable=False)
    tweet = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    user = db.relationship("User", backref=db.backref("tweets", lazy=True))


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    user = db.relationship("User", backref=db.backref("follows", lazy=True))


# User Registration
class UserRegistrationSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    bio = fields.Str(required=False)


@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    schema = UserRegistrationSchema()
    try:
        schema.load(data)
    except ValidationError as err:
        return {"error": err.messages}, 400

    if User.query.filter_by(username=data["username"]).first():
        return {"error": "Username already exists"}, 400

    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(username=data["username"], password=hashed_password, bio=data["bio"])
    db.session.add(user)
    db.session.commit()
    return {
        "user_id": user.user_id,
        "username": user.username,
        "bio": user.bio,
    }, 201


# User Login
class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    schema = UserLoginSchema()
    try:
        schema.load(data)
    except ValidationError as err:
        return {"error": err.messages}, 400

    user = User.query.filter_by(username=data["username"]).first()
    if not user and bcrypt.check_password_hash(user.password, data["password"]):
        return {"error": "Invalid username or password"}, 401

    payload = {
        "user_id": user.user_id,
        "username": user.username,
        "bio": user.bio,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=300),
    }
    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")

    return {
        "token": token,
    }


# Post a Tweet
class TweetSchema(Schema):
    tweet = fields.Str(required=True)


@app.route("/tweets", methods=["POST"])
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


# Following & Unfollow
@app.route("/follow", methods=["POST"])
def follow():
    data = request.get_json()
    if not request.headers.get("Authorization"):
        return {"error": "Not authorized"}, 401
    user_id = jwt.decode(
        request.headers.get("Authorization"),
        os.getenv("SECRET_KEY"),
        algorithms="HS256",
    )["user_id"]
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


# User Profiles
@app.route("/user", methods=["GET"])
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


# with app.app_context():
#     db_init()
