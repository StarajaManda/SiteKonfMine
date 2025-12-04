from .models import Category

def categories(request):
    """Добавляет список категорий во все шаблоны"""
    return {
        'categories': Category.objects.all()
    }