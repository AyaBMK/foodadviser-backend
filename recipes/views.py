from django.core.cache import cache
import requests
from django.http import JsonResponse
from dotenv import load_dotenv
import os
from .models import Recipe, Nutrition
from recipeingredient.models import UnitIngr, RecipeIngr
from ingredients.models import Ingredient
from django.db.utils import IntegrityError

load_dotenv()

api_key = os.getenv('API_KEY_E')

def get_recipe(request, recipe_id):
    cache_key = f"recipe_{recipe_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return JsonResponse(cached_data)

    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}&includeNutrition=true'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        update_or_create_ingredients_from_api(recipe_id)
        cache.set(cache_key, data, timeout=3600)  # Cache the data for an hour
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Unable to fetch recipe data"}, status=500)



def get_recipes_list(request):
    number = int(request.GET.get('number', 100))  
    recipes = Recipe.objects.all()[:number]  
    recipes_data = []

    # Premièrement, récupère la liste des recettes
    url = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={api_key}&number={number}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        recipe_ids = [recipe['id'] for recipe in data.get('results', [])]

        # Pour chaque recette, récupérer ses détails
        for recipe_id in recipe_ids:
            # Vérifier si la recette existe dans le cache ou base de données avant de récupérer ses détails
            cached_recipe = cache.get(f"recipe_{recipe_id}")
            if not cached_recipe:
                get_recipe_and_populate_ingredients(recipe_id)
                # update_or_create_ingredients_from_api(recipe_id)

        return JsonResponse(data)
    elif response.status_code == 402:
        return JsonResponse({"error": "Daily points limit reached. Please try again tomorrow."}, status=402)
    else:
        return JsonResponse({"error": "Unable to fetch recipes list"}, status=500)

def update_or_create_ingredients_from_api(recipe_id):
    # URL de l'API pour récupérer les informations d'une recette
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        ingredients_data = data.get("extendedIngredients", [])
        
        for ingredient_data in ingredients_data:
            ingredient_name = ingredient_data["name"]
            ingredient_id = ingredient_data["id"]
            ingredient_image_url = f"https://spoonacular.com/cdn/ingredients_100x100/{ingredient_data.get('image', '')}"  # Construire l'URL complète de l'image

            # Vérifier si l'ingrédient existe déjà dans la base de données
            ingredient, created = Ingredient.objects.update_or_create(
                id_ingredient=ingredient_id,  # Recherche par id_ingredient
                defaults={'name': ingredient_name, 'image_url': ingredient_image_url}
            )
            if created:
                print(f"Ingrédient créé : {ingredient_name} (ID: {ingredient_id})")
            else:
                print(f"Ingrédient mis à jour : {ingredient_name} (ID: {ingredient_id})")
        
        print("Mise à jour ou création des ingrédients terminée.")
    else:
        print(f"Erreur lors de la récupération des ingrédients pour la recette {recipe_id}. Status code: {response.status_code}")


# def update_or_create_ingredients_from_api(recipe_id):
#     # URL de l'API pour récupérer les informations d'une recette
#     url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"
#     response = requests.get(url)

#     if response.status_code == 200:
#         data = response.json()
#         ingredients_data = data.get("extendedIngredients", [])
        
#         # Parcours des ingrédients de la recette
#         for ingredient_data in ingredients_data:
#             ingredient_id = ingredient_data['id']
#             ingredient_name = ingredient_data['name']
#             ingredient_image_url = f"https://spoonacular.com/cdn/ingredients_100x100/{ingredient_data.get('image', '')}"

#             # Recherche si l'ingrédient existe déjà
#             ingredient, created = Ingredient.objects.get_or_create(
#                 id_ingredient=ingredient_id,
#                 defaults={'name': ingredient_name, 'image_url': ingredient_image_url}
#             )
            
#             if created:
#                 print(f"Ingrédient créé : {ingredient_name} (ID: {ingredient_id})")
#             else:
#                 # Si l'ingrédient existe déjà, on peut le mettre à jour si nécessaire
#                 if ingredient.name != ingredient_name or ingredient.image_url != ingredient_image_url:
#                     ingredient.name = ingredient_name
#                     ingredient.image_url = ingredient_image_url
#                     ingredient.save()
#                     print(f"Ingrédient mis à jour : {ingredient_name} (ID: {ingredient_id})")
#                 else:
#                     print(f"Ingrédient déjà à jour : {ingredient_name} (ID: {ingredient_id})")
                
#     else:
#         print(f"Échec de la récupération des données pour la recette {recipe_id}. Code HTTP : {response.status_code}")




def get_recipe_and_populate_ingredients(recipe_id):
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}&includeNutrition=true'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        ingredients_data = data.get("extendedIngredients", [])
        try:
            recipe = Recipe.objects.get(id_recipe=recipe_id)

            # Précharger les unités et ingrédients existants
            existing_units = {unit.name: unit for unit in UnitIngr.objects.all()}
            existing_ingredients = {ingredient.id_ingredient: ingredient for ingredient in Ingredient.objects.all()}

            for ingredient_data in ingredients_data:
                ingredient_name = ingredient_data["name"]
                amount = ingredient_data["amount"]
                unit_name = ingredient_data["unit"]
                ingredient_id = ingredient_data["id"]

                # Gérer l'unité (ajout ou récupération de l'unité)
                unit = existing_units.get(unit_name)
                if not unit:
                    unit, created = UnitIngr.objects.get_or_create(name=unit_name)
                    existing_units[unit_name] = unit

                # Gérer l'ingrédient (ajout ou mise à jour)
                ingredient = existing_ingredients.get(ingredient_id)
                if not ingredient:
                    ingredient, created = Ingredient.objects.get_or_create(
                        id_ingredient=ingredient_id,
                        defaults={'name': ingredient_name}
                    )
                    existing_ingredients[ingredient_id] = ingredient
                else:
                    # Si l'ingrédient existe déjà, mettre à jour son nom si nécessaire
                    if ingredient.name != ingredient_name:
                        ingredient.name = ingredient_name
                        ingredient.save()

                # Ajouter ou récupérer l'entrée dans RecipeIngr (assurer l'unicité)
                recipe_ingredient, created = RecipeIngr.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount,
                    unit=unit
                )

                # Log des ajouts ou mises à jour
                if created:
                    print(f"Added {ingredient_name} to recipe {recipe.title} with amount {amount} {unit_name}")
                else:
                    print(f"Updated {ingredient_name} in recipe {recipe.title}")

        except Recipe.DoesNotExist:
            print(f"Recipe with id {recipe_id} not found.")
        except Exception as e:
            print(f"An error occurred while processing recipe {recipe_id}: {e}")

    else:
        print(f"Error fetching details for recipe {recipe_id}. Status code: {response.status_code}")

def getRecipesSuggestionList(request): 
    ingredients = request.GET.get('list', '')
    number= int(request.GET.get('number', 8))
    print("Ingredients:", ingredients)
    print("Number:", number)

    if not ingredients:
            return JsonResponse({"error": "Missing 'list' parameter"}, status=400)
    
    url=(
            f'https://api.spoonacular.com/recipes/findByIngredients'
            f'?ingredients={ingredients}&number={number}&apiKey={api_key}'
        )
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return JsonResponse(data, safe=False)
    
    elif response.status_code == 402:
        return JsonResponse({"error": "Daily points limit reached. Please try again tomorrow."}, status=402)
    else:
        return JsonResponse({"error": "Unable to fetch recipes list"}, status=500)
