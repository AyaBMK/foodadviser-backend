from django.urls import path
from . import views  # Importer vos vues depuis le fichier views.py
from users.views import register
from users.views import login_view
from django.contrib import admin


urlpatterns = [
    # Ajoutez ici les routes pour votre application
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('admin/', admin.site.urls),
]