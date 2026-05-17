"""
Management command to seed the database with sample data.

Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from books.models import Author, Category, Book


class Command(BaseCommand):
    """Seeds the database with sample authors, categories and books."""

    help = "Seeds the database with sample library data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@libratrack.example",
                password="adminpassword123",
            )
            self.stdout.write(self.style.SUCCESS("Created admin user"))
        else:
            admin = User.objects.get(username="admin")

        fiction, _ = Category.objects.get_or_create(
            name="Fiction",
            defaults={"description": "Fictional novels and short stories"},
        )
        science, _ = Category.objects.get_or_create(
            name="Science",
            defaults={"description": "Science and popular science books"},
        )

        orwell, _ = Author.objects.get_or_create(
            first_name="George", last_name="Orwell",
            defaults={"birth_year": 1903, "bio": "English novelist and essayist."},
        )
        austen, _ = Author.objects.get_or_create(
            first_name="Jane", last_name="Austen",
            defaults={"birth_year": 1775, "bio": "English novelist known for Pride and Prejudice."},
        )
        hawking, _ = Author.objects.get_or_create(
            first_name="Stephen", last_name="Hawking",
            defaults={"birth_year": 1942, "bio": "Theoretical physicist and cosmologist."},
        )

        book1, created = Book.objects.get_or_create(
            isbn="9780451524935",
            defaults={
                "title": "Nineteen Eighty-Four",
                "published_year": 1949,
                "description": "A dystopian novel set in a totalitarian society ruled by Big Brother.",
                "added_by": admin,
            },
        )
        if created:
            book1.authors.add(orwell)
            book1.categories.add(fiction)

        book2, created = Book.objects.get_or_create(
            isbn="9780141439518",
            defaults={
                "title": "Pride and Prejudice",
                "published_year": 1813,
                "description": "A romantic novel following the Bennet family and Mr Darcy.",
                "added_by": admin,
            },
        )
        if created:
            book2.authors.add(austen)
            book2.categories.add(fiction)

        book3, created = Book.objects.get_or_create(
            isbn="9780553380163",
            defaults={
                "title": "A Brief History of Time",
                "published_year": 1988,
                "description": "An exploration of cosmology, black holes and the nature of time.",
                "added_by": admin,
            },
        )
        if created:
            book3.authors.add(hawking)
            book3.categories.add(science)

        self.stdout.write(self.style.SUCCESS("Database seeded! Admin login: admin / adminpassword123"))
