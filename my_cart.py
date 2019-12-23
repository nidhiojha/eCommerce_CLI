from flask import Flask, request, jsonify, session
from passlib.hash import pbkdf2_sha256
from mongoengine import connect
from models import Users, Products
from pymongo import MongoClient
import uuid
import json

#Instance Of App
app = Flask(__name__)

connection = MongoClient() 
database = connection["eCommerce"]     #database name. 

users_collection = database["users"]  
cart_collection = database["user_cart"]     # collection name.
products_collection = database["products"]        

app.secret_key = str(uuid.uuid4())

#Connect to mongodb 
connect(
    db="eCommerce"
)

#Register User/Admin
@app.route("/register", methods=["POST"])
def register_user():
    # {"username":"nidhi_user", "email":"nidhi_user@gmail.com", "password":"nidhi", "is_admin":false, "is_user":true} 
    user_data = request.get_json(force=True)
    username = user_data["username"]
    email = user_data["email"]
    is_admin = False
    is_user = False
    password = pbkdf2_sha256.hash(user_data["password"])
    user_id = str(uuid.uuid4())
    if "is_admin" in user_data:
        is_admin = user_data["is_admin"]
    if "is_user" in user_data:
        is_user = user_data["is_user"]
    user = users_collection.insert_one({"username":username, "email":email, "user_id":str(user_id), "password":str(password), "is_admin":bool(is_admin), "is_user":bool(is_user)})
    
    return jsonify({"status": True, "message": "Successfully Register"})

#Login User/Admin
@app.route("/login", methods=["POST"])
def login_user():
    # {"username":"nidhi_user","password":"nidhi"} 
    credentials = request.get_json(force=True)
    try:
        if credentials["username"] and credentials["password"]:
            valid_credentials = pbkdf2_sha256.verify(credentials["password"],
                                                     Users.objects(username=credentials["username"]).first().password)
        else:
            valid_credentials = False
    except:
        valid_credentials = False

    if valid_credentials:
        session["username"] = credentials["username"]


    return jsonify({"status": valid_credentials})

#logout user
@app.route("/logout")
def logout_user():
    session.clear()
    return jsonify({"status": "Logout Successfully"})


#ADD The Product Only By Admin
@app.route("/addProduct", methods=["POST"])
def add_product():
    # {"title" : "sports", "description" : "batting","quantity": 2, "price" : 5000, "user_id" : "8881ebf2-aec5-4dd5-997d-082d9cb50bdc"} 
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})
    
    prod_data = request.get_json(force=True)
    user_db = users_collection.find({})
    
    for document in user_db:
        user_details_fetch = users_collection.find_one({"username": session["username"]})

        if user_details_fetch["is_admin"]:
            product_id = str(uuid.uuid4())
            title = prod_data["title"]
            description = prod_data["description"]
            price = prod_data["price"]
            quantity = int(prod_data["quantity"])
            user_id = session["user_id"]
            product = products_collection.insert_one({"product_id":product_id, "title":title, "description":description, "price":int(price),
            "quantity": quantity, "user_id":str(user_id)})
            return jsonify({"status":True, "message":"Item Added Successfully."})
        elif user_details_fetch["is_user"] :
            return jsonify({"status":False, "message":"Operation Not Permitted"})
            

# Delete The Product Only By Admin
@app.route("/deleteProduct", methods=["DELETE"])
def delete_product():
# {"product_id":"7cb5b3df-b5de-4dc1-9b81-d56c5d7415ab"}
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    prod_db = products_collection.find({})
    user_db = users_collection.find({})

    prod_data = request.get_json(force=True)
    
    for user_document in user_db:
        user_details_fetch = users_collection.find_one({"username": session["username"]})
        if user_details_fetch["is_admin"] :
            product_id_fetch = products_collection.find_one({"product_id": prod_data["product_id"]})
            if product_id_fetch:
                products_collection.remove( {"product_id":prod_data["product_id"]});
                return jsonify({"status":True, "message":"Product Deleted"})

            if not product_id_fetch:
                return jsonify({"status":False, "message": "No Such Item"})

        elif user_details_fetch["is_user"] :
                return jsonify({"status":False, "message": "You Are Not Permitted To Remove Product Item"})
            
    

