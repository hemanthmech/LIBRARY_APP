"""
Automated test suite for the Library Management System.

Tests cover:
- Models (data integrity, properties, relationships)
- Forms (validation, error handling)
- Views (CRUD operations, HTTP responses, authentication)
- Borrowing logic (availability, return flow)

Run with: python manage.py test books
Or with coverage: coverage run manage.py test books && coverage report
"""

from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import Book, Author, Category, BorrowRecord
from .forms import BookForm, BorrowForm


# ── Model Tests ───────────────────────────────────────────────────────────────

class CategoryModelTest(TestCase):
    """Tests for the Category model."""

    def setUp(self):
        self.category = Category.objects.create(
            name="Fiction",
            description="Fictional works",
        )

    def test_str_returns_name(self):
        """Category __str__ should return its name."""
        self.assertEqual(str(self.category), "Fiction")

    def test_absolute_url(self):
        """Category get_absolute_url should return a valid URL."""
        url = self.category.get_absolute_url()
        self.assertIn(str(self.category.pk), url)


class AuthorModelTest(TestCase):
    """Tests for the Author model."""

    def setUp(self):
        self.author = Author.objects.create(
            first_name="Jane",
            last_name="Austen",
            birth_year=1775,
        )

    def test_str_returns_full_name(self):
        """Author __str__ should return first and last name."""
        self.assertEqual(str(self.author), "Jane Austen")

    def test_full_name_property(self):
        """Author full_name property should concatenate names."""
        self.assertEqual(self.author.full_name, "Jane Austen")

    def test_absolute_url(self):
        """Author get_absolute_url should return a valid URL."""
        url = self.author.get_absolute_url()
        self.assertIn(str(self.author.pk), url)


class BookModelTest(TestCase):
    """Tests for the Book model and its properties."""

    def setUp(self):
        self.author = Author.objects.create(first_name="George", last_name="Orwell")
        self.book = Book.objects.create(
            title="Nineteen Eighty-Four",
            isbn="9780451524935",
            published_year=1949,
            status=Book.STATUS_AVAILABLE,
        )
        self.book.authors.add(self.author)

    def test_str_returns_title(self):
        """Book __str__ should return the book title."""
        self.assertEqual(str(self.book), "Nineteen Eighty-Four")

    def test_is_available_true_when_status_available(self):
        """is_available should be True when status is 'available'."""
        self.assertTrue(self.book.is_available)

    def test_is_available_false_when_status_borrowed(self):
        """is_available should be False when status is 'borrowed'."""
        self.book.status = Book.STATUS_BORROWED
        self.book.save()
        self.assertFalse(self.book.is_available)

    def test_author_names_returns_string(self):
        """author_names should return a comma-separated string of authors."""
        self.assertIn("George Orwell", self.book.author_names())


