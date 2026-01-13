from pathlib import Path
import sys

from inline_snapshot import snapshot
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from analyze_flask_restful import analyze_file


def test_flask_restful_analysis(tmp_path):
    """Test analyzing a Flask-RESTful file with various patterns"""
    test_file = tmp_path / "flask_app.py"

    source = '''
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

# Resources defined as tuples
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
'''

    test_file.write_text(source)
    result = analyze_file(test_file)

    assert result == snapshot({
    "file": "/private/var/folders/xv/1jph5b9s0295tw5n_f6spjl00000gp/T/pytest-of-kvoon/pytest-11/test_flask_restful_analysis0/flask_app.py",
    "flask_restful_imports": ["Api", "Resource"],
    "api_instance": {"var_name": "api", "app_arg": "app"},
    "resources": [
        {"name": "UserResource", "methods": ["get", "post"]},
        {"name": "ProductResource", "methods": ["get", "post"]},
        {"name": "OrderResource", "methods": ["get", "put"]},
    ],
    "routes": [
        {"resource": "UserResource", "path": "'/users'"},
        {"resource": "ProductResource", "path": "'/api/v1/products'"},
        {"resource": "OrderResource", "path": "'/api/v1/orders'"},
        {
            "resource": "UserResource",
            "path": "'/api/v2/users'",
            "endpoint": "'v2_users'",
        },
    ],
})
