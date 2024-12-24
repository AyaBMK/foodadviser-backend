from django.db import models
from ingredients.models import Ingredient
from recipes.models import Recipe

class UnitIngr(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class RecipeIngr(models.Model):
    recipe = models.ForeignKey("recipes.Recipe", on_delete=models.CASCADE)
    ingredient = models.ForeignKey("ingredients.Ingredient", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.ForeignKey(UnitIngr, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('recipe', 'ingredient', 'unit')  

    def __str__(self):
        
        return f"{self.amount} {self.unit} of {self.ingredient} in {self.recipe}"
