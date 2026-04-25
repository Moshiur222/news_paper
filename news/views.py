from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from collections import defaultdict
from .models import *




def home(request):
    current_language = request.session.get('language', 'bn')

    dhaka_location = Location.objects.filter(name_en='Dhaka').first()
    if dhaka_location:
        dhaka_name = dhaka_location.name_bn if current_language == 'bn' else dhaka_location.name_en
    else:
        dhaka_name = 'ঢাকা' if current_language == 'bn' else 'Dhaka'

    categories = Category.objects.prefetch_related(
        'news'
    ).all()
    context = {
        'current_language': current_language,
        'dhaka': dhaka_name,
        'categories': categories,
    }

    return render(request, 'news/landing/pages/home.html', context)

def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Email is required")
        elif Subscriber.objects.filter(email=email).exists():
            messages.warning(request, "You are already subscribed!")
        else:
            Subscriber.objects.create(email=email)
            messages.success(request, "Subscribed successfully!")

    return redirect(request.META.get("HTTP_REFERER", "/"))

def category_news(request, slug):
    category = get_object_or_404(Category, slug=slug)

    news = (
        News.objects
        .filter(category=category)
        .select_related('category', 'location')
        .order_by('-created_at')
    )

    return render(request, 'news/landing/pages/category_news.html', {
        'category': category,
        'news': news,
        'active_url': slug
    })

def location_news(request, slug):
    location = get_object_or_404(Location, slug=slug)

    news_list = (  # ← এখানে news_list ব্যবহার করুন
        News.objects
        .filter(location=location)
        .select_related('category', 'location')
        .order_by('-created_at')
    )

    return render(request, 'news/landing/pages/location_news.html', {
        'location': location,
        'news_list': news_list,  # ← news_list হিসাবে পাঠান
        'active_url': slug
    })
    

def news_view(request, slug):
    news = get_object_or_404(News, slug=slug)
    category_slug = news.category.slug if news.category else None
    
    return render(request, 'news/landing/pages/news_details.html', {
        'news': news,
        'active_url': category_slug,
        'categories': Category.objects.all(),
        'top_newses': News.objects.filter(is_breaking=True).order_by('-id')[:10],
        'trending_news': TrandingNews.objects.all().order_by('-id')[:10],
        'latest_news': News.objects.exclude(id=news.id).order_by('-id')[:10],
    })


