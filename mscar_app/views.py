from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import os
from .models import Mod, Category, Review, Version, UserProfile, Bookmark
from .forms import ReviewForm, CustomUserCreationForm, UserProfileForm, ModForm, VersionForm
from django.http import Http404
from django.urls import reverse

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Сообщение показывается ТОЛЬКО на следующей странице (mod_list)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('mscar_app:mod_list')
        else:
            # Сообщения об ошибках показываем на ЭТОЙ же странице
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле "{field}": {error}')
    
    else:
        form = CustomUserCreationForm()
    
    # Очищаем ВСЕ сообщения перед рендерингом страницы регистрации
    # чтобы не показывать старые сообщения с других страниц
    storage = messages.get_messages(request)
    storage.used = True
    
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
            # Сообщение об ошибке показываем на ЭТОЙ же странице
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    # Очищаем ВСЕ сообщения перед рендерингом страницы входа
    storage = messages.get_messages(request)
    storage.used = True
    
    return render(request, 'mscar_app/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('mscar_app:mod_list')

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
            
            messages.success(request, 'Мод успешно создан!')
            
            if became_author:
                messages.info(request, 'Поздравляем! Теперь вы автор на BlockMods!')
            
            return redirect('mscar_app:mod_detail', mod_id=mod.id)
        else:
            # Показываем ошибки формы на ЭТОЙ же странице
            for field, errors in mod_form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле "{field}": {error}')
            for field, errors in version_form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле "{field}": {error}')
    
    else:
        mod_form = ModForm()
        version_form = VersionForm()
    
    # Очищаем ВСЕ сообщения перед рендерингом страницы создания мода
    # кроме тех, что были добавлены ВЫШЕ (ошибки валидации формы)
    # Мы не очищаем, а просто гарантируем что старые сообщения не покажутся
    existing_messages = list(messages.get_messages(request))
    storage = messages.get_messages(request)
    storage.used = True
    
    # Если есть ошибки формы (добавленные выше), сохраняем их
    form_errors = [msg for msg in existing_messages if 'Ошибка в поле' in str(msg.message)]
    for error in form_errors:
        messages.error(request, str(error.message))
    
    context = {
        'mod_form': mod_form,
        'version_form': version_form,
        'categories': Category.objects.all(),
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
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле "{field}": {error}')
    
    else:
        form = VersionForm()
    
    # Очищаем старые сообщения перед рендерингом
    existing_messages = list(messages.get_messages(request))
    storage = messages.get_messages(request)
    storage.used = True
    
    # Восстанавливаем только ошибки формы (добавленные выше)
    form_errors = [msg for msg in existing_messages if 'Ошибка в поле' in str(msg.message)]
    for error in form_errors:
        messages.error(request, str(error.message))
    
    context = {
        'form': form,
        'mod': mod,
    }
    return render(request, 'mscar_app/add_version.html', context)


@login_required
def delete_mod(request, mod_id):
    """Удаление мода"""
    mod = get_object_or_404(Mod, id=mod_id)
    
    # Проверяем, что пользователь является автором мода
    if mod.author != request.user:
        messages.error(request, 'Вы не можете удалить этот мод')
        return redirect('mscar_app:mod_detail', mod_id=mod.id)
    
    if request.method == 'POST':
        # Удаляем мод (сработает кастомный метод delete из models.py)
        mod.delete()
        messages.success(request, f'Мод "{mod.title}" успешно удален')
        return redirect('mscar_app:profile')
    
    # Если GET-запрос, показываем страницу подтверждения
    context = {
        'mod': mod,
        'categories': Category.objects.all(),
    }
    return render(request, 'mscar_app/delete_mod.html', context)

@login_required
def delete_mod_ajax(request, mod_id):
    """Удаление мода через AJAX"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    mod = get_object_or_404(Mod, id=mod_id)
    
    # Проверяем, что пользователь является автором мода
    if mod.author != request.user:
        return JsonResponse({
            'success': False,
            'message': 'Вы не можете удалить этот мод'
        }, status=403)
    
    try:
        mod_title = mod.title
        mod.delete()
        return JsonResponse({
            'success': True,
            'message': f'Мод "{mod_title}" успешно удален'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при удалении мода: {str(e)}'
        }, status=500)

@login_required
def bookmarks(request):
    """Страница с закладками пользователя"""
    user_bookmarks = Bookmark.objects.filter(user=request.user).select_related('mod')
    bookmarked_mods = [bookmark.mod for bookmark in user_bookmarks]
    
    # Для AJAX-запросов возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'bookmarks_count': len(bookmarked_mods),
            'mods': [
                {
                    'id': mod.id,
                    'title': mod.title,
                    'image_url': mod.image.url if mod.image else '',
                    'category': mod.category.name,
                    'author': mod.author.username,
                    'description': mod.description[:100] + '...' if len(mod.description) > 100 else mod.description,
                    'average_rating': mod.average_rating,
                    'total_reviews': mod.total_reviews,
                    'downloads': mod.downloads,
                    'current_version': mod.current_version,
                }
                for mod in bookmarked_mods
            ]
        })
    
    context = {
        'bookmarked_mods': bookmarked_mods,
        'categories': Category.objects.all(),
    }
    return render(request, 'mscar_app/bookmarks.html', context)

@login_required
def toggle_bookmark(request, mod_id):
    """Добавить/удалить мод из закладок"""
    mod = get_object_or_404(Mod, id=mod_id)
    
    if request.method == 'POST':
        # Проверяем, есть ли уже закладка
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            mod=mod
        )
        
        if not created:
            # Если закладка уже существует - удаляем её
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True
        
        # Возвращаем JSON для AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'is_bookmarked': is_bookmarked,
                'bookmarks_count': Bookmark.objects.filter(user=request.user).count()
            })
        
        # Обычный запрос - показываем сообщение и редирект
        if is_bookmarked:
            messages.success(request, f'Мод "{mod.title}" добавлен в закладки')
        else:
            messages.success(request, f'Мод "{mod.title}" удален из закладок')
    
    return redirect(request.META.get('HTTP_REFERER', 'mscar_app:mod_list'))

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
            mod.author = request.user  # Убедимся что автор - текущий пользователь
            mod.current_version = version_form.cleaned_data['version_number']
            mod.save()
            
            # Сохраняем версию
            version = version_form.save(commit=False)
            version.mod = mod
            version.save()
            
            # Проверяем, стал ли пользователь автором
            user_profile = request.user.userprofile
            became_author = user_profile.promote_to_author()
            
            messages.success(request, 'Мод успешно создан!')
            
            if became_author:
                messages.info(request, 'Поздравляем! Теперь вы автор на BlockMods!')
            
            # ВСЕГДА перенаправляем на страницу мода, а не возвращаем JSON
            return redirect('mscar_app:mod_detail', mod_id=mod.id)
        else:
            # Показываем ошибки формы
            for field, errors in mod_form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле "{field}": {error}')
            for field, errors in version_form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле "{field}": {error}')
    
    else:
        mod_form = ModForm()
        version_form = VersionForm()
    
    context = {
        'mod_form': mod_form,
        'version_form': version_form,
        'categories': Category.objects.all(),
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
    
    # Получаем закладки пользователя
    user_bookmarks = []
    if request.user.is_authenticated:
        user_bookmarks = Bookmark.objects.filter(user=request.user).values_list('mod_id', flat=True)
    
    category_id = request.GET.get('category')
    if category_id:
        mods = mods.filter(category_id=category_id)
    
    search_query = request.GET.get('q')
    if search_query:
        mods = mods.filter(title__icontains=search_query)
    
    # Сортировка по рейтингу
    sort_by = request.GET.get('sort', 'rating')
    if sort_by == 'rating':
        mods = sorted(mods, key=lambda x: x.average_rating, reverse=True)
    elif sort_by == 'popular':
        mods = mods.order_by('-downloads')
    elif sort_by == 'new':
        mods = mods.order_by('-id')
    
    context = {
        'mods': mods,
        'categories': categories,
        'user_bookmarks': user_bookmarks,
    }
    return render(request, 'mscar_app/mod_list.html', context)

def mod_detail(request, mod_id):
    mod = get_object_or_404(Mod, id=mod_id)
    categories = Category.objects.all()
    reviews = mod.review_set.all()
    
    # Получаем закладки пользователя
    user_bookmarks = []
    if request.user.is_authenticated:
        user_bookmarks = Bookmark.objects.filter(user=request.user).values_list('mod_id', flat=True)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.mod = mod
            review.author = request.user
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
        'user_bookmarks': user_bookmarks,  # ✅ Добавляем закладки в контекст
    }
    return render(request, 'mscar_app/mod_detail.html', context)

def download_mod(request, mod_id, version_id=None):
    mod = get_object_or_404(Mod, id=mod_id)
    
    # Если версия не указана, используем последнюю версию
    if version_id:
        version = get_object_or_404(Version, id=version_id, mod=mod)
        file_to_download = version.file
    else:
        # Ищем последнюю версию
        latest_version = mod.versions.order_by('-release_date').first()
        if latest_version:
            file_to_download = latest_version.file
        else:
            messages.error(request, 'Файл мода не найден')
            return redirect('mscar_app:mod_detail', mod_id=mod.id)
    
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

def handler404(request, exception):
    return render(request, 'mscar_app/404.html', status=404)

def handler500(request):
    return render(request, 'mscar_app/500.html', status=500)

def handler403(request, exception):
    return render(request, 'mscar_app/403.html', status=403)

def handler400(request, exception):
    return render(request, 'mscar_app/400.html', status=400)