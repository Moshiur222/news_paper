from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *



# for landing page 
def home(request):
    current_language = request.session.get('language', 'bn')
    # Get location name in current language
    dhaka_location = Location.objects.filter(name_en='Dhaka').first()
    if dhaka_location:
        dhaka_name = dhaka_location.name_bn if current_language == 'bn' else dhaka_location.name_en
    else:
        dhaka_name = 'ঢাকা' if current_language == 'bn' else 'Dhaka'
    
    context = {
        'current_language': current_language,
        'dhaka': dhaka_name,
    }
    
    return render(request, 'news/landing/pages/home.html', context)




def category_news(request, slug):
    category = get_object_or_404(Category, slug=slug)
    news = News.objects.filter(category=category)
    return render(request, 'news\landing\pages\category_news.html', {'category': category, 'news': news, "active_url": slug})

# for admin panel

def admin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "news/admin/pages/login.html")

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("admin")

    return render(request, "news/admin/pages/dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("admin")

@login_required
def admin_location_list(request):
    if not request.user.is_authenticated:
        return redirect("admin")

    # ADD
    if request.method == "POST" and "add_location" in request.POST:
        name_en = request.POST.get("name_en")
        name_bn = request.POST.get("name_bn")
        
        if not name_en or not name_bn:
            messages.error(request, "Both English and Bangla names are required!")
            return redirect("admin_location_list")
        
        Location.objects.create(name_en=name_en, name_bn=name_bn)
        messages.success(request, f'Location "{name_en}" has been added successfully!')
        return redirect("admin_location_list")

    # UPDATE
    if request.method == "POST" and "update_id" in request.POST:
        loc_id = request.POST.get("update_id")
        name_en = request.POST.get("name_en")
        name_bn = request.POST.get("name_bn")

        if not name_en or not name_bn:
            messages.error(request, "Both English and Bangla names are required!")
            return redirect("admin_location_list")

        location = get_object_or_404(Location, id=loc_id)
        location.name_en = name_en
        location.name_bn = name_bn
        location.save()
        
        messages.success(request, f'Location "{name_en}" has been updated successfully!')
        return redirect("admin_location_list")

    # DELETE
    if request.method == "POST" and "delete_id" in request.POST:
        loc_id = request.POST.get("delete_id")
        location = get_object_or_404(Location, id=loc_id)
        location_name = location.name_en
        location.delete()
        
        messages.success(request, f'Location "{location_name}" has been deleted successfully!')
        return redirect("admin_location_list")

    locations = Location.objects.all().order_by('name_en')

    return render(request, "news/admin/pages/admin_location_list.html", {
        "locations": locations
    })


@login_required
def news(request):
    if not request.user.is_authenticated:
        return redirect("admin")
    
    # DELETE ACTION
    if request.method == "POST" and request.POST.get("delete_id"):
        news_id = request.POST.get("delete_id")
        news_obj = get_object_or_404(News, id=news_id)
        
        if news_obj.image:
            news_obj.image.delete(save=False)
        
        news_obj.delete()
        messages.success(request, f'News "{news_obj.title_en}" has been deleted successfully!')
        return redirect("news")

    # UPDATE ACTION
    if request.method == "POST" and request.POST.get("update_id"):
        news_id = request.POST.get("update_id")
        title_en = request.POST.get("title_en")
        title_bn = request.POST.get("title_bn")
        description_en = request.POST.get("description_en")
        description_bn = request.POST.get("description_bn")
        category_id = request.POST.get("category")
        location_id = request.POST.get("location")

        if not title_en or not title_bn or not category_id or not location_id:
            messages.error(request, 'English title, Bangla title, Category, and Location are required!')
            return redirect("news")

        category = get_object_or_404(Category, id=category_id)
        location = get_object_or_404(Location, id=location_id)
        news_obj = get_object_or_404(News, id=news_id)

        news_obj.title_en = title_en
        news_obj.title_bn = title_bn
        news_obj.description_en = description_en
        news_obj.description_bn = description_bn
        news_obj.category = category
        news_obj.location = location

        if request.FILES.get("image"):
            if news_obj.image:
                news_obj.image.delete(save=False)
            news_obj.image = request.FILES.get("image")

        news_obj.save()
        messages.success(request, f'News "{title_en}" has been updated successfully!')
        return redirect("news")

    # ADD ACTION
    if request.method == "POST":
        title_en = request.POST.get("title_en")
        title_bn = request.POST.get("title_bn")
        description_en = request.POST.get("description_en")
        description_bn = request.POST.get("description_bn")
        category_id = request.POST.get("category")
        location_id = request.POST.get("location")

        if not title_en or not title_bn or not category_id or not location_id or not request.FILES.get("image"):
            messages.error(request, 'English Title, Bangla Title, Category, Location, and Image are required!')
            return redirect("news")

        category = get_object_or_404(Category, id=category_id)
        location = get_object_or_404(Location, id=location_id)

        News.objects.create(
            title_en=title_en,
            title_bn=title_bn,
            description_en=description_en,
            description_bn=description_bn,
            category=category,
            location=location,
            image=request.FILES.get("image")
        )
        messages.success(request, f'News "{title_en}" has been added successfully!')
        return redirect("news")

    # GET REQUEST - Display all news
    news_list = News.objects.select_related("category", "location").all().order_by('-id')
    categories = Category.objects.all().order_by('id')
    locations = Location.objects.all().order_by('id')

    return render(request, "news/admin/pages/news.html", {
        "news_list": news_list,
        "categories": categories,
        "locations": locations
    })

@login_required
def category(request):
    if not request.user.is_authenticated:
        return redirect("admin")
    # ADD
    if request.method == "POST" and "add_category" in request.POST:
        name_en = request.POST.get("name_en")
        name_bn = request.POST.get("name_bn")

        if not name_en or not name_bn:
            messages.error(request, "Both English and Bangla names are required!")
            return redirect("category")

        Category.objects.create(name_en=name_en, name_bn=name_bn)
        messages.success(request, f'Category "{name_en}" added successfully!')
        return redirect("category")

    # UPDATE
    if request.method == "POST" and "update_id" in request.POST:
        cat_id = request.POST.get("update_id")
        name_en = request.POST.get("name_en")
        name_bn = request.POST.get("name_bn")

        if not name_en or not name_bn:
            messages.error(request, "Both English and Bangla names are required!")
            return redirect("category")

        cat = get_object_or_404(Category, id=cat_id)
        cat.name_en = name_en
        cat.name_bn = name_bn
        cat.save()

        messages.success(request, f'Category "{name_en}" updated successfully!')
        return redirect("category")

    # DELETE
    if request.method == "POST" and "delete_id" in request.POST:
        cat_id = request.POST.get("delete_id")
        cat = get_object_or_404(Category, id=cat_id)
        name = cat.name_en
        cat.delete()

        messages.success(request, f'Category "{name}" deleted successfully!')
        return redirect("category")

    categories = Category.objects.all().order_by("name_en")

    return render(request, "news/admin/pages/category.html", {
        "categories": categories
    })

@require_http_methods(["POST"])
def switch_language(request):
    language = request.POST.get('language', 'bn')
    next_url = request.POST.get('next', '/')

    if language in ['bn', 'en']:
        request.session['language'] = language

    return redirect(next_url)