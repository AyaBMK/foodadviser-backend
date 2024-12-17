from django.db import models

class Ingredient(models.Model): 
    name = models.CharField(max_length=55, unique=True, verbose_name="name")
    image_url = models.URLField(max_length=500, null=True, blank=True)
    
    def __str__(self):
        return self.name