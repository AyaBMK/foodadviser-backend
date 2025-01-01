# from django.shortcuts import render
# from django.http import JsonResponse
# import requests
# from django.conf import settings
# from dotenv import load_dotenv
# import os

# load_dotenv()

# api_key = os.getenv('API_KEY_S')
# def get_recipes_autocomplete(request):
#     query = request.GET.get('query', '')
#     number = request.GET.get('number', 10)  
#     if not query:
#         return JsonResponse({"error": "Le paramètre 'query' est requis."}, status=400)

#     spoonacular_url = "https://api.spoonacular.com/recipes/autocomplete"
#     params = {
#         "query": query,
#         "number": number,
#         "apiKey": api_key,
#     }

#     try:
#         response = requests.get(spoonacular_url, params=params)
#         response.raise_for_status()
#         data = response.json()
#         return JsonResponse(data, safe=False)
#     except requests.exceptions.RequestException as e:
#         return JsonResponse({"error": str(e)}, status=500)

from django.http import JsonResponse
from recipes.models import Recipe

def get_recipes_autocomplete_from_db(request):
    query = request.GET.get('query', '')
    number = int(request.GET.get('number', 10))  # Nombre de résultats à retourner

    if not query:
        return JsonResponse({"error": "Le paramètre 'query' est requis."}, status=400)

    # Rechercher des recettes dont le titre contient la requête
    recipes = Recipe.objects.filter(title__icontains=query)[:number]
    results = [
        {
            "id": recipe.id_recipe,
            "title": recipe.title,
            "image_url": recipe.image_url,
        }
        for recipe in recipes
    ]

    return JsonResponse(results, safe=False)
