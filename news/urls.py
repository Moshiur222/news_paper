from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin, name='admin'),
    path('', home, name='home'),
    path('api/login/', login_api, name='login_api'),
    path('api/register/', register_api, name='register_api'),
    path('location/<slug:slug>/', location_news, name='location_news'),


    path('profile/', profile_view, name='profile'),
    path('api/profile/update/', update_profile, name='update_profile'),
    path('api/profile/change-password/', change_password, name='change_password'),
    path('api/profile/upload-pic/', upload_profile_pic, name='upload_profile_pic'),
    path('api/profile/remove-pic/', remove_profile_pic, name='remove_profile_pic'),
    path('api/comment/delete/', delete_comment, name='delete_comment'),
    path('api/profile/profile-pic/', user_profile_api, name='profile_pic'),
    
    # ========== TRENDING NEWS URLs ==========
    path('trending/', trending, name='trending'),
    path('trending/<slug:slug>/', trending_news, name='trending_news'),
    path('trending/get/<int:pk>/', get_trending_news, name='get_trending_news'),
    path('trending/delete/<int:pk>/', delete_trending_news, name='delete_trending_news'),
    
    # ========== REGULAR NEWS URLs ==========
    path('news/<slug:slug>/', news_view, name='news_home'),
    path("admin/news/", news, name="news"),
    path("news/get/<int:pk>/", get_news, name="get_news"),
    path("news/delete/<int:pk>/", delete_news, name="delete_news"),
    path('api/poll/vote/', submit_poll_vote, name='submit_poll_vote'),
    path('api/poll/results/', get_poll_results, name='get_poll_results'),
    path('api/comment/add/', submit_comment, name='submit_comment'),
    
    # ========== OTHER URLs ==========
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('admin_location_list/', admin_location_list, name='admin_location_list'),
    path('category/', category, name='category'),
    path('tag/', tags, name='tag'),
    path('tag/get/<int:pk>/', get_tag, name='get_tag'),
    path('tag/delete/<int:pk>/', delete_tag, name='delete_tag'),
    path('tags/<slug:slug>/', tag_news, name='tag_news'),

    path('tag/get/<int:pk>/', get_tag, name='get_tag'),
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