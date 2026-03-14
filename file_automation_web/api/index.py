from flask import Flask, jsonify
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Hello from Flask on Vercel!"})

# Vercel expects a callable named 'app'
# If running locally, you can still use flask run
if __name__ == "__main__":
    run_simple("0.0.0.0", 5000, app)
