from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin, name='admin'),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin_location_list/', admin_location_list, name='admin_location_list'),
    path('hero/', hero, name='hero'),
    path('logout/', logout_view, name='logout'),
    path('switch-language/', switch_language, name='switch_language'),
]
