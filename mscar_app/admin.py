from django.contrib import admin
from .models import Category, Mod, Version, Review, Tag, UserProfile, Bookmark  

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'mod', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'mod__title']
    readonly_fields = ['created_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'website']
    list_filter = ['role']
    search_fields = ['user__username']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Mod)
class ModAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'downloads', 'is_approved', 'created_at']
    list_filter = ['category', 'is_approved', 'created_at']
    search_fields = ['title', 'author__username']
    readonly_fields = ['downloads', 'created_at', 'updated_at']

@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ['mod', 'version_number', 'release_date']
    list_filter = ['release_date']
    search_fields = ['mod__title', 'version_number']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['mod', 'author', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['mod__title', 'author__username']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']