from django.shortcuts import render, redirect
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

        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save('saldos.csv', uploaded_file)
        context['url'] = fs.url(name)

        return redirect('usuario:cargarDB')

    return render(request, 'draganddrop/upload.html', context)
