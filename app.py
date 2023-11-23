import os
from flask import Flask, request
from db import db, db_init
from marshmallow import Schema, fields, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
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
    if user and bcrypt.check_password_hash(user.password, data["password"]):
        return {"message": "User logged in successfully"}, 200
    else:
        return {"error": "Invalid username or password"}, 401


class TweetSchema(Schema):
    tweet = fields.Str(required=True)


@app.route("/tweets", methods=["POST"])
def create_tweet():
    data = request.get_


with app.app_context():
    db_init()
