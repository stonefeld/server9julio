from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy

from os import remove
from os import path

from usuario.models import Deuda

def upload(request):
    context = {}
    if request.method == 'POST':
        try:
            deudaMax = request.POST.getlist('deuda')[0]
            deuda = Deuda(deuda=deudaMax)

            if path.exists('./media/saldos.csv'):
                remove('./media/saldos.csv')

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

