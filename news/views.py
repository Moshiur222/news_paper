from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *

# Create your views here.

# for landing page 
def home(request):
    hero_areas  = HeroSection.objects.all().order_by('id')
    context = {
        'hero_areas': hero_areas
    }
    return render(request, 'news/landing/pages/home.html', context)

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


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("admin")

    return render(request, "news/admin/pages/dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("admin")

def admin_location_list(request):
    if not request.user.is_authenticated:
        return redirect("admin")

    # ADD
    if request.method == "POST" and "add_location" in request.POST:
        name = request.POST.get("name")
        Location.objects.create(name=name)
        return redirect("admin_location_list")

    # UPDATE
    if request.method == "POST" and "update_id" in request.POST:
        loc_id = request.POST.get("update_id")
        name = request.POST.get("name")

        location = get_object_or_404(Location, id=loc_id)
        location.name = name
        location.save()
        return redirect("admin_location_list")

    # DELETE
    if request.method == "POST" and "delete_id" in request.POST:
        loc_id = request.POST.get("delete_id")

        location = get_object_or_404(Location, id=loc_id)
        location.delete()
        return redirect("admin_location_list")

    locations = Location.objects.all()

    return render(request, "news/admin/pages/admin_location_list.html", {
        "locations": locations
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import HeroSection, Location

@login_required
def hero(request):

    # ADD / UPDATE
    if request.method == "POST":

        # DELETE ACTION
        if request.POST.get("delete_id"):
            hero_id = request.POST.get("delete_id")
            hero_obj = get_object_or_404(HeroSection, id=hero_id)
            
            # Optional: Delete the image file from storage
            if hero_obj.image:
                hero_obj.image.delete(save=False)
            
            hero_obj.delete()
            
            messages.success(request, f'Hero "{hero_obj.title}" has been deleted successfully!')
            return redirect("hero")

        # UPDATE ACTION
        elif request.POST.get("update_id"):
            hero_id = request.POST.get("update_id")
            title = request.POST.get("title")
            description = request.POST.get("description")
            location_id = request.POST.get("location")

            location = get_object_or_404(Location, id=location_id)
            hero_obj = get_object_or_404(HeroSection, id=hero_id)

            hero_obj.title = title
            hero_obj.description = description
            hero_obj.location = location

            if request.FILES.get("image"):
                # Optional: Delete old image before saving new one
                if hero_obj.image:
                    hero_obj.image.delete(save=False)
                hero_obj.image = request.FILES.get("image")

            hero_obj.save()
            
            messages.success(request, f'Hero "{title}" has been updated successfully!')

        # ADD ACTION
        else:
            title = request.POST.get("title")
            description = request.POST.get("description")
            location_id = request.POST.get("location")

            # Validation
            if not title or not location_id or not request.FILES.get("image"):
                messages.error(request, 'Title, Location, and Image are required!')
                return redirect("hero")

            location = get_object_or_404(Location, id=location_id)

            HeroSection.objects.create(
                title=title,
                description=description,
                location=location,
                image=request.FILES.get("image")
            )
            
            messages.success(request, f'Hero "{title}" has been added successfully!')

        return redirect("hero")

    # GET REQUEST - Display all heroes
    heroes = HeroSection.objects.select_related("location").all().order_by('-id')  # Order by latest first
    locations = Location.objects.all()

    return render(request, "news/admin/pages/hero.html", {
        "heroes": heroes,
        "locations": locations
    })


@require_http_methods(["POST"])
def switch_language(request):
    language = request.POST.get('language', 'bn')
    next_url = request.POST.get('next', '/')

    if language in ['bn', 'en']:
        request.session['language'] = language

    return redirect(next_url)