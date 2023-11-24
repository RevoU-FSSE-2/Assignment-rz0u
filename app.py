import os
from flask import Flask
from db import db, db_init
from auth.apis import auth_bp
from tweet.apis import tweet_bp
from follow.apis import follow_bp
from user_profile.apis import user_bp

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
print(database_url)
db.init_app(app)


# Home
@app.route("/")
def index():
    return "Week 21 Rayhan Zou"


# Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(tweet_bp, url_prefix="/tweet")
app.register_blueprint(follow_bp, url_prefix="/follow")
app.register_blueprint(user_bp, url_prefix="/user")


# Database Migration
# with app.app_context():
#     db_init()
