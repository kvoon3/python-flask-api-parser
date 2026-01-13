import ast
import json
import sys
from pathlib import Path


class FlaskRestfulVisitor(ast.NodeVisitor):
    def __init__(self):
        self.flask_restful_imports = []
        self.api_instance = None
        self.resources = []
        self.routes = []
        self._loop_vars = {}
        self._named_tuples = {}

    def visit_ImportFrom(self, node):
        if node.module and 'flask_restful' in node.module:
            for alias in node.names:
                self.flask_restful_imports.append(alias.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Check for api = Api(app) pattern
        if len(node.targets) == 1 and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Name) and call.func.id == 'Api':
                var_name = node.targets[0].id
                app_arg = None
                if call.args:
                    app_arg = ast.unparse(call.args[0])
                self.api_instance = {'var_name': var_name, 'app_arg': app_arg}

        # Track named tuples/lists for resource lists
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            if isinstance(node.value, (ast.Tuple, ast.List)):
                self._named_tuples[var_name] = node.value

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Check if class inherits from Resource
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(ast.unparse(base))

        if 'Resource' in bases:
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in ('get', 'post', 'put', 'delete', 'patch', 'options', 'head'):
                    methods.append(item.name)
            self.resources.append({'name': node.name, 'methods': methods})
        self.generic_visit(node)

    def visit_For(self, node):
        # Track loop variables and resolve add_resource calls inside loops
        original_vars = dict(self._loop_vars)

        # Extract loop structure: for resource, url in [(Resource, '/path'), ...]
        if isinstance(node.target, ast.Tuple):
            var_names = [elt.id for elt in node.target.elts if isinstance(elt, ast.Name)]

            # Get the iterable source
            iter_source = None
            if isinstance(node.iter, ast.Name):
                iter_source = self._named_tuples.get(node.iter.id)
            elif isinstance(node.iter, (ast.List, ast.Tuple)):
                iter_source = node.iter

            # For each iteration, set variables and visit body
            if iter_source:
                for elt in iter_source.elts:
                    if isinstance(elt, ast.Tuple) and len(elt.elts) >= 2:
                        for i, var_name in enumerate(var_names):
                            if i < len(elt.elts):
                                self._loop_vars[var_name] = ast.unparse(elt.elts[i])

                        # Visit loop body for this iteration
                        for body_node in node.body:
                            self.visit(body_node)

        # Restore original loop variables
        self._loop_vars = original_vars

    def visit_Call(self, node):
        # Check for api.add_resource calls
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'add_resource':
                self._extract_add_resource(node)
        self.generic_visit(node)

    def _extract_add_resource(self, node):
        if len(node.args) >= 2:
            resource_arg = ast.unparse(node.args[0])
            path_arg = ast.unparse(node.args[1])

            # Resolve loop variables if present
            resource = self._loop_vars.get(resource_arg, resource_arg)
            path = self._loop_vars.get(path_arg, path_arg)

            route = {'resource': resource, 'path': path}

            # Check for endpoint keyword argument
            for kw in node.keywords:
                if kw.arg == 'endpoint':
                    route['endpoint'] = ast.unparse(kw.value)

            self.routes.append(route)

    def to_dict(self):
        return {
            'flask_restful_imports': self.flask_restful_imports,
            'api_instance': self.api_instance,
            'resources': self.resources,
            'routes': self.routes
        }


def analyze_file(filepath):
    with open(filepath, 'r') as f:
        source = f.read()

    tree = ast.parse(source)
    visitor = FlaskRestfulVisitor()
    visitor.visit(tree)

    return {
        'file': str(filepath),
        **visitor.to_dict()
    }


def scan_directory(root_path):
    results = []
    for py_file in Path(root_path).rglob('*.py'):
        result = analyze_file(py_file)
        if result['flask_restful_imports'] or result['resources'] or result['routes']:
            results.append(result)
    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python analyze_flask_restful.py <file_or_directory>')
        sys.exit(1)

    target = sys.argv[1]
    path = Path(target)

    if path.is_file():
        result = analyze_file(path)
        print(json.dumps(result, indent=2))
    elif path.is_dir():
        results = scan_directory(path)
        print(json.dumps(results, indent=2))
    else:
        print(f'Error: {target} is not a valid file or directory')
        sys.exit(1)