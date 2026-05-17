"""
URL configuration for library_project.

Routes requests to the books app and Django admin.
Also includes authentication URLs for login/logout functionality.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("books.urls", namespace="books")),
]
