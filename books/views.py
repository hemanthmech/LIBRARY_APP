"""
Views for the Library Management System.

Implements CRUD operations for Books, Authors, Categories and BorrowRecords.
Uses Django's class-based views where appropriate and function-based views
for more complex logic such as borrowing and returning books.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.views.generic import DetailView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone

from .models import Book, Author, Category, BorrowRecord
from .forms import BookForm, AuthorForm, CategoryForm, BorrowForm, BookSearchForm


# ── Book Views ────────────────────────────────────────────────────────────────

def book_list(request):
    """
    Displays a searchable, filterable list of all books.

    Supports filtering by title/author text, category, and availability status.
    """
    form = BookSearchForm(request.GET or None)
    books = Book.objects.prefetch_related("authors", "categories").all()

    if form.is_valid():
        query = form.cleaned_data.get("query")
        category = form.cleaned_data.get("category")
        status = form.cleaned_data.get("status")

        if query:
            books = books.filter(
                Q(title__icontains=query) | Q(authors__first_name__icontains=query) |
                Q(authors__last_name__icontains=query)
            ).distinct()

        if category:
            books = books.filter(categories=category)

        if status:
            books = books.filter(status=status)

    context = {
        "books": books,
        "form": form,
        "total_count": books.count(),
    }
    return render(request, "books/book_list.html", context)


def book_detail(request, pk):
    """Displays full details for a single book, including its borrow history."""
    book = get_object_or_404(Book, pk=pk)
    active_borrow = book.borrow_records.filter(returned_on__isnull=True).first()
    borrow_history = book.borrow_records.select_related("borrower").all()
    context = {
        "book": book,
        "active_borrow": active_borrow,
        "borrow_history": borrow_history,
    }
    return render(request, "books/book_detail.html", context)


@login_required
def book_create(request):
    """Handles the creation of a new book record."""
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.added_by = request.user
            book.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f'"{book.title}" has been added to the library.')
            return redirect(book.get_absolute_url())
    else:
        form = BookForm()

    return render(request, "books/book_form.html", {"form": form, "action": "Add"})


@login_required
def book_edit(request, pk):
    """Handles editing an existing book record."""
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{book.title}" has been updated.')
            return redirect(book.get_absolute_url())
    else:
        form = BookForm(instance=book)

    return render(request, "books/book_form.html", {"form": form, "book": book, "action": "Edit"})


class BookDeleteView(LoginRequiredMixin, DeleteView):
    """Handles deletion of a book record with a confirmation step."""

    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("books:book_list")

    def form_valid(self, form):
        messages.success(self.request, f'"{self.object.title}" has been removed from the library.')
        return super().form_valid(form)


# ── Author Views ──────────────────────────────────────────────────────────────

def author_list(request):
    """Displays all authors with their book counts."""
    authors = Author.objects.prefetch_related("books").all()
    return render(request, "books/author_list.html", {"authors": authors})


def author_detail(request, pk):
    """Displays a single author and their associated books."""
    author = get_object_or_404(Author, pk=pk)
    return render(request, "books/author_detail.html", {"author": author})


@login_required
def author_create(request):
    """Handles creation of a new author record."""
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, f"{author.full_name} has been added.")
            return redirect(author.get_absolute_url())
    else:
        form = AuthorForm()

    return render(request, "books/author_form.html", {"form": form, "action": "Add"})


@login_required
def author_edit(request, pk):
    """Handles editing an existing author record."""
    author = get_object_or_404(Author, pk=pk)

    if request.method == "POST":
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, f"{author.full_name} has been updated.")
            return redirect(author.get_absolute_url())
    else:
        form = AuthorForm(instance=author)

    return render(request, "books/author_form.html", {"form": form, "author": author, "action": "Edit"})


class AuthorDeleteView(LoginRequiredMixin, DeleteView):
    """Handles deletion of an author record with a confirmation step."""

    model = Author
    template_name = "books/author_confirm_delete.html"
    success_url = reverse_lazy("books:author_list")


# ── Category Views ────────────────────────────────────────────────────────────

def category_list(request):
    """Displays all book categories."""
    categories = Category.objects.prefetch_related("books").all()
    return render(request, "books/category_list.html", {"categories": categories})


def category_detail(request, pk):
    """Displays a single category and the books within it."""
    category = get_object_or_404(Category, pk=pk)
    return render(request, "books/category_detail.html", {"category": category})


@login_required
def category_create(request):
    """Handles creation of a new book category."""
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created.')
            return redirect(category.get_absolute_url())
    else:
        form = CategoryForm()

    return render(request, "books/category_form.html", {"form": form, "action": "Add"})


@login_required
def category_edit(request, pk):
    """Handles editing an existing category."""
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated.')
            return redirect(category.get_absolute_url())
    else:
        form = CategoryForm(instance=category)

    return render(request, "books/category_form.html", {"form": form, "category": category, "action": "Edit"})


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Handles deletion of a category with a confirmation step."""

    model = Category
    template_name = "books/category_confirm_delete.html"
    success_url = reverse_lazy("books:category_list")


# ── Borrow / Return Views ─────────────────────────────────────────────────────

@login_required
def borrow_book(request, pk):
    """
    Handles the borrowing of a book by the currently logged-in user.

    Checks that the book is available before creating a BorrowRecord.
    """
    book = get_object_or_404(Book, pk=pk)

    if not book.is_available:
        messages.error(request, f'"{book.title}" is not currently available.')
        return redirect(book.get_absolute_url())

    if request.method == "POST":
        form = BorrowForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.book = book
            record.borrower = request.user
            record.save()

            # Update the book status to borrowed
            book.status = Book.STATUS_BORROWED
            book.save()

            messages.success(request, f'You have borrowed "{book.title}". Due: {record.due_date}.')
            return redirect(book.get_absolute_url())
    else:
        form = BorrowForm()

    return render(request, "books/borrow_form.html", {"form": form, "book": book})


@login_required
def return_book(request, pk):
    """
    Marks a borrowed book as returned.

    Only the borrower or a staff member may return a book.
    """
    record = get_object_or_404(BorrowRecord, pk=pk, returned_on__isnull=True)

    # Only allow the borrower or staff to perform a return
    if record.borrower != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorised to return this book.")
        return redirect("books:book_list")

    if request.method == "POST":
        record.returned_on = timezone.now().date()
        record.save()

        # Mark the book as available again
        record.book.status = Book.STATUS_AVAILABLE
        record.book.save()

        messages.success(request, f'"{record.book.title}" has been returned. Thank you!')
        return redirect(record.book.get_absolute_url())

    return render(request, "books/return_confirm.html", {"record": record})


@login_required
def my_books(request):
    """Displays the currently logged-in user's active and past borrows."""
    active = BorrowRecord.objects.filter(borrower=request.user, returned_on__isnull=True)
    history = BorrowRecord.objects.filter(borrower=request.user, returned_on__isnull=False)
    return render(request, "books/my_books.html", {"active": active, "history": history})
