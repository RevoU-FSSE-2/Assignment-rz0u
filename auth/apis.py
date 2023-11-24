from flask import Blueprint, request
from auth.models import User, UserRegistrationSchema, UserLoginSchema
from marshmallow import ValidationError
from db import db
import jwt, datetime, os
from utils.bcrypt import bcrypt

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    schema = UserRegistrationSchema()
    try:
        schema.load(data)
    except ValidationError as err:
        return {"error": err.messages}, 400

    if User.query.filter_by(username=data["username"]).first():
        return {"error": "Username already exists"}, 400

    if len(data["bio"]) > 200:
        return {"error": "Bio is too long! (max 200 char)"}, 400

    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(username=data["username"], password=hashed_password, bio=data["bio"])
    db.session.add(user)
    db.session.commit()
    return {
        "user_id": user.user_id,
        "username": user.username,
        "bio": user.bio,
    }, 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    schema = UserLoginSchema()
    try:
        schema.load(data)
    except ValidationError as err:
        return {"error": err.messages}, 400

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not bcrypt.check_password_hash(user.password, data["password"]):
        return {"error": "Invalid username or password"}, 401

    payload = {
        "user_id": user.user_id,
        "username": user.username,
        "bio": user.bio,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(hours=5),  # Ganti jadi 10 mins aja nanti
    }
    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")

    return {
        "token": token,
    }
