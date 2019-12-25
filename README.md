# E Commerce CLI-Application

## Description : <br />
This CLI Application contains CRUD items with Cart addition and deletion capability. Each operation except Search item requires user/admin credentials. In C-U-D methods authorised user only can do the operations. <br />

##  API Server <br />
*python [my_cart.py](https://github.com/nidhiojha/eCommerce_CLI/blob/cli_application/my_cart.py)* <br />


*FOR DETAILS (params) REFER [API DOCS](https://github.com/nidhiojha/eCommerce_CLI/blob/cli_application/API_DOCS.md)* <br />


### Mongo DB installation <br />
sudo apt-get install mongodb <br />

### Basic Installation Setups <br />
A) clone this repo <br />
B) cd /path/to/repo <br />
C) virtualenv venv <br />
D) . venv/eCommerce_env/activate <br />
E) pip install -r requirements.txt <br />


### Operations : <br />
For search(READ) items based on 'description', login not required <br />

*USER LEVEL OPERATIONS* <br >
A) User can Register  <br />
B) For cart operation (viz product adding to cart or removing products from cart) only authorised user can perform.<br>
C)User can by add multiple product from the cart as well as can view the coupens available at any time and can apply to it but only one at a time and can get discount based on final billing stage.Login checked in this stage as well.<br/>
D)Bill generated after checkout from cart including discounts and after applying coupen<br />

*ADMIN LEVEL OPERATIONS* <br >
A) Admin can Register  <br />
B) For add(CREATE)New Product, only Admin allowed, login checked in prelim stage. <br />
C)Admin have permission to add coupens per product as well as can modify the accessbility of the coupens per product.<br/>
D) For remove (DELETE) items, only Admin who added the item previously is allowed to delete, login checked in this stage as well <br />