def trending_news(request, slug):
    # একটি নির্দিষ্ট ট্রেন্ডিং নিউজ খুঁজে বের করুন
    news = get_object_or_404(TrandingNews, slug=slug)
    
    # সব ক্যাটাগরি নিন (মেনুর জন্য)
    categories = Category.objects.all()
    
    # ব্রেকিং নিউজ
    top_newses = News.objects.filter(is_breaking=True).order_by('-id')[:10]
    
    # ট্রেন্ডিং নিউজ লিস্ট (সাইডবারের জন্য)
    trending_news_list = TrandingNews.objects.all().order_by('-id')
    
    # সর্বশেষ নিউজ (News মডেল থেকে)
    latest_news_list = News.objects.all().order_by('-id')[:10]
    
    context = {
        'news': news,  # বর্তমান ট্রেন্ডিং নিউজ
        'categories': categories,
        'top_newses': top_newses,
        'trending_news': trending_news_list,  # সাইডবারের ট্রেন্ডিং লিস্ট
        'latest_news': latest_news_list,  # সাইডবারের সর্বশেষ সংবাদ
        'active_url': None,  # মেনুতে কোনো ক্যাটাগরি active না থাকলে None
    }
    
    return render(request, 'news/landing/pages/Trending_news_details.html', context)
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
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("admin")
    
    # ========== STATS CARDS এর জন্য ডাটা ==========
    total_users = User.objects.count()
    total_news = News.objects.count()
    total_trending = TrandingNews.objects.count()
    total_subscribers = Subscriber.objects.count()
    
    # গত মাসের তুলনায় পরিবর্তন
    last_month = timezone.now() - timedelta(days=30)
    previous_month = timezone.now() - timedelta(days=60)
    
    news_last_month = News.objects.filter(created_at__gte=last_month).count()
    news_previous_month = News.objects.filter(created_at__gte=previous_month, created_at__lt=last_month).count()
    
    if news_previous_month > 0:
        news_growth = round(((news_last_month - news_previous_month) / news_previous_month) * 100, 1)
    else:
        news_growth = 12.5
    
    # ========== চার্টের জন্য ডাটা (Last 7 days) ==========
    chart_labels = []
    chart_data = []
    
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        chart_labels.append(date.strftime('%a, %b %d'))
        count = News.objects.filter(created_at__date=date.date()).count()
        chart_data.append(count)
    
    # ক্যাটাগরি ভিত্তিক নিউজ কাউন্ট - আলাদা লিস্ট তৈরি করুন
    category_names = []
    category_counts = []
    
    for category in Category.objects.all()[:6]:
        category_names.append(category.name_en)
        category_counts.append(category.news.count())
    
    # ========== রিসেন্ট নিউজ ==========
    recent_news = News.objects.select_related('category', 'location').order_by('-created_at')[:8]
    
    # ========== টপ ক্যাটাগরি ==========
    top_categories = Category.objects.annotate(
        news_count=Count('news')
    ).order_by('-news_count')[:5]
    
    # ========== প্রোগ্রেস আইটেম (News by Location) ==========
    location_progress = []
    for location in Location.objects.all()[:4]:
        count = location.news.count()
        total = News.objects.count()
        percentage = int((count / total) * 100) if total > 0 else 0
        location_progress.append({
            'name': location.name_en,
            'count': count,
            'percentage': percentage
        })
    
    # ========== টিম মেম্বারস ==========
    team_members = User.objects.filter(is_staff=True)[:4]
    
    context = {
        # Stats Cards
        'total_users': total_users,
        'total_news': total_news,
        'total_trending': total_trending,
        'total_subscribers': total_subscribers,
        'news_growth': news_growth,
        
        # Charts - সরাসরি লিস্ট পাঠান
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'category_names': category_names,  # ← আলাদা লিস্ট
        'category_counts': category_counts,  # ← আলাদা লিস্ট
        
        # Recent News Table
        'recent_news': recent_news,
        
        # Top Categories
        'top_categories': top_categories,
        
        # Progress Items
        'location_progress': location_progress,
        
        # Team Members
        'team_members': team_members,
        
        # Browser Stats
        'browser_stats': [
            {'name': 'Chrome', 'icon': 'chrome', 'percent': 64},
            {'name': 'Safari', 'icon': 'safari', 'percent': 19},
            {'name': 'Firefox', 'icon': 'firefox', 'percent': 12},
            {'name': 'Edge', 'icon': 'edge', 'percent': 5},
        ],
    }
    
    return render(request, "news/admin/pages/dashboard.html", context)


def logout_view(request):
    logout(request)
    return redirect("admin")

@login_required
def admin_location_list(request):

    if not request.user.is_authenticated:
        return redirect("admin")
    locations = Location.objects.all().order_by('id')
    errors = {}
 
    # Handle form submission (Add/Edit)
    if request.method == 'POST':
        location_id = request.POST.get('location_id')
        name_en = request.POST.get('name_en', '').strip()
        name_bn = request.POST.get('name_bn', '').strip()
        
        # Validation
        if not name_en:
            errors['name_en'] = 'English name is required'
        if not name_bn:
            errors['name_bn'] = 'Bengali name is required'
        
        if not errors:
            try:
                if location_id:
                    # Edit existing location
                    location = get_object_or_404(Location, id=location_id)
                    location.name_en = name_en
                    location.name_bn = name_bn
                    location.save()
                    messages.success(request, 'Location updated successfully!')
                else:
                    # Add new location
                    Location.objects.create(
                        name_en=name_en,
                        name_bn=name_bn
                    )
                    messages.success(request, 'Location added successfully!')
                
                return redirect('admin_location_list')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
 
    context = {
        'locations': locations,
        'errors': errors,
    }
    return render(request, 'news/admin/pages/admin_location_list.html', context)
 
 
@require_http_methods(["GET"])
def get_location(request, pk):
    """
    API endpoint to get location data for editing
    """
    location = get_object_or_404(Location, pk=pk)
    data = {
        'id': location.id,
        'name_en': location.name_en,
        'name_bn': location.name_bn,
        'slug': location.slug,
    }
    return JsonResponse(data)
 
 
@require_http_methods(["POST"])
def delete_location(request, pk):
    """
    Delete a location
    """
    location = get_object_or_404(Location, pk=pk)
    location.delete()
    messages.success(request, 'Location deleted successfully!')
    return redirect('admin_location_list')



