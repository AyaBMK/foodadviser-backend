from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    pseudo = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Hachage du mot de passe à gérer
    birthdate = models.DateField()
    GENDER_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
    ]
    
    # Ajout du champ gender
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,  # Ce champ peut être vide
    )

    def __str__(self):
        return self.pseudo
