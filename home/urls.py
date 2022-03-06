from django.urls import path
from . import views

urlpatterns = [
    path('', views.home,name = 'home'),
    path('search',views.search,name='search'),
    path('register',views.register, name='register'),
    path('login',views.login, name='login'),
    path('logout',views.logout, name='logout'),
    path('contact',views.contact, name='contact'),
    
]