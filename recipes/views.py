from django.core.cache import cache
import requests
from django.http import JsonResponse
from dotenv import load_dotenv
import os
from .models import Recipe, Nutrition
from recipeingredient.models import UnitIngr, RecipeIngr
from ingredients.models import Ingredient

load_dotenv()

api_key = os.getenv('API_KEY_S')

def get_recipe(request, recipe_id):
    cache_key = f"recipe_{recipe_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return JsonResponse(cached_data)

    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}&includeNutrition=true'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        cache.set(cache_key, data, timeout=3600)  
        # populate_units_and_recipe_ingredients(recipe_id)
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Unable to fetch recipe data"}, status=500)
    
def get_recipes_list(request):
    number = request.GET.get('number', 100)

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

        return JsonResponse(data)
    elif response.status_code == 402:
        return JsonResponse({"error": "Daily points limit reached. Please try again tomorrow."}, status=402)
    else:
        return JsonResponse({"error": "Unable to fetch recipes list"}, status=500)


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