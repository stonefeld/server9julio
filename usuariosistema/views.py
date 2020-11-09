from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import FormRegistroUsuario

@login_required
def home(request):
    return render(request, template_name='usuariosistema/home.html', context={})

def registro(request):
    if request.method == 'POST':
        form = FormRegistroUsuario(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You can now log in')
            return redirect('login')

    else:
        form = FormRegistroUsuario()

    return render(request, 'usuariosistema/register.html', { 'form': form })
