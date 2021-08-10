import json

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import FormRegistroUsuario
from estacionamiento.models import CicloCaja, Cobros


@login_required
def home(request):
    return render(request, template_name='usuariosistema/home.html', context={})


def registro(request):
    if request.method == 'POST':
        form = FormRegistroUsuario(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created! You can now log in')
            return redirect('login')

    else:
        form = FormRegistroUsuario()

    return render(request, 'usuariosistema/register.html', {'form': form})


@csrf_exempt
@login_required
def cambiarContrasena(request):
    if request.method == 'POST':
        r = request.body
        data = json.loads(r.decode())
        actual = data['act']
        nueva = data['new']
        username = User.get_username(request.user)
        user = authenticate(username=username, password=actual)
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
    ciclo_caja = CicloCaja.objects.all().last()
    user = request.user
    cobros = Cobros.objects.filter(
        Q(registroEstacionamiento__cicloCaja=ciclo_caja),
        Q(registroEstacionamiento__cicloCaja__usuarioCaja__isnull=True),
        Q(usuarioCobro=user)
    ).distinct()
    print(cobros)
    if cobros:
        messages.warning(request, 'Debe cerrar la caja para poder cerrar sesión')
        return redirect('usuariosistema:home')

    else:
        return redirect('logout')