@login_required
def news(request):

    news_list = News.objects.select_related("category", "location").all().order_by('-id')
    categories = Category.objects.all().order_by('id')
    locations = Location.objects.all().order_by('id')

    errors = {}

    # ---------------- ADD / UPDATE ----------------
    if request.method == "POST":

        news_id = request.POST.get("news_id")
        title_en = request.POST.get("title_en", "").strip()
        title_bn = request.POST.get("title_bn", "").strip()
        description_en = request.POST.get("description_en", "").strip()
        description_bn = request.POST.get("description_bn", "").strip()
        category_id = request.POST.get("category")
        location_id = request.POST.get("location")
        is_breaking = request.POST.get("is_breaking") == "on"

        # ---------------- VALIDATION ----------------
        if not title_en:
            errors["title_en"] = "English title is required"
        if not title_bn:
            errors["title_bn"] = "Bangla title is required"
        if not category_id:
            errors["category"] = "Category is required"
        if not location_id:
            errors["location"] = "Location is required"

        if not errors:

            category = get_object_or_404(Category, id=category_id)
            location = get_object_or_404(Location, id=location_id)

            # ---------------- UPDATE ----------------
            if news_id:
                obj = get_object_or_404(News, id=news_id)

                obj.title_en = title_en
                obj.title_bn = title_bn
                obj.description_en = description_en
                obj.description_bn = description_bn
                obj.category = category
                obj.location = location
                obj.is_breaking = is_breaking

                if request.FILES.get("image"):
                    if obj.image:
                        obj.image.delete(save=False)
                    obj.image = request.FILES.get("image")

                obj.save()
                messages.success(request, "News updated successfully!")

            # ---------------- ADD ----------------
            else:
                if not request.FILES.get("image"):
                    messages.error(request, "Image is required!")
                    return redirect("news")

                News.objects.create(
                    title_en=title_en,
                    title_bn=title_bn,
                    description_en=description_en,
                    description_bn=description_bn,
                    category=category,
                    location=location,
                    image=request.FILES.get("image"),
                    is_breaking=is_breaking 
                )

                messages.success(request, "News added successfully!")

            return redirect("news")

        else:
            messages.error(request, "Please fix errors below")

    return render(request, "news/admin/pages/news.html", {
        "news_list": news_list,
        "categories": categories,
        "locations": locations,
        "errors": errors
    })


# ---------------- GET SINGLE NEWS ----------------
@require_http_methods(["GET"])
def get_news(request, pk):
    obj = get_object_or_404(News, pk=pk)

    return JsonResponse({
    "id": obj.id,
    "title_en": obj.title_en,
    "title_bn": obj.title_bn,
    "description_en": obj.description_en,
    "description_bn": obj.description_bn,
    "category": obj.category.id,
    "location": obj.location.id,
    "is_breaking": obj.is_breaking,
    "image": obj.image.url if obj.image else ""
})

# ---------------- DELETE ----------------
@require_http_methods(["POST"])
def delete_news(request, pk):
    obj = get_object_or_404(News, pk=pk)

    if obj.image:
        obj.image.delete(save=False)

    obj.delete()
    messages.success(request, "News deleted successfully!")
    return redirect("news")

@login_required
def category(request):

    categories = Category.objects.all().order_by('id')
    errors = {}

    # ================= ADD / UPDATE =================
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        name_en = request.POST.get('name_en', '').strip()
        name_bn = request.POST.get('name_bn', '').strip()

        # Validation
        if not name_en:
            errors['name_en'] = 'English name is required'
        if not name_bn:
            errors['name_bn'] = 'Bengali name is required'

        # 🚨 LIMIT CHECK (17 categories max)
        if not category_id and Category.objects.count() >= 17:
            messages.error(request, "Maximum 17 categories allowed!")
            return redirect('category')

        if not errors:
            try:
                if category_id:
                    # UPDATE
                    category = get_object_or_404(Category, id=category_id)
                    category.name_en = name_en
                    category.name_bn = name_bn
                    category.save()

                    messages.success(request, 'Category updated successfully!')
                else:
                    # ADD
                    Category.objects.create(
                        name_en=name_en,
                        name_bn=name_bn
                    )
                    messages.success(request, 'Category added successfully!')

                return redirect('category')

            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'news/admin/pages/category.html', {
        'categories': categories,
        'errors': errors,
    })


# ================= GET SINGLE CATEGORY (for edit) =================
@require_http_methods(["GET"])
def get_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    data = {
        'id': category.id,
        'name_en': category.name_en,
        'name_bn': category.name_bn,
        'slug': category.slug,
    }

    return JsonResponse(data)


# ================= DELETE CATEGORY =================
@require_http_methods(["POST"])
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()

    messages.success(request, 'Category deleted successfully!')
    return redirect('category')

@require_http_methods(["POST"])
def switch_language(request):
    language = request.POST.get('language', 'bn')
    next_url = request.POST.get('next', '/')

    if language in ['bn', 'en']:
        request.session['language'] = language

    return redirect(next_url)



