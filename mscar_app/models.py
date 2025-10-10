from django.db import models

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
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
    
    def __str__(self):
        return f"{self.mod.title} - {self.author_name}"

class Tag(models.Model):
    name = models.CharField(max_length=50)
    mods = models.ManyToManyField(Mod)
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
    
    def __str__(self):
        return self.name