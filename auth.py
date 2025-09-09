from flask import request, Response
import os

GEN_AUTH_USER = os.getenv("GEN_AUTH_USER")
GEN_AUTH_PASS = os.getenv("GEN_AUTH_PASS")

def check_auth(username, password):
    """Check if a username/password pair is valid."""
    return username == GEN_AUTH_USER and password == GEN_AUTH_PASS

def authenticate():
    """Send a 401 to trigger browser's basic auth dialog."""
    return Response(
        "Authentication required", 401,
        {"WWW-Authenticate": 'Basic realm="Capybara Party"'}
    )

def requires_auth(f):
    """Decorator to protect routes with basic auth."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated