from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/booksdb")
client = MongoClient(MONGO_URI)
db = client.get_database("booksdb")
books_collection = db.get_collection("books")

# Helper function to format MongoDB document
def format_book(book):
    return {
        "id": str(book["_id"]),
        "title": book["title"],
        "author": book["author"]
    }

# Route to get all books
@app.route('/books', methods=['GET'])
def get_books():
    books = books_collection.find()
    return jsonify([format_book(book) for book in books]), 200

# Route to add a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    if not data.get("title") or not data.get("author"):
        return jsonify({"error": "Title and Author are required"}), 400
    new_book = {"title": data["title"], "author": data["author"]}
    result = books_collection.insert_one(new_book)
    return jsonify(format_book(books_collection.find_one({"_id": result.inserted_id}))), 201

# Route to update a book
@app.route('/books/<string:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    if not data.get("title") or not data.get("author"):
        return jsonify({"error": "Title and Author are required"}), 400
    updated_book = {"title": data["title"], "author": data["author"]}
    result = books_collection.update_one({"_id": ObjectId(book_id)}, {"$set": updated_book})
    if result.matched_count == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book updated"}), 200

# Route to delete a book
@app.route('/books/<string:book_id>', methods=['DELETE'])
def delete_book(book_id):
    result = books_collection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book deleted"}), 200

# Route to search for books
@app.route('/books/search', methods=['GET'])
def search_books():
    query = request.args.get("query", "")
    books = books_collection.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"author": {"$regex": query, "$options": "i"}}
        ]
    })
    return jsonify([format_book(book) for book in books]), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)