from flask import Flask, request, jsonify, session, redirect
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
database = connection["eCommerce_CLI"]     #database name. 

users_collection = database["users"]  
cart_collection = database["user_cart"]     # collection name.
products_collection = database["products"] 
coupens_collection = database["coupens"]       

app.secret_key = str(uuid.uuid4())

#Connect to mongodb 
connect(
    db="eCommerce_CLI"
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
    user = users_collection.insert_one({"username":username, "email":email, "user_id":str(user_id), "password":str(password), "is_admin":bool(is_admin), "is_user":bool(is_user)})
    
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


#ADD Coupen Only By Admin
@app.route("/addCoupen", methods=["POST"])
def add_coupen():
    # {"times_of_use" : "1","discount": 50, "coupen_name":"USE50"} 
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    admin_details_fetch = users_collection.find_one({"username": session["username"]})
    coupen_data = request.get_json(force=True)
    
    if admin_details_fetch["is_admin"]:
        coupen_id = str(uuid.uuid4())
        user_id = admin_details_fetch["user_id"]
        times_of_use = coupen_data["times_of_use"]
        start_date = datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
        end_date = datetime.now() + timedelta(days=30) 
        discount = coupen_data["discount"]
        coupen_status = False
        last_use = 0
        coupen_name = coupen_data["coupen_name"]
        
        product = coupens_collection.insert_one({"coupen_id":coupen_id, "times_of_use":times_of_use, "start_date":start_date,
            "end_date":end_date, "discount":discount,"coupen_status": bool(coupen_status), "user_id":(user_id), "last_use":last_use,"coupen_name":coupen_name})
        return jsonify({"status":True, "message":"Coupen Added Successfully"})

    elif user_details_fetch["is_user"] :
        return jsonify({"status":False, "message":"Operation Not Permitted"})            


#ADD The Product Only By Admin
@app.route("/addProduct", methods=["POST"])
def add_product():
    # {"category" : "camputer", "product_name" : "hp pavillion","product_details":"7th gen", "price" : 60000, "quantity": 20} 
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    admin_details_fetch = users_collection.find_one({"username": session["username"]})

    prod_data = request.get_json(force=True)
    
    if admin_details_fetch["is_admin"]:
        product_id = str(uuid.uuid4())
        user_id = admin_details_fetch["user_id"]
        category = prod_data["category"]
        product_name = prod_data["product_name"]
        product_details = prod_data["product_details"]
        price = prod_data["price"]
        quantity = prod_data["quantity"]
        
        product = products_collection.insert_one({"product_id":product_id, "category":category, "product_name":product_name,
            "product_details":product_details, "price":price,"quantity": quantity, "user_id":(user_id)})
        return jsonify({"status":True, "message":"Item Added Successfully"})

    elif user_details_fetch["is_user"] :
        return jsonify({"status":False, "message":"Operation Not Permitted"})            


# Delete The Product Only By Admin
@app.route("/deleteProduct", methods=["DELETE"])
def delete_product():
# {"product_name":"Yahama Guitar2", "quantity":2}
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    user_details_fetch = users_collection.find_one({"username": session["username"]})    
    prod_data = request.get_json(force=True)   
    search_product = products_collection.find({"product_name": prod_data["product_name"]})      
    
    if user_details_fetch["is_user"]:
        return jsonify({"status":False, "message": "You Are Not Permitted To Remove Product Item"})
    
    elif user_details_fetch["is_admin"]:
        for prod_document in search_product:
            if prod_data["quantity"] == prod_document["quantity"]:
                new_quantity = 0
                products_collection.remove( {"product_name":prod_data["product_name"]});
                return jsonify({"status":True, "message":"Product Deleted !No Products Available For the same"})

            elif prod_data["quantity"] > prod_document["quantity"]:
                    return jsonify({"status":False, "message":"Quantity Exceeded. Please Enter Smaller Quantity"})

            elif prod_data["quantity"] < prod_document["quantity"]:
                products_collection.update_one({"product_id":prod_document["product_id"]},{"$set":{"quantity":prod_document["quantity"]-prod_data["quantity"]}})
                return jsonify({"status":True, "message":"Product Deleted !"})
            
            else:
                return jsonify({"status":False, "message": "No Such Item"})          

#Search Products By Category
@app.route("/searchProductByCategory", methods=['GET'])
def search_product_by_category():
    # {"category":"Baby Products"}
    prod_data =request.get_json(force=True)
    product_db = products_collection.find({"category":prod_data["category"]})

    count_product_db = products_collection.count({"category":prod_data["category"]})
    resulting_search_list = []
    if count_product_db != 0:
        for product in product_db:
            product_description = ({"category":product["category"], "product_name":product["product_name"],"product_details":product["product_details"],
             "price":product["price"],"quantity":product["quantity"]})
            resulting_search_list.append(product_description)
        return jsonify({"status": True, "products":resulting_search_list})
            
    else:
        return jsonify({"status":False, "message":"The Item Is Not Available."})

#Search Product Deascription
@app.route("/productDetail", methods=['GET'])
def search_product_detail():
    # {"product_name":"Yahama Guitar2"}
    prod_data =request.get_json(force=True)
    product_db = products_collection.find_one({"product_name":prod_data["product_name"]})

    if product_db:
        return jsonify({"status": True, "product_details":product_db["product_details"]})
    
    else:
        return jsonify({"status":False, "message":"No Such Product Available."})


#Search Categories
@app.route("/searchCategory", methods=['GET'])
def search_categories():
    product_db = products_collection.find()
    category_list = []

    for prod_document in product_db:
        details = {"categories":prod_document["category"]}
        category_list.append(details)
    return jsonify({"status": True, "products":category_list})


#Display Coupens
@app.route("/displayCoupens", methods=['GET'])
def display_coupens():
    coupens_db = coupens_collection.find()
    coupens_list = []

    for coupen_document in coupens_db:
        details = {"coupen_name":coupen_document["coupen_name"], "times_of_use":coupen_document["times_of_use"],
                    "discount":coupen_document["discount"],"end_date":coupen_document["end_date"]}
        coupens_list.append(details)
    return jsonify({"status": True, "Coupens":coupens_list})

    
    
# Add Items To Cart By User  
@app.route("/addCart", methods=["POST"])
def add_cart():
    # {"product_name":"Diapers", quantity": 5}
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    cart_data = request.get_json(force=True)
    sum_of_cart = 0
    
    user_details_fetch = users_collection.find_one({"username": session["username"]})
    product_details_fetch = products_collection.find({"product_name":cart_data["product_name"]})

    if not cart_data["quantity"]:
        return jsonify({"status":False, "message":"Your Cart Running Out of Quanity"})

    if products_collection.count({"product_name":cart_data["product_name"]})==0:
        return jsonify({"status":False, "message":"No Such Product Available"})
        
    if not user_details_fetch["is_user"]:
        return jsonify({"status":False, "message":"You Are Not Eligible To Add Item"})

    elif user_details_fetch["is_user"]:
        for product_document in product_details_fetch:
            product_id = product_document["product_id"]
            category = product_document["category"]
            product_name = cart_data["product_name"]
            product_details = product_document["product_details"]
            user_id = user_details_fetch["user_id"]
            quantity = (cart_data["quantity"])
            max_quantity = product_document["quantity"]
            if quantity > max_quantity:
                return jsonify({"status":False, "message":"Quanity Exceeding Max Amount Of Available Product"})

            else:
                sum_of_cart += quantity*product_document["price"]

            if product_details_fetch:        
                product = cart_collection.insert_one({"product_id":product_id, "category":category, "product_name":product_name, 
                    "product_details":product_details,"sum_of_cart":int(sum_of_cart),"quantity": quantity, "user_id":user_id})
                return jsonify({"status":True, "message":"Item Added Successfully To Cart."})
                        
            else:
                return jsonify({"status":False, "message":"No Such Product Available In Store"})


# Remove Items From Cart By User           
@app.route("/removeCart", methods=["DELETE"])
def remove_cart():
    # {"product_name":"Diapers", quantity": 1}
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    cart_data = request.get_json(force=True)   
    cart_details_fetch = cart_collection.find({"product_name":cart_data["product_name"]})  
    
    for cart_document in cart_details_fetch:
        if cart_document["product_name"] == cart_data["product_name"]:
            new_quantity =  cart_document["quantity"]-cart_data["quantity"] 

    cart_collection.update_one({"product_name":cart_document["product_name"]},{"$set":{"quantity":new_quantity}})

    return jsonify({"status":True, "message":"Product Removed From Cart Successfully"})
            

# Checkout Final Cart Items  
@app.route("/checkout", methods=["GET"])
def checkout():
    # {"coupen_name":"USE10"}
    if "username" not in session:
        return jsonify({"status":False, "message":"Login Required"})

    sum_of_cart = 0
    quantity = 0
    discounted_amount = 0
    actual_amount = 0
    coupen_discount = 0
    current_time = 0

    checkout_data = request.get_json(force=True)

    user_details_fetch = users_collection.find_one({"username": session["username"]})
    cart_details_fetch = cart_collection.find({"user_id": user_details_fetch["user_id"]})
    
    for cart_document in cart_details_fetch:
        sum_of_cart += cart_document["sum_of_cart"]
        product_details_fetch = products_collection.find_one({"product_id": cart_document["product_id"]})
        quantity = product_details_fetch["quantity"] - cart_document["quantity"]
        products_collection.update_one({"product_id":cart_document["product_id"]},{"$set":{"quantity":quantity}})

    actual_amount = sum_of_cart

    if checkout_data["coupen_name"] is None:
        coupen_discount = 0

    else:
        coupen_details = coupens_collection.find_one({"coupen_name":checkout_data["coupen_name"]})
        current_time = datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
        coupen_validity_time = datetime.strptime(str(coupen_details["end_date"]), '%Y-%m-%d %H:%M:%S.%f')
        time = coupen_validity_time - current_time

        if time.days >0 and coupen_details["times_of_use"] >0:
            coupen_last_use = coupen_details["last_use"]
        if coupen_last_use == 0 and coupen_details["times_of_use"] >0:
            discounted_amount = coupen_details["discount"] * sum_of_cart/100
        elif coupen_details["times_of_use"] >0:
            coupen_last_use = datetime.strptime(str(coupen_last_use), '%Y-%m-%d %H:%M:%S.%f')
            time = current_time-coupen_last_use
            hour = time.seconds/(60*60)
            if int(hour) < 4:
                discounted_amount = 0
            else:
                discounted_amount = coupen_details["discount"] * sum_of_cart/100


    if sum_of_cart > 10000 and discounted_amount==0:
        discounted_amount = 500

    final_amount = sum_of_cart - discounted_amount
    bill_description = ({"actual_amount":actual_amount, "discounted_amount":discounted_amount, "final_amount": final_amount})

    cart_collection.delete_many({"user_id":user_details_fetch["user_id"]})
    if coupen_discount!= 0:
        quantity = coupen_details["times_of_use"]-1
        coupens_collection.update_one({"coupen_name":coupen_details["coupen_name"]},{"$set":{"times_of_use":quantity}})
        coupens_collection.update_one({"coupen_name":coupen_details["coupen_name"]},{"$set":{"last_use":current_time}})

    return jsonify({"status":True, "BILL_GENERATED":bill_description})

if __name__ == "__main__":
    app.run(host ="0.0.0.0", debug = True)
