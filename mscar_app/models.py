from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name

class Author(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField()
    
    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
    
    def __str__(self):
        return self.username

class Mod(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    current_version = models.CharField(max_length=20)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    downloads = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Мод'
        verbose_name_plural = 'Моды'
    
    def __str__(self):
        return self.title
    
    def increment_downloads(self):
        """Увеличивает счетчик скачиваний"""
        self.downloads += 1
        self.save()
    
    @property
    def average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0
    
    @property
    def total_reviews(self):
        return self.review_set.count()

class Version(models.Model):
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=20)
    release_date = models.DateField()
    changelog = models.TextField()
    
    class Meta:
        verbose_name = 'Версия'
        verbose_name_plural = 'Версии'
    
    def __str__(self):
        return f"{self.mod.title} - {self.version_number}"

class Review(models.Model):
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100)
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
        return f"{self.mod.title} - {self.author_name} ({self.rating}/5)"

class Tag(models.Model):
    name = models.CharField(max_length=50)
    mods = models.ManyToManyField(Mod)
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
    
    def __str__(self):
        return self.name