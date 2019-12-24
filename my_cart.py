from flask import Flask, request, jsonify, session
from passlib.hash import pbkdf2_sha256
from mongoengine import connect
from models import Users, Products
from pymongo import MongoClient
import uuid
import json
from datetime import datetime, timedelta

#Instance Of App
app = Flask(__name__)

connection = MongoClient() 
database = connection["eCommerce"]     #database name. 

users_collection = database["users"]  
cart_collection = database["user_cart"]     # collection name.
products_collection = database["products"] 
coupens_collection = database["coupens"]       

app.secret_key = str(uuid.uuid4())

#Connect to mongodb 
connect(
    db="eCommerce"
)

#Register User/Admin
@app.route("/register", methods=["POST"])
def register_user():
    # {"username":"nidhi_user", "email":"nidhi_user@gmail.com", "password":"nidhi", "is_admin":false, "is_user":true,} 
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
    user = users_collection.insert_one({"coupen":0,"username":username, "email":email, "user_id":str(user_id), "password":str(password), "is_admin":bool(is_admin), "is_user":bool(is_user)})
    
    return jsonify({"status": True, "message": "Successfully Register"})

#Login User/Admin
@app.route("/login", methods=["POST"])
def login_user():
    # {"username":"nidhi_user","password":"nidhi"} 
    credentials = request.get_json(force=True)
    try:
        if credentials["username"] and credentials["password"]:
            valid_credentials = pbkdf2_sha256.verify(credentials["password"], Users.objects(username=credentials["username"]).first().password)
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
    # {"title" : "batting", "description" : "bats", "price" : 6000, "quantity": 20, "is_coupen": true, "discount":10, "coupen_type":1} 
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
            user_id = user_details_fetch["user_id"]
            is_coupen = prod_data["is_coupen"]
            discount = prod_data["discount"]
            coupen_type = prod_data["coupen_type"]

            if is_coupen == True:
                add_date = datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
                validity_of_coupon = datetime.now() + timedelta(days=30)          

                product = products_collection.insert_one({"product_id":product_id, "title":title, "description":description, "price":int(price),
                "is_coupen":is_coupen,"coupen_type":coupen_type, "quantity": quantity, "user_id":str(user_id),"coupen_date_added": add_date, "validity_of_coupon": validity_of_coupon, "discount":int(discount),
                })
                return jsonify({"status":True, "message":"Item Added Successfully With Coupen"})

            else:
                product = products_collection.insert_one({"product_id":product_id, "title":title, "description":description, "price":int(price),
                "quantity": quantity, "user_id":str(user_id)})
                return jsonify({"status":True, "message":"Item Added Successfully Without Coupen"})
        
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

#READ The Product By Description For All
@app.route("/searchProductByParameters")
def search_items_by_parameters():
    # {"description":"bats"}
    prod_data =request.get_json(force=True)
    product_db = products_collection.find({"description":prod_data["description"]})

    count_product_db = products_collection.count({"description":prod_data["description"]})
    resulting_search_list = []
    if count_product_db != 0:
        for product in product_db:
            product_description = ({"title":product["title"], "description":product["description"], "price":product["price"],"quantity":product["quantity"], "discount":product["discount"]})
            resulting_search_list.append(product_description)
        return jsonify({"status": True, "products":resulting_search_list})
            
    else:
        return jsonify({"status":False, "message":"The Item Is Not Available."})

