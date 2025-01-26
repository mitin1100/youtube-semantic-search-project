import os
from flask import Flask, render_template, request, jsonify, abort
from query_search import query_search
from pymongo import MongoClient

app = Flask(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

client = MongoClient(
    "FILL YOUR MONGO URI"
    )
db = client.myDatabase
collection = db.myCollection

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    query = request.form["query"]
    title, summary, similarity, speaker, url = query_search(query, collection)
    # print(url)
    return jsonify({
        "title": title,
        "summary": summary,
        "similarity": similarity,
        "speaker": speaker,
        "url": url
    })



if __name__ == "__main__":

    app.run(host="0.0.0.0", debug=True)
    
