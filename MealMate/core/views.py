from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
#from recipes.models import Recipe  # Assuming recipes will be added later

# Create your views here.
def frontpage(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect logged-in users to the home page
    return render(request, 'core/frontpage.html')

@login_required
def home(request):
    '''
    user = request.user
    preferences = user.userprofile
    if request.GET.get('search'):
        query = request.GET['search']
        #recipes = Recipe.objects.filter(name__icontains=query)
    else:
        #recipes = Recipe.objects.filter(cuisine__in=preferences.preferred_cuisines.split(','))

    '''
    return render(request, 'core/home.html')