from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

#Huiwen calendar
from datetime import datetime, timedelta, date
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.utils.safestring import mark_safe
import calendar

from .models import *
from .utils import Calendar
from .forms import TarifaForm



def menu_estacionamiento(request):
    return render(request, template_name='menu_estacionamiento/inicio_estacionamiento.html', context={})
    
#Cuidado Aca
#def seleccionarCalendario(request):
#   return render(request, template_name='menu_estacionamiento/calendario.html', context={})

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

class CalendarView(generic.ListView):
    model= Tarifa_mod
    template_name = 'menu_estacionamiento/calendario.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendario'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context
    
#def tarifa(request, tarifa_id=None):
    #instance = Tarifa_mod()
    #if tarifa_id:
    #    instance = get_object_or_404(Tarifa_mod, pk=tarifa_id)
    #else:
    #    instance = Tarifa_mod()

    #form = TarifaForm(request.POST or None, instance=instance)

    #si tocas submit
    #if request.POST and 'save' in request.POST and form.is_valid():
    #    form.save()
    #    return HttpResponseRedirect(reverse('menu_estacionamiento:calendario'))
    
    #si tocas delete
    #if request.POST and 'delete' in request.POST:
    #    if tarifa_id:
    #        Tarifa_mod.objects.filter(pk=tarifa_id).delete()
    #        return HttpResponseRedirect(reverse('menu_estacionamiento:calendario'))
    #return render(request, 'menu_estacionamiento/tarifa.html', {'form': form})

def tarifa(request):    
    form = TarifaForm(request.POST or None)
    if request.POST and form.is_valid():
        title = form.cleaned_data['title']
        value = form.cleaned_data['value']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']
        Tarifa_mod.objects.get_or_create(
            title=title,
            value=value,
            start_time=start_time,
            end_time=end_time
        )
        return HttpResponseRedirect(reverse('menu_estacionamiento:calendario'))
    return render(request, 'menu_estacionamiento/tarifa.html', {'form': form})

class TarifaEdit(generic.UpdateView):
    model = Tarifa_mod
    fields = ['title', 'value', 'start_time', 'end_time']
    template_name = 'menu_estacionamiento/tarifa.html'

def tarifa_detalles(request, tarifa_id):
    tarifa = Tarifa_mod.objects.get(id=tarifa_id)
    context = {
        'tarifa': tarifa
    }
    return render(request, 'tarifa-detalles.html', context)

#Termina Calendario

def resumenTiempoReal(request):
    return render(request, template_name='menu_estacionamiento/resumen_tiempo.html', context={})

def proveedores(request):
    return render(request, template_name='menu_estacionamiento/proveedores.html', context={})

def historial(request):
    return render(request, template_name='menu_estacionamiento/historial.html', context={})