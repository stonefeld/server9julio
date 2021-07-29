from estacionamiento.views import registro_estacionamiento
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from estacionamiento.models import CicloCaja, Cobros
from django.db.models import Q
import json
from django.contrib.auth.models import User
from .forms import FormRegistroUsuario
from django.contrib.auth import authenticate

@login_required
def home(request):
    return render(request, template_name='usuariosistema/home.html', context={})

def registro(request):
    if request.method == 'POST':
        form = FormRegistroUsuario(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Your account has been created! You can now log in')
            return redirect('login')

    else:
        form = FormRegistroUsuario()

    return render(request, 'usuariosistema/register.html', { 'form': form })

@csrf_exempt
@login_required
def cambiarContrasena(request):
    if request.method == 'POST':
        r = request.body
        data = json.loads(r.decode())
        actual = data['act']
        nueva = data['new']
        username = User.get_username(request.user)
        user = authenticate(username = username ,password = actual)
        if user is not None:
            u = request.user
            u.set_password(nueva)
            u.save()
            messages.warning(request, 'La contraseña fue cambiada correctamente')
            return JsonResponse('Ok', safe=False)
        else:
            messages.warning(request, 'Error al cambiar la contraseña, contraseña actual equivocada')
            return JsonResponse('False', safe=False)
    else:
        return redirect('/')
    
def logout(request):
    cicloCaja_ = CicloCaja.objects.all().last()
    user = request.user
    cobros_ = Cobros.objects.filter(
        Q(registroEstacionamiento__cicloCaja=cicloCaja_),
        Q(usuarioCobro = user)
    ).distinct()
    if cobros_ is None:
        messages.warning(request, 'Seción cerrada correctamente')
        return redirect('/logout/')
    else:
        messages.warning(request, 'Error la caja no fue cerrada')
        return redirect('/')
         
