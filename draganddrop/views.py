from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy

from os import remove
from os import path

def upload(request):
    context = {}
    if request.method == 'POST':
        if path.exists('./media/saldos.csv'):
            remove('./media/saldos.csv')

        try:
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage()
            name = fs.save('saldos.csv', uploaded_file)
            context['url'] = fs.url(name)

            return redirect('usuario:cargarDB')

        except:
            messages.warning(request, f'Debe subir un archivo')

    return render(request, 'draganddrop/upload.html', context)

