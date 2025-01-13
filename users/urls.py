from django.urls import path
from . import views  # Importer vos vues depuis le fichier views.py
from users.views import register
from users.views import login_view
from users.views import get_user, logout_view  # Importez vos vues
from django.contrib import admin


urlpatterns = [
    # Ajoutez ici les routes pour votre application
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    # path('get_user/', get_user, name='get_user'),  # Route pour récupérer l'utilisateur
    path('logout/', logout_view, name='logout'),  # Route pour la déconnexion
    path('user/<int:user_id>/', get_user, name='get_user'),
    path('admin/', admin.site.urls),
]