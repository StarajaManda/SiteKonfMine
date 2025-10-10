from django.contrib import admin
from .models import Category, Author, Mod, Version, Review, Tag

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']
    search_fields = ['username']

@admin.register(Mod)
class ModAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'current_version', 'downloads']
    list_filter = ['category', 'author']
    search_fields = ['title']

@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ['mod', 'version_number', 'release_date']
    list_filter = ['release_date']
    search_fields = ['mod__title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['mod', 'author_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['mod__title', 'author_name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']