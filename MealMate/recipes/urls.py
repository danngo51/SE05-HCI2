from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='recipe_home'),  # Landing page
    path('recipes/', views.recipe_list, name='recipe_list'),  # List of all recipes
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),  # Detailed recipe view
    path('ingredients/', views.ingredient_list, name='ingredient_list'),  # Ingredient list
    path('tags/', views.tag_list, name='tag_list'),  # Tag list
    path('nutrition/<int:pk>/', views.nutrition_detail, name='nutrition_detail'),  # Nutrition info for recipe
]
