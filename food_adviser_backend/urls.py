"""
URL configuration for food_adviser_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from turtle import home
from django.contrib import admin
from django.urls import path, include
from recipes import views
from users.views import register  # Import your register view
from users.views import login_view
from users.views import get_user  # Importez votre fonction get_user
from users.views import get_user, logout_view  # Importez vos vues


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('recipes/', include('recipes.urls')),
    path('ingredients/', include('ingredients.urls')),
    # path('users/', include('users.urls'))
    path('register/', register, name='register'),  # Your URL for registration
    path('login/', login_view, name='login'),
    # path('get_user/', get_user, name='get_user'),  # Route pour récupérer l'utilisateur
    path('user/<int:user_id>/', get_user, name='get_user'),
    path('logout/', logout_view, name='logout'),  # Route pour la déconnexion

]