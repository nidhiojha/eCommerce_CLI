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
    title = StringField(required=True)
    description = StringField()
    price = FloatField(required=True)
    quantity = StringField(required=True)
    user_id = StringField(required=True)
