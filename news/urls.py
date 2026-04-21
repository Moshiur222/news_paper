from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin, name='admin'),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('admin_location_list/', admin_location_list, name='admin_location_list'),
    path('category/', category, name='category'),
    path('news/', news, name='news'),
    path('admin/news/', news, name='news'),
    path('switch-language/', switch_language, name='switch_language'),
    path('<slug:slug>/', category_news, name='category_news'),
]
