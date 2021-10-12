from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(template_name='usuariosistema/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='usuariosistema/logout.html'), name='logout'),

    path('', include('usuariosistema.urls')),

    path('usuario/', include('usuario.urls')),
    path('upload/', include('draganddrop.urls')),

    path('general/', include('registroGeneral.urls')),
    path('tenis/', include('registroTenis.urls')),

    path('pileta/', include('registroPileta.urls')),
    path('estacionamiento/', include('estacionamiento.urls')),
    path('testing/', include('testing.urls')),
    path('menu_estacionamiento/', include('menu_estacionamiento.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
