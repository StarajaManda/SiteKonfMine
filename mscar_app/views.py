from django.shortcuts import render, get_object_or_404
from .models import Mod, Category

def mod_list(request):
    categories = Category.objects.all()
    mods = Mod.objects.all()
    
    # Фильтрация по категории
    category_id = request.GET.get('category')
    if category_id:
        mods = mods.filter(category_id=category_id)
    
    # Поиск
    search_query = request.GET.get('q')
    if search_query:
        mods = mods.filter(title__icontains=search_query)
    
    context = {
        'mods': mods,
        'categories': categories,
    }
    return render(request, 'mscar_app/mod_list.html', context)

def mod_detail(request, mod_id):
    mod = get_object_or_404(Mod, id=mod_id)
    categories = Category.objects.all()
    
    context = {
        'mod': mod,
        'categories': categories,
    }
    return render(request, 'mscar_app/mod_detail.html', context)