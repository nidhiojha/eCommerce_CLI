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
cart_collection = database["user_cart"]
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
    
    return jsonify({'status': True, 'message': "Successfully Register"})

#login user
@app.route('/login', methods=['POST'])
def login_user():
    # {"username":"nidhi_user","password":"nidhi"} 
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

#logout user
@app.route('/logout')
def logout_user():
    session.clear()
    return jsonify({'status': 'Logout Successfully'})


#ADD The Product 
@app.route('/addProduct', methods=['POST'])
def add_product():
    # {"title" : "sports", "description" : "batting","quantity": 2, "price" : 5000, "user_id" : "8881ebf2-aec5-4dd5-997d-082d9cb50bdc"} 
    if 'username' not in session:
        return jsonify({'status':False, 'message':'Login Required'})
    
    prod_data = request.get_json(force=True)
    user_db = users_collection.find({})
   
    for document in user_db:
        product_id = str(uuid.uuid4())
        title = prod_data['title']
        description = prod_data['description']
        price = prod_data['price']
        quantity = int(prod_data['quantity'])
        user_id = prod_data['user_id']
        if prod_data['user_id'] == document['user_id'] and document['is_admin']:
            product = products_collection.insert_one({"product_id":product_id, "title":title, "description":description, "price":int(price),
           "quantity": quantity, "user_id":str(user_id)})
            return jsonify({'status':True, 'message':'Item Added Successfully.'})
        elif  prod_data['user_id'] == document['user_id'] and document['is_user']:
            return jsonify({'status':False, 'message':'Operation Not Permitted'})
        

# Delete The Product
@app.route('/deleteProduct', methods=['DELETE'])
def delete_product():
# {"product_id":"7cb5b3df-b5de-4dc1-9b81-d56c5d7415ab", "user_id":"8881ebf2-aec5-4dd5-997d-082d9cb50bdc"}
    if 'username' not in session:
        return jsonify({'status':False, 'message':'Login Required'})

    prod_db = products_collection.find({})
    user_db = users_collection.find({})

    prod_data = request.get_json(force=True)
    
    for user_document in user_db:
        for prod_document in prod_db:
            if not user_document["is_admin"] and not user_document["is_user"] :
                return jsonify({'status':False, 'message': 'You Are Not Permitted To Delete This Item'})
            
            elif user_document["is_admin"] and user_document["user_id"] == prod_data[user_id] :
                product = products_collection.find_one({'product_id': prod_data['product_id']})

                if product :   
                    products_collection.remove( {"product_id":prod_data['product_id']});
                    return jsonify({'status':True, 'message':'Product Deleted'})
                
                else:
                    return jsonify({'status':False, 'message':'No Matching Product Found To Delete'})

            elif user_document["is_user"] :
                product = products_collection.find_one({'product_id': prod_data['product_id']})
                
                if product :
                    if prod_document['user_id'] == prod_data['user_id']:
                        products_collection.remove( {"product_id":prod_data['product_id']});
                        return jsonify({'status':True, 'message':'Product Deleted'})
                    else:
                        return jsonify({'status':False, 'message': 'You Are Not Authorised To Delete This Item'})
                else:
                    return jsonify({'status':False, 'message':'No Matching Product Found To Delete'})



#Search The product by ID for all
@app.route('/searchProductById')
def search_items():
    # {"prod_id" : "08d88c68-66a1-416d-af1c-b54d3c94facf"}
    prod_data =request.get_json(force=True)
    product = products_collection.find({'product_id': prod_data['prod_id']})
    product_description = {}
    if product:
        
        product_description = ({"product_id":product['product_id'], "title":product['title'], "description":product['description'], "price":product['price'],
             "user_id":str(product['user_id'])})
        return jsonify({'status': True, 'products':product_description})
    else:
        return jsonify({'status':False, 'message':'The Item Is Not Available.'})

#READ The product by tile or description or price for all
@app.route('/searchProductByParameters')
def search_items_by_parameters():
    prod_data =request.get_json(force=True)
    search_filter = {}

    if 'title' in prod_data:
        search_filter['title'] = request.args.get('title')

    if 'description' in prod_data:
        search_filter['description'] = request.args.get('description')

    if 'price' in prod_data:
        search_filter['price'] = request.args.get('price')

    product = products_collection.find_one(search_filter)
    product_description = {}
    if (product):
        product_description = ({"product_id":product['product_id'], "title":product['title'], "description":product['description'], "price":product['price'],
             "user_id":str(product['user_id'])})
        return jsonify({'status': True, 'products':product_description})
        
    else:
        return jsonify({'status':False, 'message':'The Item Is Not Available.'})


@app.route('/addCart', methods=['POST'])
def add_cart():
    # {"title":"sports", "description":"batting", "user_id":"5e0ac3f2-dd16-4c53-a6ee-f15a4a92dd96","quantity": 2 }
    if 'username' not in session:
        return jsonify({'status':False, 'message':'Login Required'})

    prod_data = request.get_json(force=True)

    user_db = users_collection.find({})
    prod_db = products_collection.find({})
    cart_db = cart_collection.find({})

    if not prod_data['quantity']:
        return jsonify({'status':False, 'message':'Your Cart Running Out of Quanity'})

    sum_of_cart = 0
    for product_document in prod_db:
        for user_document in user_db:
            
            if user_document["is_admin"] and user_document["user_id"] == prod_data["user_id"]:
                return jsonify({'status':False})

            elif user_document["is_user"] and user_document["user_id"] == prod_data["user_id"]:
                product_id = str(uuid.uuid4())
                title = prod_data['title']
                description = prod_data['description']
                seller_id = prod_data['user_id']
                quantity = int(prod_data['quantity'])
                max_quantity = product_document['quantity']

                if quantity > max_quantity:
                    return jsonify({'status':False, 'message':'Quanity Exceeding Max Amount Of Product'})
                else:
                    sum_of_cart += quantity*product_document['price']
                    if sum_of_cart > 5000:
                        total_payble_amount = sum_of_cart - (.1*sum_of_cart)
                    else:
                        total_payble_amount = sum_of_cart

                product = cart_collection.insert_one({"product_id":product_id, "title":title, "description":description, "sum_of_cart":int(sum_of_cart),
                 "total_payble_amount": total_payble_amount, "quantity": quantity, "user_id":prod_data["user_id"]})
                return jsonify({'status':True, 'message':'Item Added Successfully to Cart.'})
            else:
                return jsonify({'status':False, 'message':'Please Authorise Yourself'})
                
# Remove Item From Cart By User           
@app.route('/removeCart', methods=['DELETE'])
def remove_cart():
   # {"product_id":"e4ea97df-498f-4dc7-9a1d-5394dfc75db0", "user_id":"5e0ac3f2-dd16-4c53-a6ee-f15a4a92dd96"}
    if 'username' not in session:
        return jsonify({'status':False, 'message':'Login Required'})

    cart_db = cart_collection.find({})
    user_db = users_collection.find({})

    prod_data = request.get_json(force=True)
   
    
    for user_document in user_db:
        for prod_document in cart_db:
            product_id_fetch = cart_collection.find_one({'product_id': prod_data['product_id']})
            user_id_fetch = cart_collection.find_one({"user_id": prod_data['user_id']})

            if product_id_fetch and user_id_fetch and user_id_fetch["user_id"] == prod_data["user_id"]:
                cart_collection.remove( {"product_id":prod_data['product_id']});
                return jsonify({'status':True, 'message':'Product Deleted'})

            elif not product_id_fetch:
                return jsonify({'status':False, 'message': 'No Such Item'})

            elif not user_id_fetch:
                return jsonify({'status':False, 'message': 'You Are Not Permitted To Remove Cart Item'})
            
if __name__ == "__main__":
    app.run(host ="0.0.0.0", debug = True)
