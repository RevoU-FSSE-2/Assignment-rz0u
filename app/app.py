from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://~~'
app.config['SECRET_KEY'] = 'my-secret-key'
db = SQLAlchemy(app)
jwt = JWTManager(app)

#Define models
##---------------

@app.route('/register', methods=['POST'])
def register():
    # Register Logic
    pass

@app.route('/login', methods=['POST'])
def login():
    # Login Logic
    pass

@app.route('/tweet', methods=['POST'])
@jwt_required
def post_tweet():
    # Post Tweet Logic
    pass

@app.route('/profile', methods=['GET'])
@jwt_required
def profile():
    # Profile Retrieval Logic
    pass

if __name__ == '__main__':
    app.run(debug=True)