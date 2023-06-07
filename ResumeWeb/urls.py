# Импорты
from django.urls import path, include
from .views import start
from . import forms
from . import views

# Ссылки с их представлениями
urlpatterns = [
    path('', views.start, name='homepage'),
    path('create', views.crresume, name='crresume'),
    path('show', views.shresume),
    path('update', views.updresume),
    path('delete', views.delresume),
    path('accounts/', include('django.contrib.auth.urls')),
    path("signup/", views.register, name="signup"),
]
