from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),  # List view
    path('<int:pk>/', views.recipe_detail, name='recipe_detail'),  # Detail view
    path('new/', views.recipe_create, name='recipe_create'),  # Create view
    path('ingredients/new/', views.ingredient_create, name='ingredient_create'), # Create view
    path('ingredients/', views.ingredient_list, name='ingredient_list'), # List view
]