from flask import Flask, request, jsonify, session
from passlib.hash import pbkdf2_sha256
from mongoengine import connect
from models import Users, Products
from pymongo import MongoClient
import uuid
import json

#instance of app
app = Flask(__name__)

connection = MongoClient() 
database = connection["eCommerce"]     #database name. 
users_collection = database["users"]  
products_collection = database["products"]        # collection name.

app.secret_key = str(uuid.uuid4())

#Connect to mongodb 
connect(
    db='eCommerce'
)

#register the user
@app.route('/register', methods=['POST'])
def register_user():
	# {"username":"nidhi_user", "email":"nidhi_user@gmail.com", "password":"nidhi", "is_admin":false, "is_user":true} 
    user_data = request.get_json(force=True)
    username = user_data['username']
    email = user_data['email']
    is_admin = False
    is_user = False
    password = pbkdf2_sha256.hash(user_data['password'])
    user_id = str(uuid.uuid4())
    if 'is_admin' in user_data:
        is_admin = user_data['is_admin']
    if 'is_user' in user_data:
        is_user = user_data['is_user']
    user = users_collection.insert_one({"username":username, "email":email, "user_id":str(user_id), "password":str(password), "is_admin":bool(is_admin), "is_user":bool(is_user)})
    
    return jsonify({'status': True, 'message': "successfully register"})

#login user
@app.route('/login', methods=['POST'])
def login_user():
    credentials = request.get_json(force=True)
    try:
        if credentials['username'] and credentials['password']:
            valid_credentials = pbkdf2_sha256.verify(credentials['password'],
                                                     Users.objects(username=credentials['username']).first().password)
        else:
            valid_credentials = False
    except:
        valid_credentials = False

    if valid_credentials:
        session['username'] = credentials['username']

    return jsonify({'status': valid_credentials})



if __name__ == "__main__":
    app.run(host ="0.0.0.0", debug = True)
