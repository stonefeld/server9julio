from django.shortcuts import render


def inicio(request):
    if request.method == 'GET':
        return render(request, 'testing/playground.html')
