from django.urls import path
# from .views import get_recipes_autocomplete
from .views import get_recipes_autocomplete_from_db

urlpatterns = [
    # path('autocomplete/', get_recipes_autocomplete, name='autocomplete_recipes'),
    path('autocomplete/', get_recipes_autocomplete_from_db, name='autocomplete_recipes'),
]