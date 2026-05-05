from app import create_app
import json
app = create_app()
endpoints = sorted([r.endpoint for r in app.url_map.iter_rules()])
print(json.dumps(endpoints, indent=2))
