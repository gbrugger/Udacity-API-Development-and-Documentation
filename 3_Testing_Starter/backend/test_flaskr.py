import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Book


class BookTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "bookshelf_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )
        self.app = create_app(self.database_path)
        self.client = self.app.test_client

        self.new_book = {"title": "Anansi Boys",
                         "author": "Neil Gaiman", "rating": 5}

    def tearDown(self):
        """Executed after each test"""
        pass


# @TODO: Write at least two tests for each endpoint - one each for success and error behavior.
#        You can feel free to write additional tests for nuanced functionality,
#        Such as adding a book without a rating, etc.
#        Since there are four routes currently, you should have at least eight tests.
# Optional: Update the book information in setUp to make the test database your own!

    def test_retrieve_books(self):
        """Test retrieve books """
        res = self.client().get('http://localhost:5000/books?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_books"])
        self.assertTrue(len(data["books"]))

    def test_retrieve_books_page_not_found(self):
        """Test retrieve books """
        res = self.client().get('http://localhost:5000/books?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)

    def test_create_book(self):
        """Test create book """
        res = self.client().post('http://localhost:5000/books', json=self.new_book)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['created'])

    def test_create_book_not_allowed(self):
        res = self.client().post('/books/1000', json=self.new_book)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['success'], False)

    def test_update_book(self):
        res = self.client().patch('/books/5', json={'rating': 2})
        data = json.loads(res.data)
        with self.app.app_context():
            book = Book.query.filter(Book.id == 5).one_or_none()
            self.assertEqual(book.format()['rating'], 2)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_update_book_bad_request(self):
        res = self.client().patch('/books/1000', json={'rating': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)

    def test_delete_book(self):
        res = self.client().delete('/books/3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_book_non_existing(self):
        res = self.client().delete('/books/3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["message"], "unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
