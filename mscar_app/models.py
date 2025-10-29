from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
import os

def mod_image_path(instance, filename):
    """Генерирует путь для изображений модов"""
    # Используем instance.id если он есть, иначе временный путь
    if instance.id:
        return f'mods/{instance.id}/{filename}'
    return f'mods/temp/{filename}'

class UserProfile(models.Model):
    USER = 'user'
    AUTHOR = 'author'
    ROLE_CHOICES = [
        (USER, 'Обычный пользователь'),
        (AUTHOR, 'Автор'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True, verbose_name="О себе")
    website = models.URLField(blank=True, verbose_name="Веб-сайт")
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    def promote_to_author(self):
        """Повышает пользователя до автора"""
        if self.role != self.AUTHOR:
            self.role = self.AUTHOR
            self.save()
            return True
        return False

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name

class Mod(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    current_version = models.CharField(max_length=20, verbose_name="Текущая версия")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    downloads = models.PositiveIntegerField(default=0, verbose_name="Скачивания")
    image = models.ImageField(upload_to=mod_image_path, null=True, blank=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен")
    
    class Meta:
        verbose_name = 'Мод'
        verbose_name_plural = 'Моды'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0
    
    @property
    def total_reviews(self):
        return self.review_set.count()
    
    def increment_downloads(self):
        """Увеличивает счетчик скачиваний"""
        self.downloads += 1
        self.save()
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Если это новый мод и автор еще не авторизован, повышаем его
        if is_new and hasattr(self.author, 'userprofile'):
            if self.author.userprofile.promote_to_author():
                # Здесь можно добавить логику для показа поздравления
                pass

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE, verbose_name="Мод")  # Теперь Mod определен
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    
    class Meta:
        verbose_name = 'Закладка'
        verbose_name_plural = 'Закладки'
        unique_together = ['user', 'mod']  # Один пользователь не может добавить один мод дважды
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.mod.title}"

class Version(models.Model):
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=20, verbose_name="Номер версии")
    release_date = models.DateField(verbose_name="Дата выпуска")
    changelog = models.TextField(verbose_name="Список изменений")
    file = models.FileField(upload_to='versions/', verbose_name="Файл мода", default='default_mod.jar')
    
    class Meta:
        verbose_name = 'Версия'
        verbose_name_plural = 'Версии'
        ordering = ['-release_date']
    
    def __str__(self):
        return f"{self.mod.title} - {self.version_number}"

class Review(models.Model):
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор отзыва")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Оценка от 1 до 5 звезд"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.mod.title} - {self.author.username} ({self.rating}/5)"

class Tag(models.Model):
    name = models.CharField(max_length=50)
    mods = models.ManyToManyField(Mod)
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
    
    def __str__(self):
        return self.name