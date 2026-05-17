"""
URL patterns for the books application.

Provides named routes for all book, author, category,
and borrowing-related views.
"""

from django.urls import path
from . import views

app_name = "books"

urlpatterns = [
    # Home / book list
    path("", views.book_list, name="book_list"),

    # Book CRUD
    path("books/add/", views.book_create, name="book_create"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/edit/", views.book_edit, name="book_edit"),
    path("books/<int:pk>/delete/", views.BookDeleteView.as_view(), name="book_delete"),

    # Borrowing
    path("books/<int:pk>/borrow/", views.borrow_book, name="borrow_book"),
    path("borrow/<int:pk>/return/", views.return_book, name="return_book"),
    path("my-books/", views.my_books, name="my_books"),

    # Author CRUD
    path("authors/", views.author_list, name="author_list"),
    path("authors/add/", views.author_create, name="author_create"),
    path("authors/<int:pk>/", views.author_detail, name="author_detail"),
    path("authors/<int:pk>/edit/", views.author_edit, name="author_edit"),
    path("authors/<int:pk>/delete/", views.AuthorDeleteView.as_view(), name="author_delete"),

    # Category CRUD
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_create"),
    path("categories/<int:pk>/", views.category_detail, name="category_detail"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
]
