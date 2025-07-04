from app import app 

# Required entry point for Vercel
def handler(environ, start_response):
    return app(environ, start_response)