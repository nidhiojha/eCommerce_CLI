from mongoengine import Document, StringField, EmailField, FloatField, BooleanField, IntField

class Users(Document):
    user_id = StringField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    is_admin = BooleanField(default=False)
    is_user = BooleanField(default=False)

class Products(Document):
    product_id = StringField(required= True, unique=True)
    category = StringField(required=True,unique=True)
    product_name = StringField(required=True, unique=True)
    product_details = StringField(required=True)
    price = FloatField(required=True)
    quantity = IntField(required=True)
    user_id = StringField(required=True)
    
class Cart(Document):
    product_id = StringField(required= True, unique=True)
    category = StringField(required=True,unique=True)
    product_name = StringField(required=True, unique=True)
    product_details = StringField(required=True)
    sum_of_cart = FloatField(required=True)
    quantity = IntField(required=True)
    user_id = StringField(required=True)
    
class Coupens(Document):
    coupen_name = StringField(required=True, unique=True)
    coupen_id = StringField(required= True, unique=True)
    times_of_use = IntField(required=True)
    start_date = StringField(required= True)
    end_date = StringField(required= True)
    discount = FloatField(required=True)
    coupen_status = BooleanField(default=False)
    last_use = StringField(required=True)

