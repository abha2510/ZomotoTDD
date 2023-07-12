import pytest
from app.app import app
import json
import uuid
from bson import ObjectId
from pymongo import MongoClient


client = MongoClient("mongodb+srv://abha25meshram:abha@cluster0.3spxr7d.mongodb.net/zomato?retryWrites=true&w=majority")
db = client["Zomato"]

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_database_connection(client):
    response = client.get('/')
    assert response.status_code == 200

def test_create_menu_item(client):
    response = client.post('/menu', json={"dish_id":1,'name': 'Pizza', 'price': 10,'stock':5,"availability": "yes"})
    assert response.status_code == 201    

def test_delete_menu_item(client):
    response = client.delete('/menu/1')
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Dish removed from the menu."


def test_update_availability(client):
    response = client.put(f'/menu/1')
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Availability updated."


def test_take_order(client):
    # Add a dish to the menu collection with dish_id = 1, availability = "yes", and stock > 0
    menu_item = {"dish_id": 1, "name": "Pizza", "price": 10, "availability": "yes", "stock": 5}
    db.menu.insert_one(menu_item)

    # Test order placement with a valid dish ID and sufficient stock
    response = client.post('/orders', json={"dish_ids": [1]})
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "Invalid dish ID: 1 or dish is not available or out of stock."

    # Test order placement with an invalid dish ID
    response = client.post('/orders', json={"dish_ids": [2]})
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "Invalid dish ID: 2 or dish is not available or out of stock."

    # Test order placement with a dish that is not available
    menu_item = {"dish_id": 2, "name": "Burger", "price": 8, "availability": "no", "stock": 3}
    db.menu.insert_one(menu_item)
    response = client.post('/orders', json={"dish_ids": [2]})
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "Invalid dish ID: 2 or dish is not available or out of stock."

    # Test order placement with a dish that is out of stock
    menu_item = {"dish_id": 3, "name": "Pasta", "price": 12, "availability": "yes", "stock": 0}
    db.menu.insert_one(menu_item)
    response = client.post('/orders', json={"dish_ids": [3]})
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "Invalid dish ID: 3 or dish is not available or out of stock."



