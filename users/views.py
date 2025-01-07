from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
import json
from .models import User as MyUser
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return HttpResponse("Bienvenue sur l'API Food Adviser !")
@csrf_exempt  
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            pseudo = data['pseudo']
            password = data['password']
            birthdate = data['birthdate']
            gender = data['gender']
            hashed_password = make_password(password)

            data = json.loads(request.body)
            
            user = MyUser.objects.create(email=email, pseudo=pseudo,password=hashed_password,birthdate=birthdate,gender=gender)
            user.save()
            return JsonResponse({"message": "Inscription réussie"}, status=200)
        except ValidationError as e:
            return JsonResponse({"message": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"message": "Erreur d'inscription: " + str(e)}, status=500)
    else:
        return JsonResponse({"message": "Méthode HTTP non autorisée"}, status=405)
@csrf_exempt
def login_view(request):
    # Si la méthode est POST, on traite la requête
    if request.method == 'POST':
        try:
            # Charger les données envoyées dans la requête
            data = json.loads(request.body)
            email_or_pseudo = data.get('emailOrPseudo')
            password = data.get('password')
            print("pwd:", password)

            # Vérifier que les deux champs sont présents
            if not email_or_pseudo or not password:
                return JsonResponse({"error": "Email/Pseudo and password are required"}, status=400)

            # Rechercher l'utilisateur par email ou pseudo
            user = MyUser.objects.filter(email=email_or_pseudo).first() or MyUser.objects.filter(pseudo=email_or_pseudo).first()

            # Vérifier si l'utilisateur existe et que le mot de passe est correct
            if user and check_password(password, user.password):
                # login(request, user)  # Authentifier l'utilisateur
                request.session['user_id'] = user.id
                # return JsonResponse({"message": "Login successful", "userId": user.id})
                return JsonResponse({"message": "Login successful", "userId": user.id}, status=200)

            # Si l'utilisateur n'est pas trouvé ou que le mot de passe est incorrect
            return JsonResponse({"error": "Invalid email, pseudo, or password"}, status=400)

        except json.JSONDecodeError:
            # Si le corps de la requête est invalide
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    # Si la méthode n'est pas POST
    return JsonResponse({"error": "Method not allowed"}, status=405)
def get_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = MyUser.objects.filter(id=user_id).first()
        if user:
            return JsonResponse({"userId": user.id, "email": user.email, "pseudo": user.pseudo}, status=200)
    return JsonResponse({"error": "No user is logged in"}, status=401)
def logout_view(request):
    request.session.flush()  # Efface toutes les données de session
    return JsonResponse({"message": "Logout successful"}, status=200)
# @csrf_protect  # Cette décorateur assure que la requête nécessite un token CSRF valide       
# def register(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data['email']
#             pseudo = data['pseudo']
#             password = data['password']
#             password_confirmation = data['passwordConfirmation']
#             birthdate_str = data['birthdate']
#             gender = data['gender']

#             # Validation des mots de passe
#             if password != password_confirmation:
#                 return JsonResponse({"error": "Passwords do not match"}, status=400)

#             # Vérification si l'email ou le pseudo existe déjà
#             if MyUser.objects.filter(email=email).exists():
#                 return JsonResponse({"error": "Email already in use"}, status=400)
#             if MyUser.objects.filter(pseudo=pseudo).exists():
#                 return JsonResponse({"error": "Pseudo already in use"}, status=400)

#             # Validation du format de la date de naissance
#             birthdate = parse_date(birthdate_str)
#             if not birthdate:
#                 return JsonResponse({"error": "Invalid birthdate format"}, status=400)

#             # Création de l'utilisateur
#             hashed_password = make_password(password)
#             user = MyUser.objects.create(
#                 email=email,
#                 pseudo=pseudo,
#                 password=hashed_password,
#                 birthdate=birthdate,
#                 gender=gender,  # Ajouter le genre ici
#             )
#             return JsonResponse({"message": "User created successfully", "userId": user.id}, status=201)

#         except (KeyError, ValueError) as e:
#             return JsonResponse({"error": "Bad request data"}, status=400)

#     return JsonResponse({"error": "Method not allowed"}, status=405)

# def login_view(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         email_or_pseudo = data.get('emailOrPseudo')
#         password = data.get('password')

#         user = MyUser.objects.filter(email=email_or_pseudo).first() or MyUser.objects.filter(pseudo=email_or_pseudo).first()
        
#         if user and check_password(password, user.password):
#             login(request, user)
#             return JsonResponse({"message": "Login successful"})
#         return JsonResponse({"error": "Invalid email, pseudo, or password"}, status=400)

#     return JsonResponse({"error": "Method not allowed"}, status=405)

# from django.contrib.auth import authenticate, login
# from django.contrib.auth.hashers import check_password
# from django.http import JsonResponse
# import json
# from .models import User as MyUser
# from django.views.decorators.csrf import csrf_protect