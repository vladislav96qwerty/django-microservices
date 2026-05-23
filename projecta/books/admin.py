from django.contrib import admin

from .models import Author, Book, Category, Review


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "birth_date", "created_at")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "isbn", "author", "price", "stock", "is_active")
    list_filter = ("is_active", "language", "categories")
    search_fields = ("title", "isbn", "author__name")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "user", "rating", "created_at")
    list_filter = ("rating",)
