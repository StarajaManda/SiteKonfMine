from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import os
from .models import Mod, Category, Review, Version, UserProfile
from .forms import ReviewForm, CustomUserCreationForm, UserProfileForm, ModForm, VersionForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('mscar_app:mod_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'mscar_app/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('mscar_app:mod_list')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'mscar_app/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('mscar_app:mod_list')

@login_required
def profile(request):
    user_profile = request.user.userprofile
    user_mods = Mod.objects.filter(author=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('mscar_app:profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    context = {
        'form': form,
        'user_mods': user_mods,
        'user_profile': user_profile,
    }
    return render(request, 'mscar_app/profile.html', context)

@login_required
def create_mod(request):
    if request.method == 'POST':
        mod_form = ModForm(request.POST, request.FILES)
        version_form = VersionForm(request.POST, request.FILES)
        
        if mod_form.is_valid() and version_form.is_valid():
            # Сохраняем мод
            mod = mod_form.save(commit=False)
            mod.author = request.user
            mod.current_version = version_form.cleaned_data['version_number']
            mod.save()
            
            # Сохраняем версию
            version = version_form.save(commit=False)
            version.mod = mod
            version.save()
            
            # Проверяем, стал ли пользователь автором
            user_profile = request.user.userprofile
            became_author = user_profile.promote_to_author()
            
            messages.success(request, 'Мод успешно загружен!')
            
            if became_author:
                # Возвращаем флаг для показа поздравления
                return JsonResponse({
                    'success': True,
                    'became_author': True,
                    'mod_id': mod.id
                })
            else:
                return JsonResponse({
                    'success': True,
                    'became_author': False,
                    'mod_id': mod.id
                })
        else:
            errors = {}
            if mod_form.errors:
                errors.update(mod_form.errors)
            if version_form.errors:
                errors.update(version_form.errors)
            return JsonResponse({'success': False, 'errors': errors})
    
    else:
        mod_form = ModForm()
        version_form = VersionForm()
    
    categories = Category.objects.all()
    context = {
        'mod_form': mod_form,
        'version_form': version_form,
        'categories': categories,
    }
    return render(request, 'mscar_app/create_mod.html', context)

@login_required
def add_version(request, mod_id):
    mod = get_object_or_404(Mod, id=mod_id, author=request.user)
    
    if request.method == 'POST':
        form = VersionForm(request.POST, request.FILES)
        if form.is_valid():
            version = form.save(commit=False)
            version.mod = mod
            version.save()
            
            # Обновляем текущую версию мода
            mod.current_version = version.version_number
            mod.save()
            
            messages.success(request, 'Версия успешно добавлена!')
            return redirect('mscar_app:mod_detail', mod_id=mod.id)
    else:
        form = VersionForm()
    
    context = {
        'form': form,
        'mod': mod,
    }
    return render(request, 'mscar_app/add_version.html', context)

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