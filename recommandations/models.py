from django.db import models
from django.contrib.auth.models import User  
from recipes.models import Recipe

class UserRecipeView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe_views')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='user_views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')  

    def __str__(self):
        return f"{self.user.username} viewed {self.recipe.title} on {self.viewed_at}"
