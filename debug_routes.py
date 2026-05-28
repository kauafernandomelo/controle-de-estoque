import sys; sys.path.insert(0, '.')
from src.main import create_app
app = create_app()

for i, r in enumerate(app.routes):
    t = type(r).__name__
    methods = getattr(r, 'methods', None)
    print(f'{i}: [{t}] path={r.path!r} methods={methods}')

print()
for r in app.routes:
    if r.path == '/health':
        print(f'HEALTH: {type(r).__name__} methods={getattr(r, "methods", None)}')
        from starlette.routing import Match
        scope = {'type': 'http', 'method': 'GET', 'path': '/health', 'headers': []}
        result, _ = r.matches(scope)
        print(f'  matches /health GET: {result}')
        scope2 = {'type': 'http', 'method': 'GET', 'path': '/dashboard', 'headers': []}
        result2, _ = r.matches(scope2)
        print(f'  matches /dashboard GET: {result2}')
