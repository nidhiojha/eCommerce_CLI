### REGISTER_END_POINT <br />

**METHOD** : POST <br />

**END POINT** : localhost:5000/register <br />

**Request body** (JSON) <br />
{ <br />
  "username" : "string", <br />
  "email" : "string", <br />
  "is_admin" : "boolean", <br />
  "is_user" : "boolean", <br />
  "password" :"string" <br />
} <br />
 
**Sample request** <br />
{"username":"nidhi_user", "email":"nidhi_user@gmail.com", "password":"nidhi", "is_admin":false, "is_user":true}  <br />

**Response Param** <br />
{ <br />
  "status": true, <br />
  "message": "Successfully Register" <br />
} <br />

### LOGIN_END_POINT <br />

**METHOD** : POST <br />

**END POINT** : localhost:5000/login <br />

**Request body** <br />
{ <br />
  "username" : "string", <br />
  "password" : "string" <br />
} <br />

**Sample request** <br />
{"username" : "nidhi_user", "password" : "nidhi" } <br />


**Response Param** <br />
{ <br />
  "status": true <br />
} <br />


### CREATE_END_POINT:

**METHOD** : POST <br />

**END POINT** : localhost:5000/addProduct <br />

**Request body** <br />
{ <br />
  "title" : "string", <br />
  "description" :"string", <br />
  "price" : "float", <br />
} <br />


**If ADMIN Then Pick User Name From Session** <br />

**Sample request** <br />
{"title" : "sports", "description" : "batting","quantity": 2, "price" : 5000}  <br />

**Response Param** <br />
{ <br />
  "status": true <br />
} <br />


**METHOD** : POST <br />

**END POINT** : localhost:5000/addCart <br />

**Request body** <br />
{ <br />
  "title" : "string", <br />
  "description" :"string", <br />
  "quantity" : "integer", <br />
} <br />


**If USER Then Pick User Name From Session** <br />

**Sample request** <br />
{"title" : "sports", "description" : "batting","quantity": 2}  <br />

**Response Param** <br />
{ <br />
  "message": "Item Added Successfully To Cart. Coupen Already Applied", <br />
  "status": true <br />
} <br />

*IF NOT AUTHORISED USER* <br />

**response**
{ <br />
  "message": "Please Authorise Yourself", <br />
  "status": false <br />
} <br 

### READ_END_POINT: <br />

**METHOD** : GET <br />

***Type*** <br />
 
**searchProductByParameters** <br />

**END POINT** : localhost:5000/searchProductByParameters <br />

**Request Body**<br />
{"description":"bats"}  <br />

**Response**[<br />
{ [<br />
  "products": [<br />
    { [<br />
      "description": "bats",[<br />
      "discount": 10,[<br />
      "price": 6000,[<br />
      "quantity": 20,[<br />
      "title": "batting"[<br />
    },[<br />
    { [<br />
      "description": "bats",[<br />
      "discount": 10,[<br />
      "price": 6000,[<br />
      "quantity": 20,[<br />
      "title": "bawls"[<br />
    } [<br />
  ],[<br />
  "status": true[<br />
} [<br />


**METHOD** : GET <br />

***Type*** <br />
 
**checkout** <br />

**END POINT** : localhost:5000/checkout <br />

**Request Body**<br />
{"username":nidhi_user }  <br />

**Response**[<br />
{
  "BILL_GENERATED": {
    "actual_amount": 36000,
    "discounted_amount": 500,
    "final_amount": 35500
  },
  "status": true
}


### DELETE_END_POINT: <br />

**METHOD** : DELETE <br />

**END POINT** : localhost:5000/deleteProduct <br />

**Request body** <br />
{ <br />
  "product_id" : "string" <br />
}  <br />

**Sample Request**
{"product_id":"7cb5b3df-b5de-4dc1-9b81-d56c5d7415ab"} <br />

*IF USER:* <br />

**Sample Request**
{"product_id":"fb98e6b4-b2cc-414b-92f5-9264ef0a14d4"} <br />

**response**
{ <br />
  "message": "Opearation not permitted", <br />
  "status": false <br />
} <br />

*IF USER WITH INVALID creation:* <br />

**response**
{ <br />
  "message": "Opearation not permitted", <br />
  "status": false <br />
} <br />

*ANY OTHER CASES:* <br />

{"product_id":"fb98e6b4-b2cc-414b-92f5-9264ef0a14d4"} <br />

{ <br />
  "status": true <br />
} <br />


**METHOD** : DELETE <br />

**END POINT** : localhost:5000/removeCart <br />

**Request body** <br />
{ <br />
  "product_id" : "string" <br />
}  <br />

**Sample Request**
{"product_id":"7cb5b3df-b5de-4dc1-9b81-d56c5d7415ab"} <br />

*IF USER:* <br />

**Sample Request**
{"product_id":"fb98e6b4-b2cc-414b-92f5-9264ef0a14d4"} <br />

**response**
{ <br />
  "message": "Product Deleted Successfully", <br />
  "status": true <br />
} <br />

*IF USER WITH INVALID CREATION:* <br />

**response**
{ <br />
  "message": "You Are Not Permitted To Remove Cart Item", <br />
  "status": false <br />
} <br />

*IF PRODUCT ID DOES NOT EXISTS IN CART DATABASE:* <br />

**response**
{ <br />
  "message": "No Such Item", <br />
  "status": false <br />
} <br />

