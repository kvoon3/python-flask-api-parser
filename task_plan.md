# Task Plan: Flask-RESTful AST Analyzer

## Goal
Create a Python AST-based analyzer script that scans Python files to extract Flask-RESTful patterns:
- flask_restful imports (Api, Resource)
- Api instantiation: `apiVarName = Api(appName)`
- Resource class definitions
- API URL registrations via `add_resource`

## Requirements
- Generic script that can scan all Python files
- Concise code, no over-engineering
- Natural code comments only
- Output as JSON

## Phases

### Phase 1: Design Analyzer Structure
- [x] Define AST visitor class to traverse the code
- [x] Track imports from flask_restful
- [x] Track Api instantiation
- [x] Track Resource class definitions
- [x] Track add_resource calls (direct and loop-based)

### Phase 2: Implement Script
- [x] Write AST analyzer
- [x] Add file scanning capability
- [x] Add JSON output formatting

### Phase 3: Test
- [x] Test with test/test.py
- [x] Verify JSON output matches expected structure

## Expected Output Structure
```json
{
  "file": "path/to/file.py",
  "flask_restful_imports": ["Api", "Resource"],
  "api_instance": {
    "var_name": "api",
    "app_arg": "app"
  },
  "resources": [
    {"name": "UserResource", "methods": ["get", "post"]}
  ],
  "routes": [
    {"resource": "UserResource", "path": "/users"},
    {"resource": "ProductResource", "path": "/api/v1/products"},
    {"resource": "OrderResource", "path": "/api/v1/orders"},
    {"resource": "UserResource", "path": "/api/v2/users", "endpoint": "v2_users"}
  ]
}
```

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|