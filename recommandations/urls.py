from django.urls import path
from .views import RecipeView, UserViewedRecipesView, RecipeRecommendationView

urlpatterns = [
    path('view_recipe/<int:recipe_id>/', RecipeView.as_view(), name='view_recipe'),
    path('viewed_recipes/', UserViewedRecipesView.as_view(), name='viewed_recipes'),
    path('recommend_recipes/', RecipeRecommendationView.as_view(), name='recommend_recipes'), 
]
