from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from recommandations.models import UserRecipeView
from recipes.models import Recipe
from django.shortcuts import get_object_or_404
import openai
import os
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")

class RecipeView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request, recipe_id):
        # Récupérer la recette
        recipe = get_object_or_404(Recipe, id_recipe=recipe_id)
        
        # Enregistrer la vue de la recette
        _, created = UserRecipeView.objects.get_or_create(user=request.user, recipe=recipe)
        
        if created:
            return Response({"message": f"Recette {recipe.title} vue avec succès !"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": f"Vous avez déjà vu cette recette."}, status=status.HTTP_200_OK)
        
class UserViewedRecipesView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        # Récupérer les recettes vues par l'utilisateur connecté
        viewed_recipes = UserRecipeView.objects.filter(user=request.user)
        
        # Extraire les titres des recettes
        titles = [view.recipe.title for view in viewed_recipes]
        
        if titles:
            return Response({"viewed_recipes": titles}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Aucune recette consultée."}, status=status.HTTP_404_NOT_FOUND)
        

# class RecipeRecommendationView(APIView):
#     permission_classes = [IsAuthenticated]  

#     def post(self, request):
#         viewed_recipes = UserRecipeView.objects.filter(user=request.user)
#         print("viewed_recipes", viewed_recipes, '-----------------------------------------------------------')
#         titles = [view.recipe.title for view in viewed_recipes]
#         print("titles", titles, '-----------------------------------------------------------')

#         if not titles:
#             return Response({"message": "Aucune recette consultée."}, status=status.HTTP_404_NOT_FOUND)
        
#         prompt = (
#             f"Voici une liste de titres de recettes que l'utilisateur a consultées : {', '.join(titles)}. "
#             "Propose-moi 4 catégories de plats en anglais, chacun avec un titre contenant UN SEUL MOT. "
#             "Rends la réponse au format suivant, sans aucun texte additionnel :\n"
#             "1. [Titre]\n"
#             "2. [Titre]\n"
#             "3. [Titre]\n"
#             "4. [Titre]"
#         )
#         print("prompt", prompt, '-----------------------------------------------------------')
        
#         response_openai = openai.chat.completions.create(
#             model="gpt-4o-mini",  
#             messages=[
#                 {"role": "system", "content": "Tu es un assistant intelligent."},
#                 {"role": "user", "content": prompt},
#             ],
#             max_tokens=50,
#             temperature=0.7,
#         )

#         # Extraire les titres suggérés par OpenAI
#         suggested_titles = response_openai.choices[0].message.content.strip().split("\n")
#         print("suggested_titles", suggested_titles, '-----------------------------------------------------------')
#         # suggested_titles = [title.split(".")[1].strip() for title in suggested_titles if "." in title]
#         suggested_titles = [
#             title.split(".")[1].strip()  # Extraire le texte après "1.", "2.", etc.
#             for title in suggested_titles
#             if "." in title and title.split(".")[1].strip()
#         ]
#         print("SUGGESTED TITLES", suggested_titles, '-----------------------------------------------------------')
#         # Préparer l'appel à Spoonacular
#         api_key_spoonacular = os.getenv("API_KEY_D")
#         spoonacular_url = "https://api.spoonacular.com/recipes/complexSearch"
#         recommended_recipes = []

#         # Rechercher des recettes pour chaque titre
#         for title in suggested_titles:
#             params = {
#                 "apiKey": api_key_spoonacular,
#                 "query": title,
#                 "number": 1
#             }
#             req = requests.Request("GET", spoonacular_url, params=params)
#             prepared = req.prepare()
#             print("8888888888888888", prepared.url)
#             response = requests.get(spoonacular_url, params=params)

#             if response.status_code == 200:
#                 data = response.json()
#                 if data.get("results"):
#                     recommended_recipes.append(data["results"][0])  # Ajouter la première recette trouvée
                    
#         print("Recommended_recipes---------------------:", recommended_recipes, '-----------------------------------------------------------')
#         return Response({"recommended_recipes": recommended_recipes}, status=status.HTTP_200_OK)



class RecipeRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        viewed_recipes = UserRecipeView.objects.filter(user=request.user)
        titles = [view.recipe.title for view in viewed_recipes]

        if not titles:
            return Response({"message": "Aucune recette consultée."}, status=status.HTTP_404_NOT_FOUND)

        prompt = (
            f"Voici une liste de titres de recettes que l'utilisateur a consultées : {', '.join(titles)}. "
            "Propose-moi 4 catégories de plats en anglais, chacun avec un titre contenant UN SEUL MOT. "
            "Rends la réponse au format suivant, sans aucun texte additionnel :\n"
            "1. [Titre]\n"
            "2. [Titre]\n"
            "3. [Titre]\n"
            "4. [Titre]"
        )
        print("prompt: ", prompt)
        response_openai = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un assistant intelligent."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=50,
            temperature=0.7,
        )

        suggested_titles = [
            title.split(".")[1].strip()
            for title in response_openai.choices[0].message.content.strip().split("\n")
            if "." in title and title.split(".")[1].strip()
        ]
        print("Suggest", suggested_titles)
        api_key_spoonacular = os.getenv("API_KEY")
        api_key_spoonacular1 = os.getenv("API_KEY_G")
        spoonacular_search_url = "https://api.spoonacular.com/recipes/complexSearch"
        spoonacular_details_url = "https://api.spoonacular.com/recipes/{id}/information"
        recommended_recipes = []

        for title in suggested_titles:
            print("title", title)
            params = {"apiKey": api_key_spoonacular, "query": title, "number": 1}
            print("params", params)
            response = requests.get(spoonacular_search_url, params=params)
            print("response", response)
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    recipe_id = data["results"][0]["id"]

                    # Récupérer les détails de la recette
                    details_response = requests.get(
                        spoonacular_details_url.format(id=recipe_id),
                        params={"apiKey": api_key_spoonacular1}
                    )
                    req = requests.Request("GET", spoonacular_search_url, params=params)
                    prepared = req.prepare()
                    print("8888888888888888", prepared.url)
                    if details_response.status_code == 200:
                        recipe_details = details_response.json()
                        steps = []
                        if recipe_details.get("analyzedInstructions"):
                            for instruction in recipe_details["analyzedInstructions"]:
                                steps.extend(step["step"] for step in instruction.get("steps", []))
                        recommended_recipes.append({
                            "id": recipe_details["id"],
                            "title": recipe_details["title"],
                            "image": recipe_details["image"],
                            "summary": recipe_details.get("summary", "Aucun résumé disponible."),
                            "servings": recipe_details.get("servings", "Non spécifié"),
                        })

        print("\n================================", recommended_recipes)
        return Response({"recommended_recipes": recommended_recipes}, status=status.HTTP_200_OK)

