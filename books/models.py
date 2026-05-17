"""
Models for the Library Management System.

Defines the data structure for books, authors, categories,
and borrowing records with appropriate relationships.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """Represents a genre or category for books (e.g. Fiction, Science)."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("books:category_detail", kwargs={"pk": self.pk})


class Author(models.Model):
    """Represents a book author with optional biographical details."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_year = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("books:author_detail", kwargs={"pk": self.pk})

    @property
    def full_name(self):
        """Returns the author's full name as a single string."""
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    """
    Central model representing a book in the library.

    Relates to Author (many-to-many) and Category (many-to-many).
    Tracks availability for borrowing.
    """

    STATUS_AVAILABLE = "available"
    STATUS_BORROWED = "borrowed"
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_BORROWED, "Borrowed"),
    ]

    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author, related_name="books")
    categories = models.ManyToManyField(Category, related_name="books", blank=True)
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    published_year = models.IntegerField()
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
    )
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_books",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("books:book_detail", kwargs={"pk": self.pk})

    @property
    def is_available(self):
        """Returns True if the book can be borrowed."""
        return self.status == self.STATUS_AVAILABLE

    def author_names(self):
        """Returns a comma-separated string of all author names."""
        return ", ".join(str(a) for a in self.authors.all())


class BorrowRecord(models.Model):
    """
    Tracks the borrowing history for each book.

    Links a User to a Book with borrow and return dates.
    """

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrow_records")
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrow_records")
    borrowed_on = models.DateField(default=timezone.now)
    due_date = models.DateField()
    returned_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-borrowed_on"]

    def __str__(self):
        return f"{self.book.title} — {self.borrower.username}"

    @property
    def is_overdue(self):
        """Returns True if the book has not been returned and is past its due date."""
        if self.returned_on:
            return False
        return timezone.now().date() > self.due_date

    @property
    def is_returned(self):
        """Returns True if the book has been returned."""
        return self.returned_on is not None
