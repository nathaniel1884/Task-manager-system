from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from .forms import TaskForm, RegisterForm, LoginForm

# Task Views
@login_required(login_url='login')
def index(request):
    """Display all tasks for the logged-in user"""
    tasks = Task.objects.filter(user=request.user)
    form = TaskForm()  # Create empty form for adding tasks
    
    context = {
        'tasks': tasks,
        'form': form,
        'total': tasks.count(),
        'completed': tasks.filter(completed=True).count()
    }
    return render(request, 'tasks/index.html', context)

@login_required(login_url='login')
def add_task(request):
    """Add a new task using Django Form"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)  # Don't save yet
            task.user = request.user  # Add the user
            task.save()  # Now save
            messages.success(request, 'Task added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('index')

@login_required(login_url='login')
def toggle_task(request, task_id):
    """Toggle task completion status"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('index')

@login_required(login_url='login')
def delete_task(request, task_id):
    """Delete a task"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted successfully!')
    return redirect('index')

@login_required(login_url='login')
def edit_task(request, task_id):
    """Edit an existing task"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('index')
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'editing': True
    }
    return render(request, 'tasks/edit_task.html', context)

# Authentication Views
def login_view(request):
    """Handle user login using Django Form"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    
    # Pass both forms to context
    return render(request, 'tasks/login.html', {
        'login_form': form,
        'register_form': RegisterForm()  # Add register form for when switching tabs
    })

def register_view(request):
    """Handle user registration using Django Form"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please login.')
            return redirect('login')
        else:
            # Form will automatically show errors
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    
    # Pass both forms to context so template can access them
    return render(request, 'tasks/login.html', {
        'register_form': form,
        'login_form': LoginForm()  # Add login form for when switching tabs
    })

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')