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
    try:
        recipe = Recipe.objects.get(id_recipe=recipe_id)
        nutrition = Nutrition.objects.filter(recipe=recipe).first()

        recipe_ingredients = RecipeIngr.objects.filter(recipe=recipe)
        ingredients_data = []

        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            unit = recipe_ingredient.unit
            ingredient_data = {
                'ingredient_name': ingredient.name,
                'amount': recipe_ingredient.amount,
                'unit': unit.name if unit else None,
                'image_url': ingredient.image_url  
            }
            ingredients_data.append(ingredient_data)

        data = {
            'id_recipe': recipe.id_recipe,
            'title': recipe.title,
            'image_url': recipe.image_url,
            'instructions': recipe.instructions,
            'servings': recipe.servings,
            'ready_in_minutes': recipe.ready_in_minutes,
            'vegetarian': recipe.vegetarian,
            'vegan': recipe.vegan,
            'very_popular': recipe.very_popular,
            'preparation_minutes': recipe.preparation_minutes,
            'cooking_minutes': recipe.cooking_minutes,
            'health_score': recipe.health_score,
            'steps': recipe.steps,
            'ingredients': ingredients_data,  
            'nutrition': {
                'calories': nutrition.calories if nutrition else None,
                'protein': nutrition.protein if nutrition else None,
                'fat': nutrition.fat if nutrition else None,
                'carbohydrates': nutrition.carbohydrates if nutrition else None,
                'sugar': nutrition.sugar if nutrition else None,
                'fiber': nutrition.fiber if nutrition else None,
                'sodium': nutrition.sodium if nutrition else None,
            } if nutrition else None,
        }

        return JsonResponse(data)

    except Recipe.DoesNotExist:
        print("Recipe is not exist in BDD.. Trying to ask api...")
        return get_recipe_from_spoon(recipe_id)

def get_recipe_from_spoon(recipe_id):
    print('Spoonacular')
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}&includeNutrition=true'
    response = requests.get(url)
    try:
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data)
        else:
            return JsonResponse({"error": "Unable to fetch recipe data from API"}, status=500)
    except Exception as e:
        print("Unexpected error during API fetch")
        return JsonResponse({"error": "Unexpected error occurred while fetching data from API"}, status=500)

def get_recipes_list(request):
    number = int(request.GET.get('number', 100))  
    recipes = Recipe.objects.all()[:number]  
    recipes_data = []

    for recipe in recipes:
        recipes_data.append({
            'id_recipe': recipe.id_recipe,
            'title': recipe.title,
            'image_url': recipe.image_url,
            'servings': recipe.servings,
            'ready_in_minutes': recipe.ready_in_minutes,
            'vegetarian': recipe.vegetarian,
            'vegan': recipe.vegan,
            'very_popular': recipe.very_popular,
        })

    return JsonResponse({'recipes': recipes_data})

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
        for recipe_data in data:
            recipe_id = recipe_data['id']
            try:
                recipe = Recipe.objects.get(id_recipe=recipe_id)
                print(f"Recipe {recipe_id} already exists in the database.")
            except Recipe.DoesNotExist:
                print(f"Recipe {recipe_id} does not exist. Fetching and populating ingredients...")
        
        return JsonResponse(data, safe=False)
    
    elif response.status_code == 402:
        return JsonResponse({"error": "Daily points limit reached. Please try again tomorrow."}, status=402)
    else:
        return JsonResponse({"error": "Unable to fetch recipes list"}, status=500)