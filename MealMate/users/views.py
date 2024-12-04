from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, EmailLoginForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

# Models 
from .models import UserProfile
from .models import Budget

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
@login_required
def health_concerns(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get updated health concerns from POST data
        new_concerns = request.POST.getlist('new[]')
        existing_concerns = request.POST.getlist('existing[]')
        
        # Save updated concerns to the database
        profile.health_concerns = existing_concerns + new_concerns
        profile.save()
        return redirect('budget')  # Redirect to the next page

    # Pass existing health concerns to the template
    return render(request, 'users/pref_health_concerns.html', {
        'existing_data': profile.health_concerns or [],  # Existing concerns are locked
    })

@login_required
def budget(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)  # Get the current user's profile
    budgets = Budget.objects.all()  # Fetch all budgets
    selected_budget = profile.budget

    return render(request, 'users/pref_budget.html', {
        'budgets': budgets,
        'selected_budget': selected_budget
    })

@login_required
def diet_preferences(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get updated health concerns from POST data
        new_diet = request.POST.getlist('new_diet[]')
        existing_diet = request.POST.getlist('existing_diet[]')
        
        # Save updated concerns to the database
        profile.diet = existing_diet+ new_diet
        profile.save()
        return redirect('dishes')  # Redirect to the next page

    # Pass existing health concerns to the template
    return render(request, 'users/pref_diet.html', {
        'existing_diet': profile.diet or [],  # Existing concerns are locked
    })

@login_required
def dishes_preferences(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get updated health concerns from POST data
        new_dishes = request.POST.getlist('new_dishes[]')
        existing_dishes = request.POST.getlist('existing_dishes[]')
        
        # Save updated concerns to the database
        profile.preferred_cuisines = existing_dishes+ new_dishes
        profile.save()
        return redirect('')  # Redirect to the next page

    # Pass existing health concerns to the template
    return render(request, 'users/pref_dishes.html', {
        'existing_dishes': profile.preferred_cuisines or [],  # Existing concerns are locked
    })

def final_page(request):
    return render(request, 'users/pref_done.html')

### MAIN ###
def main(request):
    return render(request, 'users/main.html')

def recipe(request):
    return render(request, 'users/recipe.html')

def change_options(request):
    return render(request, 'users/change_options.html')