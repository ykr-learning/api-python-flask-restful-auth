from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

items = []


class Item(Resource):

    @jwt_required()
    def get(self, name):
        item = next(filter(lambda x: x["name"] == name, items), None)
        if item is None:
            return {'item': None}, 404
        else:
            return item

    def post(self, name):
        data = request.get_json()
        if next(filter(lambda x: x["name"] == name, items), None) is not None:
            return {
                "message": "Item with name {name} is already present".format(name=name)
            }, 409
        item = {'name': name, 'price': data["price"]}
        items.append(item)
        return item, 201

    def delete(self, name):
        item = next(filter(lambda x: x["name"] == name, items), None)
        if item is None:
            return {"item": None}, 404
        else:
            items.remove(item)
            return {'message': 'item removed'}, 204

    def put(self, name):
        data = request.get_json()

        item = next(filter(lambda x: x["name"] == name, items), None)
        if item is None:
            item = {"name": name, "price": data["price"]}
            items.append(item)
            return item, 201
        else:
            if data["price"] != item["price"]:
                item["price"] = data["price"]
                return {"message": "Price updated to " + str(data["price"])}, 204
            else:
                return {
                    "message": "Price is already at " + str(data["price"])
                }, 200


class ItemList(Resource):
    def get(self):
        return {"items": items}


def create_app():
    app = Flask(__name__)

    app.secret_key = "my_key"

    api = Api(app)
    api.add_resource(Item, '/item/<string:name>')
    api.add_resource(ItemList, '/items')

    jwt = JWT(app, authenticate, identity)


    return app


# Run this code, only with: python app.py
if __name__ == "__main__":
    app = create_app()
    app.run(port=8000, debug=True)
