# Python Flask API Parser

A tool for analyzing Flask-RESTful applications using Python's Abstract Syntax Tree (AST).

## Features

- Detects Flask-RESTful imports (`Api`, `Resource`)
- Identifies API instances and their app arguments
- Extracts Resource classes and their HTTP methods
- Parses route definitions from `add_resource()` calls
- Supports loop-based route registration patterns

## Installation

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Analyze a single file:
```bash
python analyze_flask_restful.py path/to/file.py
```

### Analyze a directory:
```bash
python analyze_flask_restful.py path/to/directory
```

### Example output:
```json
{
  "file": "app.py",
  "flask_restful_imports": ["Api", "Resource"],
  "api_instance": {
    "var_name": "api",
    "app_arg": "app"
  },
  "resources": [
    {"name": "UserResource", "methods": ["get", "post"]}
  ],
  "routes": [
    {"resource": "UserResource", "path": "'/users'"}
  ]
}
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific test:
```bash
pytest test/test_analyze_flask_restful.py
```

### Updating Snapshots

This project uses `inline-snapshot` for testing. To update snapshot values:

```bash
pytest --inline-snapshot=fix
```

For interactive review of snapshot changes:
```bash
pytest --inline-snapshot=review
```

## License

MIT
