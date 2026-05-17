"""
Forms for the Library Management System.

Uses Django ModelForms with crispy-forms for Bootstrap 5 rendering.
Each form validates its data and provides user-friendly error messages.
"""

from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

from .models import Book, Author, Category, BorrowRecord


class BookForm(forms.ModelForm):
    """Form for creating and editing Book records."""

    class Meta:
        model = Book
        fields = ["title", "authors", "categories", "isbn", "published_year", "description", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "authors": forms.CheckboxSelectMultiple(),
            "categories": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("title"),
            Row(
                Column("isbn", css_class="col-md-6"),
                Column("published_year", css_class="col-md-6"),
            ),
            "authors",
            "categories",
            "description",
            "status",
            Submit("submit", "Save Book", css_class="btn btn-primary mt-3"),
        )

    def clean_isbn(self):
        """Validates that the ISBN contains only digits and is 10 or 13 characters long."""
        isbn = self.cleaned_data.get("isbn", "").strip()
        digits_only = isbn.replace("-", "")
        if not digits_only.isdigit():
            raise forms.ValidationError("ISBN must contain only digits.")
        if len(digits_only) not in (10, 13):
            raise forms.ValidationError("ISBN must be 10 or 13 digits long.")
        return digits_only

    def clean_published_year(self):
        """Validates that the published year is a plausible value."""
        year = self.cleaned_data.get("published_year")
        current_year = timezone.now().year
        if year and (year < 1000 or year > current_year + 1):
            raise forms.ValidationError(f"Enter a year between 1000 and {current_year + 1}.")
        return year


class AuthorForm(forms.ModelForm):
    """Form for creating and editing Author records."""

    class Meta:
        model = Author
        fields = ["first_name", "last_name", "bio", "birth_year"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("first_name", css_class="col-md-6"),
                Column("last_name", css_class="col-md-6"),
            ),
            "birth_year",
            "bio",
            Submit("submit", "Save Author", css_class="btn btn-primary mt-3"),
        )

    def clean_birth_year(self):
        """Validates that the birth year is a plausible value if provided."""
        year = self.cleaned_data.get("birth_year")
        current_year = timezone.now().year
        if year and (year < 1800 or year > current_year):
            raise forms.ValidationError(f"Enter a year between 1800 and {current_year}.")
        return year


class CategoryForm(forms.ModelForm):
    """Form for creating and editing Category records."""

    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "name",
            "description",
            Submit("submit", "Save Category", css_class="btn btn-primary mt-3"),
        )


class BorrowForm(forms.ModelForm):
    """Form for recording a book loan to a user."""

    class Meta:
        model = BorrowRecord
        fields = ["due_date", "notes"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "due_date",
            "notes",
            Submit("submit", "Confirm Borrow", css_class="btn btn-success mt-3"),
        )

    def clean_due_date(self):
        """Validates that the due date is in the future."""
        due_date = self.cleaned_data.get("due_date")
        if due_date and due_date <= timezone.now().date():
            raise forms.ValidationError("Due date must be in the future.")
        return due_date


class BookSearchForm(forms.Form):
    """Simple search form for filtering books by title, author, or category."""

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Search by title or author...",
            "class": "form-control",
            "aria-label": "Search books",
        }),
        label="",
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={"class": "form-select"}),
        label="",
    )
    status = forms.ChoiceField(
        choices=[("", "Any Status")] + Book.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="",
    )