@login_required
def trending(request):
    # select_related সম্পূর্ণ সরিয়ে ফেলুন
    news_list = TrandingNews.objects.all().order_by('-id')
    errors = {}

    if request.method == "POST":
        news_id = request.POST.get("news_id")
        title_en = request.POST.get("title_en", "").strip()
        title_bn = request.POST.get("title_bn", "").strip()
        description_en = request.POST.get("description_en", "").strip()
        description_bn = request.POST.get("description_bn", "").strip()

        if not title_en:
            errors["title_en"] = "English title is required"
        if not title_bn:
            errors["title_bn"] = "Bangla title is required"
            
        if not errors:
            if news_id:  # UPDATE
                obj = get_object_or_404(TrandingNews, id=news_id)
                obj.title_en = title_en
                obj.title_bn = title_bn
                obj.description_en = description_en
                obj.description_bn = description_bn

                if request.FILES.get("image"):
                    if obj.image:
                        obj.image.delete(save=False)
                    obj.image = request.FILES.get("image")

                obj.save()
                messages.success(request, "News updated successfully!")

            else:  # ADD NEW
                if not request.FILES.get("image"):
                    messages.error(request, "Image is required!")
                    return redirect("trending")

                TrandingNews.objects.create(  # ← News না, TrandingNews
                    title_en=title_en,
                    title_bn=title_bn,
                    description_en=description_en,
                    description_bn=description_bn,
                    image=request.FILES.get("image"),
                )
                messages.success(request, "News added successfully!")

            return redirect("trending")
        else:
            messages.error(request, "Please fix errors below")

    return render(request, "news/admin/pages/trending_news.html", {
        "news_list": news_list,
        "errors": errors
    })
# ---------------- GET SINGLE NEWS ----------------
@require_http_methods(["GET"])
def get_trending_news(request, pk):
    obj = get_object_or_404(TrandingNews, pk=pk)

    return JsonResponse({
    "id": obj.id,
    "title_en": obj.title_en,
    "title_bn": obj.title_bn,
    "description_en": obj.description_en,
    "description_bn": obj.description_bn,
    "image": obj.image.url if obj.image else ""
})

# ---------------- DELETE ----------------
@require_http_methods(["POST"])
def delete_trending_news(request, pk):
    obj = get_object_or_404(TrandingNews, pk=pk)

    if obj.image:
        obj.image.delete(save=False)

    obj.delete()
    messages.success(request, "News deleted successfully!")
    return redirect("trending")


@login_required
def company_info(request):
    company = CompanyInfo.objects.first()
    errors = {}

    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        mobile_no_en = request.POST.get("mobile_no_en", "").strip()
        mobile_no_bn = request.POST.get("mobile_no_bn", "").strip()

        location_en = request.POST.get("location_en", "").strip()
        location_bn = request.POST.get("location_bn", "").strip()

        facebook = request.POST.get("facebook", "").strip()
        twitter = request.POST.get("twitter", "").strip()
        instagram = request.POST.get("instagram", "").strip()
        linkedin = request.POST.get("linkedin", "").strip()
        youtube = request.POST.get("youtube", "").strip()

        # Validation
        if not email:
            errors["email"] = "Email is required"

        if not errors:
            if company:  # UPDATE
                company.email = email
                company.mobile_no_en = mobile_no_en
                company.mobile_no_bn = mobile_no_bn
                company.location_en = location_en
                company.location_bn = location_bn

                company.facebook = facebook
                company.twitter = twitter
                company.instagram = instagram
                company.linkedin = linkedin
                company.youtube = youtube

                company.save()
                messages.success(request, "Company info updated successfully!")

            else:  # CREATE
                CompanyInfo.objects.create(
                    email=email,
                    mobile_no_en=mobile_no_en,
                    mobile_no_bn=mobile_no_bn,
                    location_en=location_en,
                    location_bn=location_bn,
                    facebook=facebook,
                    twitter=twitter,
                    instagram=instagram,
                    linkedin=linkedin,
                    youtube=youtube,
                )

                messages.success(request, "Company info created successfully!")

            return redirect("company_info")

        else:
            messages.error(request, "Please fix errors below")

    return render(request, "news/admin/pages/company_info.html", {
        "company": company,
        "errors": errors
    })

@login_required
def subscribers(request):
    subscribers = Subscriber.objects.all().order_by('-id')

    return render(request, "news/admin/pages/subscriber.html", {
        'subscribers': subscribers
    })