from django.urls import path
from . import views  # Importer vos vues depuis le fichier views.py
from users.views import register
from users.views import login_view


urlpatterns = [
    # Ajoutez ici les routes pour votre application
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', views.home, name='home'),  # Utiliser la vue home()

]
