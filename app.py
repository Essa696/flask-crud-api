from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS
DATABASE = 'books.db'

# Initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS books (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            author TEXT NOT NULL
                        )''')
        
@app.route('/')
def home():
    return "Welcome to the Flask CRUD API! Use the /books endpoint."        

@app.route('/books', methods=['GET'])
def get_books():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = [{"id": row[0], "title": row[1], "author": row[2]} for row in cursor.fetchall()]
    return jsonify(books)

@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    title = data.get('title')
    author = data.get('author')
    if not title or not author:
        return jsonify({"error": "Title and Author are required"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        conn.commit()
        book_id = cursor.lastrowid

    return jsonify({"id": book_id, "title": title, "author": author}), 201

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book deleted"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)