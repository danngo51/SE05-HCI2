from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, EmailLoginForm
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

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
    user = request.user

    if request.method == 'POST':
        # Check which form is submitted
        if 'email' in request.POST:  # Profile Info Form
            user.email = request.POST.get('email', user.email)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.save()
            messages.success(request, 'Profile details updated successfully.')
        elif 'password' in request.POST:  # Password Form
            password = request.POST.get('password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if password and new_password:
                if user.check_password(password):
                    if new_password == confirm_password:
                        user.set_password(new_password)
                        user.save()
                        update_session_auth_hash(request, user)  # Keep the user logged in
                        messages.success(request, 'Password changed successfully.')
                    else:
                        messages.error(request, 'New passwords do not match.')
                else:
                    messages.error(request, 'Incorrect current password.')

        return redirect('profile_preferences')  # Redirect to the same page after processing

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
    if request.method == 'POST':
        # Get the selected budget from POST data
        selected_budget_id = request.POST.get('budget')

        # Save the selected budget to the user's profile
        if selected_budget_id:
            try:
                selected_budget = Budget.objects.get(id=selected_budget_id)
                profile.budget = selected_budget
                profile.save()
            except Budget.DoesNotExist:
                # Handle the case where the budget ID is invalid
                pass

        return redirect('diet')  # Redirect to the next page
    
    return render(request, 'users/pref_budget.html', {
        'budgets': budgets,
        'selected_budget': selected_budget
    })

@login_required
def diet_preferences(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get updated health concerns from POST data
        new_concerns = request.POST.getlist('new[]')
        existing_concerns = request.POST.getlist('existing[]')
        
        # Save updated concerns to the database
        profile.diet = existing_concerns + new_concerns
        profile.save()
        return redirect('dishes')  # Redirect to the next page

    # Pass existing health concerns to the template
    return render(request, 'users/pref_diet.html', {
        'existing_data': profile.diet or [],  # Existing concerns are locked
    })

@login_required
def dishes_preferences(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get updated health concerns from POST data
        new_concerns = request.POST.getlist('new[]')
        existing_concerns = request.POST.getlist('existing[]')
        
        # Save updated concerns to the database
        profile.preferred_cuisines = existing_concerns + new_concerns
        profile.save()
        return redirect('done')  # Redirect to the next page

    # Pass existing health concerns to the template
    return render(request, 'users/pref_dishes.html', {
        'existing_data': profile.preferred_cuisines or [],  # Existing concerns are locked
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