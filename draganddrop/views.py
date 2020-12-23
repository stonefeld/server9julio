from os import remove
from os import path

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.conf import settings

from usuario.models import Deuda

@login_required
def upload(request):
    context = {}
    if request.method == 'POST':
        try:
            deudaMax = request.POST.getlist('deuda')[0]
            deuda = Deuda(deuda=deudaMax)

            media_root = settings.MEDIA_ROOT
            location = path.join(media_root, 'saldos.csv')

            if path.exists(location):
                remove(location)

            try:
                uploaded_file = request.FILES['file']
                fs = FileSystemStorage()
                name = fs.save('saldos.csv', uploaded_file)
                context['url'] = fs.url(name)
                deuda.save()

                return redirect('usuario:cargarDB')

            except:
                context = {
                    'deuda': str(Deuda.objects.all().last().deuda)
                }
                messages.warning(request, f'Debe subir un archivo')

        except:
            context = {
                'deuda': str(Deuda.objects.all().last().deuda)
            }
            messages.warning(request, f'Debe especificar una deuda máxima')

    else:
        context = {
            'deuda': str(Deuda.objects.all().last().deuda)
        }

    return render(request, 'draganddrop/upload.html', context)

