from mongoengine import Document, StringField, EmailField, FloatField, BooleanField

class Users(Document):
    username = StringField(required=True, unique=True)
    user_id = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    is_admin = BooleanField(default=False)
    is_user = BooleanField(default=False)

class Products(Document):
    product_id = StringField(required= True, unique=True)
    title = StringField(required=True,)
    description = StringField()
    price = FloatField(required=True)
    quantity = StringField(required=True)
    user_id = StringField(required=True)
    is_coupen = BooleanField(default=False)
    discount = BooleanField(default=True)
    coupen_type = FloatField(required=True)

class Cart(Document):
    product_id = StringField(required= True, unique=True)
    title = StringField(required=True)
    description = StringField(required=True)
    sum_of_cart = FloatField(required=True)
    quantity = StringField(required=True)
    user_id = StringField(required=True)
