from flask import Flask,jsonify,request
from pymongo import MongoClient
from bson import ObjectId
import uuid
import time
import random


def generate_order_id():
    return str(uuid.uuid4())

def generate_order_id():
    timestamp = str(int(time.time()))
    random_num = str(random.randint(1000, 9999))
    return timestamp + random_num

app = Flask(__name__)

client = MongoClient("mongodb+srv://abha25meshram:abha@cluster0.3spxr7d.mongodb.net/zomato?retryWrites=true&w=majority")
db = client["Zomato"]


@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/menu', methods=['POST'])
def create_menu_item():
    data = request.get_json()
    dish_id = data["dish_id"]
    name = data['name']
    price = data['price']
    stock=data["stock"]
    availability = data['availability']
    menu_item = {"dish_id": dish_id, 'name': name, 'price': price, 'stock':stock,'availability': availability}
    result = db.menu.insert_one(menu_item)
    menu_item["_id"] = str(result.inserted_id)
    
    return jsonify({"message": "Dish added successfully!", "menu_item": menu_item}), 201


@app.route("/menu/<int:dish_id>", methods=["DELETE"])
def remove_dish(dish_id):
    result = db.menu.delete_one({"dish_id": dish_id})
    if result.deleted_count > 0:
        return "Dish removed from the menu."
    else:
        return "Dish not found in the menu."

    

@app.route("/menu/<int:dish_id>", methods=["PUT"])
def update_availability(dish_id):
    dish = db.menu.find_one({"dish_id": dish_id})
    if dish:
        current_availability = dish["availability"]
        new_availability = "no" if current_availability == "yes" else "yes"
        result = db.menu.update_one({"dish_id": dish_id}, {"$set": {"availability": new_availability}})
        if result.modified_count > 0:
            return "Availability updated."
        else:
            return "Failed to update availability."
    else:
        return "Dish not found in the menu."

    
@app.route("/orders", methods=["POST"])
def take_order():
    order = request.get_json()
    dish_ids = order.get("dish_ids", [])
    ordered_dishes = []
    total_price = 0

    if not dish_ids:
        return "No dish IDs provided.", 400

    for dish_id in dish_ids:
        dish = db.menu.find_one({"dish_id": dish_id})
        if dish and dish["availability"] == "yes" and dish["stock"] > 0:
            ordered_dishes.append(dish)
            total_price += dish["price"]
            # Decrement the stock by 1
            db.menu.update_one({"dish_id": dish_id}, {"$inc": {"stock": -1}})
        else:
            return f"Invalid dish ID: {dish_id} or dish is not available or out of stock.", 400

    order["id"] = db.order.count_documents({}) + 1
    order["dishes"] = ordered_dishes
    order["status"] = "Received"
    order["total_price"] = total_price
    db.order.insert_one(order)

    return "Order placed successfully."





if __name__ == '__main__':
    app.run(debug=True)
