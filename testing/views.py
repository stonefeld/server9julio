from django.shortcuts import render

# Create your views here.
def inicio(request):
    if request.method == 'GET':
        return render(request, 'testing/playground.html')