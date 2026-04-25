from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin, name='admin'),
    path('', home, name='home'),
    path('location/<slug:slug>/', location_news, name='location_news'),
    
    # ========== TRENDING NEWS URLs ==========
    path('trending/', trending, name='trending'),
    path('trending/<slug:slug>/', trending_news, name='trending_news'),  # স্ল্যাশ যোগ করুন
    path('trending/get/<int:pk>/', get_trending_news, name='get_trending_news'),  # ← যোগ করুন
    path('trending/delete/<int:pk>/', delete_trending_news, name='delete_trending_news'),  # ← যোগ করুন
    
    # ========== REGULAR NEWS URLs ==========
    path('news/<slug:slug>/', news_view, name='news_home'),  # স্ল্যাশ যোগ করুন
    path("admin/news/", news, name="news"),
    path("news/get/<int:pk>/", get_news, name="get_news"),
    path("news/delete/<int:pk>/", delete_news, name="delete_news"),
    
    # ========== OTHER URLs ==========
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('admin_location_list/', admin_location_list, name='admin_location_list'),
    path('category/', category, name='category'),
    path('categories/get/<int:pk>/', get_category, name='get_category'),
    path('categories/delete/<int:pk>/', delete_category, name='delete_category'),
    path('switch-language/', switch_language, name='switch_language'),
    path('category/<slug:slug>/', category_news, name='category_news'),
    path('locations/get/<int:pk>/', get_location, name='get_location'),
    path('locations/delete/<int:pk>/', delete_location, name='delete_location'),
    path('company_info/', company_info, name='company_info'),
    path("subscribe/", subscribe, name="subscribe"),
    path("subscriber/", subscribers, name="subscriber"),
]