# E Commerce CLI-Application

## Description : <br />
This CLI Application contains CRUD items with Cart addition and deletion capability. Each operation except Search item requires user/admin credentials. In C-U-D methods authorised user only can do the operations. <br />

##  API Server <br />
*python [my_cart.py](https://github.com/nidhiojha/eCommerce_CLI/blob/cli_application/my_cart.py)* <br />


*FOR DETAILS (params) REFER [API DOCS](https://github.com/nidhiojha/eCommerce_CLI/blob/cli_application/API_DOCS.md)* <br />

*FOR all test cases REFER [Test Cases](https://github.com/nidhiojha/eCommerce_CLI/blob/cli_application/test_cases.py)* <br />

### Mongo DB installation <br />
sudo apt-get install mongodb <br />

### Basic Installation Setups <br />
A) clone this repo <br />
B) cd /path/to/repo <br />
C) virtualenv venv <br />
D) . venv/eCommerce_env/activate <br />
E) pip install -r requirements.txt <br />


### Operations : <br />
A) Register user as admin or user <br />
B) For add(CREATE)New Items, only Admin allowed, login checked in prelim stage. <br />
C) For search(READ) items based on 'title', login not required <br />
D) For changes (UPDATE) items, only Admin who add the item previously is allowed, login checked in this stage as well <br />
E) For remove (DELETE) items, only Admin who added the item previously is allowed to delete, login checked in this stage as       well <br />
F) For cart operation (viz product adding to cart or removing products from cart) only user can perform, login checked in this stage as well <br />

