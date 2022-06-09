from app import create_app
import pytest

CONTENT_TYPE_APPLICATION_JSON = 'application/json'

REQUEST_ITEM_NAME = "/item/{name}"


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


def get_auth_token(client):
    response_post_auth = client.post("/auth", content_type=CONTENT_TYPE_APPLICATION_JSON,
                           json={"username": "user1", "password":"azerty"}, follow_redirects=True)
    token = response_post_auth.get_json()['access_token']
    return token

def test_request_items(client):
    response = client.get("/items")
    assert b'"items": []' in response.data
    assert response.status_code == 200


def test_request_item_not_exists(client):
    response = client.get("/item/fake", headers={'Authorization': 'JWT {token}'.format(token=get_auth_token(client))})
    assert b'"item": null' in response.data
    assert response.status_code == 404


def test_post_item(client):
    name = "piano"
    price = 15

    response = client.post(REQUEST_ITEM_NAME.format(name=name), content_type=CONTENT_TYPE_APPLICATION_JSON,
                           json={"name": name, "price": price}, follow_redirects=True)
    assert response.status_code == 201

    response_get = client.get(REQUEST_ITEM_NAME.format(name=name), headers={'Authorization': 'JWT {token}'.format(token=get_auth_token(client))})

    assert name == response_get.get_json()['name']
    assert price == response_get.get_json()['price']

    assert response_get.status_code == 200


def test_put_item(client):
    name = "guitare"
    price1 = 15
    price2 = 20
    price3 = price2

    response_put1 = client.put(REQUEST_ITEM_NAME.format(name=name), content_type=CONTENT_TYPE_APPLICATION_JSON,
                               json={"name": name, "price": price1}, follow_redirects=True)
    assert response_put1.status_code == 201

    assert name == response_put1.get_json()['name']
    assert price1 == response_put1.get_json()['price']

    response_put2 = client.put(REQUEST_ITEM_NAME.format(name=name), content_type=CONTENT_TYPE_APPLICATION_JSON,
                               json={"name": name, "price": price2}, follow_redirects=True)
    assert response_put2.status_code == 204
    # The http status 204, block retrieving other information, so, we will test if that is pushed with a get.

    response_get2 = client.get(REQUEST_ITEM_NAME.format(name=name), headers={'Authorization': 'JWT {token}'.format(token=get_auth_token(client))})
    assert name == response_get2.get_json()['name']
    assert price2 == response_get2.get_json()['price']

    response_put3 = client.put(REQUEST_ITEM_NAME.format(name=name), content_type=CONTENT_TYPE_APPLICATION_JSON,
                               json={"name": name, "price": price3}, follow_redirects=True)
    assert response_put3.status_code == 200

    assert "Price is already at {price}".format(
        price=price3) in str(response_put3.data)

    response_get3 = client.get(REQUEST_ITEM_NAME.format(name=name), headers={'Authorization': 'JWT {token}'.format(token=get_auth_token(client))})
    assert name == response_get3.get_json()['name']
    assert price3 == response_get3.get_json()['price']


def test_delete_item(client):
    name = "violon"
    price = 15

    response = client.post(REQUEST_ITEM_NAME.format(name=name), content_type=CONTENT_TYPE_APPLICATION_JSON,
                           json={"name": name, "price": price}, follow_redirects=True)
    assert response.status_code == 201

    response_get = client.get(REQUEST_ITEM_NAME.format(name=name), headers={'Authorization': 'JWT {token}'.format(token=get_auth_token(client))})
    assert response_get.status_code == 200

    response_delete = client.delete(REQUEST_ITEM_NAME.format(name=name))
    assert response_delete.status_code == 204

    response_get = client.get(REQUEST_ITEM_NAME.format(name=name), headers={'Authorization': 'JWT {token}'.format(token=get_auth_token(client))})
    assert response_get.status_code == 404
