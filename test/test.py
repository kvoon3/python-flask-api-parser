from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class UserResource(Resource):
    def get(self):
        return {'users': []}

    def post(self):
        return {'status': 'created'}


api.add_resource(UserResource, '/users')

class ProductResource(Resource):
    def get(self, product_id=None):
        if product_id:
            return {'product': product_id}
        return {'products': []}

    def post(self):
        return {'status': 'created'}


class OrderResource(Resource):
    def get(self):
        return {'orders': []}

    def put(self, order_id):
        return {'order': order_id}

# 资源元组定义
default_resources = (
    (ProductResource, '/api/v1/products'),
    (OrderResource, '/api/v1/orders'),
)

for resource, url in default_resources:
    api.add_resource(resource, url)

more_resources = [
    (UserResource, '/api/v2/users'),
]

for resource, url in more_resources:

    api.add_resource(resource, url, endpoint='v2_users')
