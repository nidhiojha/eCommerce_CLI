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


### READ_END_POINT: <br />

**METHOD** : GET <br />

***Type*** <br />
 
**searchProductByParameters** <br />

**END POINT** : localhost:5000/searchProductByParameters?title=sports <br />
OR <br />
**END POINT** : localhost:5000/searchProductByParameters?description=batting <br />

**Request Body**<br />
{"title":"sports"}  <br />
OR <br />
{"description":"batting"} <br />

**Response**
{
  "products": [ <br />
    { <br />
      "_id": { <br />
        "$oid": "5916b4cc1d41c813b1781c1a" <br />
      }, <br />
      "description": "batting", <br />
      "price": 5000, <br />
      "product_id": "fb98e6b4-b2cc-414b-92f5-9264ef0a14d4", <br />
      "user_id": "0a8aee78-2e9d-491c-8af1-1390ef50586a", <br />
      "title": "sports" <br />
    } <br />
  ], <br />
  "status": true <br />
} <br />



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
