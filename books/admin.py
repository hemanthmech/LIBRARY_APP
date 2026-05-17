"""
Django admin configuration for the Library Management System.

Registers all models with customised list displays and filters
for efficient back-end management.
"""

from django.contrib import admin
from .models import Book, Author, Category, BorrowRecord


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "birth_year"]
    search_fields = ["first_name", "last_name"]
    ordering = ["last_name"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author_names", "isbn", "published_year", "status"]
    list_filter = ["status", "categories"]
    search_fields = ["title", "isbn", "authors__last_name"]
    filter_horizontal = ["authors", "categories"]

    def author_names(self, obj):
        return obj.author_names()
    author_names.short_description = "Authors"


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ["book", "borrower", "borrowed_on", "due_date", "returned_on", "is_overdue"]
    list_filter = ["returned_on"]
    search_fields = ["book__title", "borrower__username"]
    date_hierarchy = "borrowed_on"

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = "Overdue?"