class BorrowRecordModelTest(TestCase):
    """Tests for the BorrowRecord model."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.book = Book.objects.create(
            title="Test Book",
            isbn="1234567890",
            published_year=2000,
        )
        self.today = timezone.now().date()
        self.record = BorrowRecord.objects.create(
            book=self.book,
            borrower=self.user,
            borrowed_on=self.today,
            due_date=self.today + timedelta(days=14),
        )

    def test_str_includes_book_and_user(self):
        """BorrowRecord __str__ should include book title and username."""
        result = str(self.record)
        self.assertIn("Test Book", result)
        self.assertIn("testuser", result)

    def test_is_not_overdue_before_due_date(self):
        """is_overdue should be False when due date is in the future."""
        self.assertFalse(self.record.is_overdue)

    def test_is_overdue_after_due_date(self):
        """is_overdue should be True when due date has passed without return."""
        self.record.due_date = self.today - timedelta(days=1)
        self.record.save()
        self.assertTrue(self.record.is_overdue)

    def test_is_not_overdue_if_returned(self):
        """is_overdue should be False even past due date if book was returned."""
        self.record.due_date = self.today - timedelta(days=1)
        self.record.returned_on = self.today
        self.record.save()
        self.assertFalse(self.record.is_overdue)

    def test_is_returned_false_when_no_return_date(self):
        """is_returned should be False when returned_on is None."""
        self.assertFalse(self.record.is_returned)

    def test_is_returned_true_when_return_date_set(self):
        """is_returned should be True when returned_on is set."""
        self.record.returned_on = self.today
        self.record.save()
        self.assertTrue(self.record.is_returned)


# ── Form Tests ────────────────────────────────────────────────────────────────

class BookFormTest(TestCase):
    """Tests for BookForm validation logic."""

    def setUp(self):
        self.author = Author.objects.create(first_name="Test", last_name="Author")

    def _form_data(self, **kwargs):
        base = {
            "title": "Valid Title",
            "isbn": "9780451524935",
            "published_year": 2000,
            "authors": [self.author.pk],
            "status": Book.STATUS_AVAILABLE,
        }
        base.update(kwargs)
        return base

    def test_valid_form(self):
        """Form should be valid with correct data."""
        form = BookForm(data=self._form_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_isbn_must_be_numeric(self):
        """Form should reject ISBNs containing non-digit characters."""
        form = BookForm(data=self._form_data(isbn="NOTANISBN"))
        self.assertFalse(form.is_valid())
        self.assertIn("isbn", form.errors)

    def test_isbn_must_be_10_or_13_digits(self):
        """Form should reject ISBNs of incorrect length."""
        form = BookForm(data=self._form_data(isbn="123"))
        self.assertFalse(form.is_valid())
        self.assertIn("isbn", form.errors)

    def test_published_year_cannot_be_in_far_future(self):
        """Form should reject published years too far in the future."""
        form = BookForm(data=self._form_data(published_year=9999))
        self.assertFalse(form.is_valid())
        self.assertIn("published_year", form.errors)


class BorrowFormTest(TestCase):
    """Tests for BorrowForm validation logic."""

    def test_due_date_must_be_in_future(self):
        """Form should reject due dates that are today or in the past."""
        form = BorrowForm(data={"due_date": date.today().isoformat()})
        self.assertFalse(form.is_valid())
        self.assertIn("due_date", form.errors)

    def test_valid_future_due_date(self):
        """Form should accept a due date in the future."""
        future = (date.today() + timedelta(days=7)).isoformat()
        form = BorrowForm(data={"due_date": future})
        self.assertTrue(form.is_valid(), form.errors)


# ── View Tests ────────────────────────────────────────────────────────────────

class BookListViewTest(TestCase):
    """Tests for the book list / home view."""

    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(first_name="H.G.", last_name="Wells")
        self.book = Book.objects.create(
            title="The Time Machine",
            isbn="9780486284729",
            published_year=1895,
        )
        self.book.authors.add(self.author)

    def test_book_list_returns_200(self):
        """Book list view should return HTTP 200."""
        response = self.client.get(reverse("books:book_list"))
        self.assertEqual(response.status_code, 200)

    def test_book_appears_in_list(self):
        """Book title should appear in the rendered book list page."""
        response = self.client.get(reverse("books:book_list"))
        self.assertContains(response, "The Time Machine")

    def test_search_filters_results(self):
        """Search query should filter books by title."""
        response = self.client.get(reverse("books:book_list"), {"query": "Time"})
        self.assertContains(response, "The Time Machine")

    def test_search_excludes_non_matching(self):
        """Search query should exclude non-matching books."""
        response = self.client.get(reverse("books:book_list"), {"query": "zzznomatch"})
        self.assertNotContains(response, "The Time Machine")


class BookDetailViewTest(TestCase):
    """Tests for the book detail view."""

    def setUp(self):
        self.client = Client()
        self.book = Book.objects.create(
            title="Dune",
            isbn="9780441013593",
            published_year=1965,
        )

    def test_book_detail_returns_200(self):
        """Book detail view should return HTTP 200 for an existing book."""
        response = self.client.get(reverse("books:book_detail", kwargs={"pk": self.book.pk}))
        self.assertEqual(response.status_code, 200)

    def test_book_detail_returns_404_for_missing_book(self):
        """Book detail view should return HTTP 404 for a non-existent book."""
        response = self.client.get(reverse("books:book_detail", kwargs={"pk": 99999}))
        self.assertEqual(response.status_code, 404)


class BookCreateViewTest(TestCase):
    """Tests for the book creation view (requires authentication)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="creator", password="pass123")
        self.author = Author.objects.create(first_name="Test", last_name="Author")

    def test_create_redirects_unauthenticated_users(self):
        """Anonymous users should be redirected to login."""
        response = self.client.get(reverse("books:book_create"))
        self.assertRedirects(response, f"/accounts/login/?next=/books/add/")

    def test_authenticated_user_can_access_create_form(self):
        """Logged-in users should see the create form."""
        self.client.login(username="creator", password="pass123")
        response = self.client.get(reverse("books:book_create"))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_create_book(self):
        """Logged-in users should be able to POST a new book."""
        self.client.login(username="creator", password="pass123")
        data = {
            "title": "New Book",
            "isbn": "9781234567897",
            "published_year": 2023,
            "authors": [self.author.pk],
            "status": Book.STATUS_AVAILABLE,
        }
        response = self.client.post(reverse("books:book_create"), data)
        self.assertEqual(Book.objects.filter(title="New Book").count(), 1)


class BorrowReturnFlowTest(TestCase):
    """Integration tests for the borrow and return book workflow."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="borrower", password="pass123")
        self.book = Book.objects.create(
            title="Borrowed Book",
            isbn="1111111111",
            published_year=2020,
            status=Book.STATUS_AVAILABLE,
        )

    def test_borrow_book_marks_it_as_borrowed(self):
        """Borrowing a book should update its status to 'borrowed'."""
        self.client.login(username="borrower", password="pass123")
        future = (date.today() + timedelta(days=14)).isoformat()
        self.client.post(
            reverse("books:borrow_book", kwargs={"pk": self.book.pk}),
            {"due_date": future},
        )
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, Book.STATUS_BORROWED)

    def test_cannot_borrow_unavailable_book(self):
        """Borrowing a book that is already borrowed should redirect with an error."""
        self.book.status = Book.STATUS_BORROWED
        self.book.save()
        self.client.login(username="borrower", password="pass123")
        response = self.client.get(reverse("books:borrow_book", kwargs={"pk": self.book.pk}))
        self.assertRedirects(response, self.book.get_absolute_url())

    def test_return_book_marks_it_as_available(self):
        """Returning a book should update its status back to 'available'."""
        self.client.login(username="borrower", password="pass123")
        record = BorrowRecord.objects.create(
            book=self.book,
            borrower=self.user,
            borrowed_on=date.today(),
            due_date=date.today() + timedelta(days=14),
        )
        self.book.status = Book.STATUS_BORROWED
        self.book.save()

        self.client.post(reverse("books:return_book", kwargs={"pk": record.pk}))
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, Book.STATUS_AVAILABLE)
