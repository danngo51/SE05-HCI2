from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile_details'),
    # path('preferences/', views.preferences, name='profile_preferences'),
    path('history/', views.history, name='profile_history'),
    path('preferences/health-concerns', views.health_concerns, name='health_concerns'),
    path('preferences/budget/', views.budget, name='budget'),
    path('preferences/diet-preferences/', views.diet_preferences, name='diet'),
    path('preferences/dishes-preferences/', views.dishes_preferences, name='dishes'),
    path('preferences/done/', views.final_page, name='done'),
    path('main/', views.main, name='main'),
    path('recipe/', views.recipe, name='recipe'),
    path('change-options/', views.change_options, name='change_options'),
]
