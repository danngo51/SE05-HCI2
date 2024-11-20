from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, EmailLoginForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView

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
