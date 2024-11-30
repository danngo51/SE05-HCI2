from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, EmailLoginForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('frontpage')  # Redirect to the front page
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = EmailLoginForm
    template_name = 'users/login.html'

@login_required
def profile(request):
    return render(request, 'users/profile_details.html')

@login_required
def preferences(request):
    return render(request, 'users/profile_preferences.html')

@login_required
def history(request):
    return render(request, 'users/profile_history.html')


### PREFERENCES ###
def health_concerns(request):
    return render(request, 'users/pref_health_concerns.html')

def budget(request):
    return render(request, 'users/pref_budget.html')

def diet_preferences(request):
    return render(request, 'users/pref_diet.html')

def dishes_preferences(request):
    return render(request, 'users/pref_dishes.html')

def final_page(request):
    return render(request, 'users/pref_done.html')

### MAIN ###
def main(request):
    return render(request, 'users/main.html')

def recipe(request):
    return render(request, 'users/recipe.html')

def change_options(request):
    return render(request, 'users/change_options.html')