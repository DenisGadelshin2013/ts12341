
from flask import Flask, request
from bot import handle_update

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot is live"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    return handle_update(update)
