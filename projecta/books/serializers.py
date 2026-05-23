from rest_framework import serializers

from .models import Author, Book, Category, Review


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "name", "bio", "birth_date")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ("id", "book", "user", "rating", "text", "created_at")
        read_only_fields = ("created_at",)

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class BookListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "slug",
            "isbn",
            "author_name",
            "price",
            "cover",
            "stock",
            "is_in_stock",
            "language",
        )


class BookDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "slug",
            "isbn",
            "author",
            "categories",
            "description",
            "cover",
            "price",
            "stock",
            "is_in_stock",
            "pages",
            "language",
            "publication_date",
            "is_active",
            "reviews",
            "average_rating",
            "created_at",
            "updated_at",
        )

    def get_average_rating(self, obj):
        ratings = [r.rating for r in obj.reviews.all()]
        return round(sum(ratings) / len(ratings), 2) if ratings else None


class BookWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "slug",
            "isbn",
            "author",
            "categories",
            "description",
            "cover",
            "price",
            "stock",
            "pages",
            "language",
            "publication_date",
            "is_active",
        )