#READ The Product By Title Or Description Or Price For All
@app.route("/searchProductByParameters")
def search_items_by_parameters():
    # {"title":"sports"}
    prod_data =request.get_json(force=True)
    search_filter = {}

    if "title" in prod_data:
        search_filter["title"] = request.args.get("title")

    if "description" in prod_data:
        search_filter["description"] = request.args.get("description")

    product = products_collection.find_one(search_filter)
    product_description = {}
    if (product):
        product_description = ({"product_id":product["product_id"], "title":product["title"], "description":product["description"], "price":product["price"],
             "user_id":str(product["user_id"])})
        return jsonify({"status": True, "products":product_description})
        
    else:
        return jsonify({"status":False, "message":"The Item Is Not Available."})

# Add Items To Cart By User  
@app.route("/addCart", methods=["POST"])
def add_cart():
    # {"title":"sports", "description":"batting","quantity": 2 }
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    prod_data = request.get_json(force=True)
    user_db = users_collection.find({})
    prod_db = products_collection.find({})
    sum_of_cart = 0
    
    if not prod_data["quantity"]:
        return jsonify({"status":False, "message":"Your Cart Running Out of Quanity"})
   
    for product_document in prod_db:

        for user_document in user_db:
            user_details_fetch = users_collection.find_one({"username": session["username"]})

            if not user_details_fetch["is_user"]:
                return jsonify({"status":False, "message":"You Are Not Eligible To Add Item"})

            elif user_details_fetch["is_user"] :
                product_id = str(uuid.uuid4())
                title = prod_data["title"]
                description = prod_data["description"]
                user_id = user_details_fetch["user_id"]
                quantity = int(prod_data["quantity"])
                max_quantity = product_document["quantity"]

                if quantity > max_quantity:
                    return jsonify({"status":False, "message":"Quanity Exceeding Max Amount Of Product"})
                else:
                    sum_of_cart += quantity*product_document["price"]
                    if sum_of_cart > 5000:
                        total_payble_amount = sum_of_cart - (.1*sum_of_cart)
                    else:
                        total_payble_amount = sum_of_cart
                product = cart_collection.insert_one({"product_id":product_id, "title":title, "description":description, "sum_of_cart":int(sum_of_cart),
                 "total_payble_amount": total_payble_amount, "quantity": quantity, "user_id":user_details_fetch["user_id"]})
                return jsonify({"status":True, "message":"Item Added Successfully To Cart."})
            else:
                return jsonify({"status":False, "message":"Please Authorise Yourself"})

# Remove Items From Cart By User           
@app.route("/removeCart", methods=["DELETE"])
def remove_cart():
    # {"product_id":"2b52508c-6843-4fa1-ac2b-c36fdfe6bb71"}
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    cart_db = cart_collection.find({})
    user_db = users_collection.find({})
    prod_data = request.get_json(force=True)   
    
    for user_document in user_db:
        for prod_document in cart_db:
            user_details_fetch = users_collection.find_one({"username": session["username"]})

            product_id_fetch = cart_collection.find_one({"product_id": prod_data["product_id"]})
            user_id_fetch = cart_collection.find_one({"user_id": user_details_fetch["user_id"]})

            if product_id_fetch and user_id_fetch:
                cart_collection.remove( {"product_id":prod_data["product_id"]});
                return jsonify({"status":True, "message":"Product Deleted Successfully"})

            elif not product_id_fetch:
                return jsonify({"status":False, "message": "No Such Item"})

            elif not user_id_fetch:
                return jsonify({"status":False, "message": "You Are Not Permitted To Remove Cart Item"})
            
if __name__ == "__main__":
    app.run(host ="0.0.0.0", debug = True)