# Add Items To Cart By User  
@app.route("/addCart", methods=["POST"])
def add_cart():
    # {"title":"sports", "description":"batting","quantity": 2, "is_coupen":true}
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    cart_data = request.get_json(force=True)
    user_db = users_collection.find({})
    prod_db = products_collection.find({})
    sum_of_cart = 0
    
    if not cart_data["quantity"]:
        return jsonify({"status":False, "message":"Your Cart Running Out of Quanity"})

    if products_collection.count({"title":cart_data["title"]})==0:
        return jsonify({"status":False, "message":"No Such Product Available"})

    else:
        user_details_fetch = users_collection.find_one({"username": session["username"]})
        product_details_fetch = products_collection.find_one({"title":cart_data["title"]})

        for product_document in prod_db:
            for user_document in user_db:

                if not user_details_fetch["is_user"]:
                    return jsonify({"status":False, "message":"You Are Not Eligible To Add Item"})

                elif user_details_fetch["is_user"] :
                    product_id = product_details_fetch["product_id"]
                    title = cart_data["title"]
                    description = cart_data["description"]
                    user_id = user_details_fetch["user_id"]
                    quantity = int(cart_data["quantity"])
                    max_quantity = product_document["quantity"]
                    is_coupen = product_document["is_coupen"]

                    if quantity > max_quantity:
                        return jsonify({"status":False, "message":"Quanity Exceeding Max Amount Of Available Product"})

                    else:
                        sum_of_cart += quantity*product_document["price"]
                    
                    product_details_fetch = products_collection.find_one({"product_id": product_id})

                    if product_details_fetch and is_coupen==True and user_details_fetch["coupen"] == 0:        
                        product = cart_collection.insert_one({"product_id":product_details_fetch["product_id"], "title":title, "description":description, "sum_of_cart":int(sum_of_cart),
                            "quantity": quantity, "user_id":user_details_fetch["user_id"], "is_coupen":True})

                        users_collection.update_one({"user_id":user_details_fetch["user_id"]},{"$set":{"coupen":product_details_fetch["discount"]}})
                        return jsonify({"status":True, "message":"Item Added Successfully To Cart."})

                    elif product_details_fetch and is_coupen==True and user_details_fetch["coupen"] != 0:
                        product = cart_collection.insert_one({"product_id":product_details_fetch["product_id"], "title":title, "description":description, "sum_of_cart":int(sum_of_cart),
                            "quantity": quantity, "user_id":user_details_fetch["user_id"], "is_coupen":False})
                        return jsonify({"status":True, "message":"Item Added Successfully To Cart. Coupen Already Applied"})

                    elif product_details_fetch and is_coupen==False:        
                        product = cart_collection.insert_one({"product_id":product_details_fetch["product_id"], "title":title, "description":description, "sum_of_cart":int(sum_of_cart),
                            "quantity": quantity, "user_id":user_details_fetch["user_id"], "is_coupen":is_coupen})
                        return jsonify({"status":True, "message":"Item Added Successfully To Cart."})
                    
                    else:
                        return jsonify({"status":False, "message":"Please Select Valid Product From Available Options"})

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
    cart_data = request.get_json(force=True)   
    
    for user_document in user_db:
        for prod_document in cart_db:
            user_details_fetch = users_collection.find_one({"username": session["username"]})
            product_id_fetch = cart_collection.find_one({"product_id": cart_data["product_id"]})
            user_id_fetch = cart_collection.find_one({"user_id": user_details_fetch["user_id"]})

            if product_id_fetch and user_id_fetch:
                cart_collection.remove( {"product_id":cart_data["product_id"]});
                return jsonify({"status":True, "message":"Product Deleted Successfully"})

            elif not product_id_fetch:
                return jsonify({"status":False, "message": "No Such Item"})

            elif not user_id_fetch:
                return jsonify({"status":False, "message": "You Are Not Permitted To Remove Cart Item"})

# Checkout Final Cart Items  
@app.route("/checkout", methods=["GET"])
def checkout():
    # {"username":nidhi_user }
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    sum_of_cart = 0
    quantity = 0
    discounted_amount = 0
    actual_amount = 0

    user_details_fetch = users_collection.find_one({"username": session["username"]})
    coupen = user_details_fetch['coupen']
    
    cart_details_fetch = cart_collection.find({"user_id": user_details_fetch["user_id"]})
    
    for cart_document in cart_details_fetch:
        sum_of_cart += cart_document["sum_of_cart"]
        product_details_fetch = products_collection.find_one({"product_id": cart_document["product_id"]})
        quantity = product_details_fetch["quantity"] - cart_document["quantity"]
        products_collection.update_one({"product_id":cart_document["product_id"]},{"$set":{"quantity":quantity}})

    actual_amount = sum_of_cart
    if sum_of_cart > 10000 and  cart_document["is_coupen"] == False :
        discounted_amount = 500

    elif sum_of_cart > 10000 and  cart_document["is_coupen"] == True :
        discounted_amount = (coupen*sum_of_cart)/100

    elif sum_of_cart <= 10000:
        discounted_amount = (coupen*sum_of_cart)/100

    final_amount = sum_of_cart - discounted_amount
    bill_description = ({"actual_amount":actual_amount, "discounted_amount":discounted_amount, "final_amount": final_amount})

    cart_collection.delete_many({"user_id":user_details_fetch["user_id"]})

    users_collection.update_one({"user_id":user_details_fetch["user_id"]},{"$set":{"coupen":0}})

    return jsonify({"status":True, "BILL_GENERATED":bill_description})

if __name__ == "__main__":
    app.run(host ="0.0.0.0", debug = True)
