import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    def getPage(request, books):
        page = request.args.get('page', 1, type=int)
        start = (page-1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF

        books = Book.query.order_by(Book.id).all()
        return [book.format() for book in books[start:end]]

    # @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars

    @app.route('/books')
    def getBooks():
        books = Book.query.order_by(Book.id).all()
        fBooks = getPage(request, books)
        if len(fBooks) == 0:
            abort(404)

        return jsonify({"success": True, "books": fBooks, "total_books": len(books)})

    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh

    @app.route('/books/<int:bookId>', methods=['PATCH'])
    def updateRating(bookId):
        body = request.get_json()

        try:
            book = Book.query.filter(Book.id == bookId).one_or_none()
            if book is None:
                abort(404)

            if 'rating' in body:
                book.rating = int(body.get('rating'))
                book.update()
                return jsonify({'success': True})
            else:
                return jsonify({'success': False})
        except:
            abort(400)
    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'

    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.
    @app.route('/books/<int:bookId>', methods=['DELETE'])
    def deleteBook(bookId):
        try:
            book = Book.query.filter(Book.id == bookId).one_or_none()
            if book is None:
                abort(404)

            book.delete()
            books = Book.query.order_by(Book.id).all()
            fBooks = getPage(request, books)
            if len(fBooks) == 0:
                abort(404)

            return jsonify({"success": True, "deleted": bookId, "books": fBooks, "total_books": len(books)})
        except:
            abort(422)

    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.
    @app.route("/books", methods=["POST"])
    def createBook():
        body = request.get_json()

        newTitle = body.get("title", None)
        newAuthor = body.get("author", None)
        newRating = body.get("rating", None)

        try:
            book = Book(title=newTitle, author=newAuthor, rating=newRating)
            book.insert()

            books = Book.query.order_by(Book.id).all()
            fBooks = getPage(request, books)

            return jsonify(
                {
                    "success": True,
                    "created": book.id,
                    "books": fBooks,
                    "total_books": len(books),
                }
            )

        except:
            abort(422)

    @app.errorhandler(404)
    def notFound(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    return app
