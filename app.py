from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "Jarvis Cloud Engine Running", "message": "System Online"})

@app.route("/command", methods=["POST"])
def command():
    data = request.json
    user_query = data.get("query", "")
    
    # Logic handling
    reply = f"Jarvis processed: {user_query}"
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
  
