from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
import os
from .models import Mod, Category, Review, Version
from .forms import ReviewForm

def mod_list(request):
    categories = Category.objects.all()
    mods = Mod.objects.all()
    
    category_id = request.GET.get('category')
    if category_id:
        mods = mods.filter(category_id=category_id)
    
    search_query = request.GET.get('q')
    if search_query:
        mods = mods.filter(title__icontains=search_query)
    
    # Сортировка по рейтингу
    sort_by = request.GET.get('sort', 'rating')
    if sort_by == 'rating':
        # Сортируем по убыванию рейтинга
        mods = sorted(mods, key=lambda x: x.average_rating, reverse=True)
    elif sort_by == 'popular':
        mods = mods.order_by('-downloads')
    elif sort_by == 'new':
        mods = mods.order_by('-id')
    
    context = {
        'mods': mods,
        'categories': categories,
    }
    return render(request, 'mscar_app/mod_list.html', context)

def mod_detail(request, mod_id):
    mod = get_object_or_404(Mod, id=mod_id)
    categories = Category.objects.all()
    reviews = mod.review_set.all()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.mod = mod
            review.save()
            messages.success(request, 'Ваш отзыв успешно добавлен!')
            return redirect('mscar_app:mod_detail', mod_id=mod.id)
    else:
        form = ReviewForm()
    
    context = {
        'mod': mod,
        'categories': categories,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'mscar_app/mod_detail.html', context)

def download_mod(request, mod_id, version_id=None):
    mod = get_object_or_404(Mod, id=mod_id)
    
    # Если версия не указана, используем текущую версию
    if version_id:
        version = get_object_or_404(Version, id=version_id, mod=mod)
    else:
        # Ищем последнюю версию или используем текущую
        latest_version = mod.versions.order_by('-release_date').first()
        if latest_version:
            version = latest_version
        else:
            version = None
    
    # Увеличиваем счетчик скачиваний
    mod.increment_downloads()
    
    # В реальном проекте здесь была бы отдача файла
    # Для демо просто показываем сообщение
    messages.success(request, f'Мод "{mod.title}" успешно скачан!')
    
    # Перенаправляем обратно на страницу мода
    return redirect('mscar_app:mod_detail', mod_id=mod.id)

def download_modal(request, mod_id):
    """Возвращает HTML для модального окна выбора версии"""
    mod = get_object_or_404(Mod, id=mod_id)
    versions = mod.versions.all()
    
    return render(request, 'mscar_app/download_modal.html', {
        'mod': mod,
        'versions': versions
    })