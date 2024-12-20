from django.core.cache import cache
import requests
import os 
from dotenv import load_dotenv
from ingredients.models import Ingredient 
from django.http import JsonResponse

load_dotenv() 
API_KEY = os.getenv("API_KEY")

 
 
def get_recipe(request, recipe_id):
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}&includeNutrition=true'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        for ingredient_data in data.get('extendedIngredients', []) :
            Ingredient.objects.update_or_create(
                name=ingredient_data['name'],
                defaults={
                    'id_ingredient': ingredient_data.get('id', None),   
                    'image_url': f"https://spoonacular.com/cdn/ingredients_100x100/{ingredient_data.get('image', '')}"
                }
            )
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Unable to fetch recipe data"}, status=500)


def get_recipes_list(request):
    number = request.GET.get('number', 100)  

    # url = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&query={query}&cuisine={cuisine}&diet={diet}&number={number}'
    url = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&number={number}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for recipe in data.get('results', []): 
            save_ingredients_for_recipe(recipe['id'])
        return JsonResponse(data)
    elif response.status_code == 402:
        return JsonResponse({"error": "Daily points limit reached. Please try again tomorrow."}, status=402)
    else:
        return JsonResponse({"error": "Unable to fetch recipes list"}, status=500)


# def get_recipes_list(request):
#     number = request.GET.get('number', 5)
#     cache_key = f"recipes_list_{number}"
#     cached_data = cache.get(cache_key)

#     if cached_data:
#         return JsonResponse(cached_data)

#     url = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&number={number}'
#     response = requests.get(url)

#     if response.status_code == 200:
#         data = response.json()
#         cache.set(cache_key, data, timeout=3600)  
#         return JsonResponse(data)
#     elif response.status_code == 402:
#         return JsonResponse({"error": "Daily points limit reached. Please try again tomorrow."}, status=402)
#     else:
#         return JsonResponse({"error": "Unable to fetch recipes list"}, status=response.status_code)




def save_ingredients_for_recipe(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}"
    print(f"Calling Spoonacular API with URL: {url}")
   
    response = requests.get(url)
    
    print(f"Response status code: {response.status_code}")
    print(f"Response body: {response.text}")

    if response.status_code == 200:
        recipe_details = response.json()

        for ingredient_data in recipe_details.get('extendedIngredients', []):
            spoonacular_id = ingredient_data.get('id', None)
            try: 
                Ingredient.objects.get_or_create(
                    id_ingredient=spoonacular_id,
                    defaults={
                        'name': ingredient_data.get('name'),
                        'image_url': f"https://spoonacular.com/cdn/ingredients_100x100/{ingredient_data.get('image', '')}"
                    }
                )
            except Exception as e :
                print(f"Erreur lors de l'enregistrement de l'ingrédient {ingredient_data['name']}: {e}")
                continue 

        return JsonResponse({"message": f"Ingrédients pour la recette {recipe_id} enregistrés avec succès"})
    else:
        return JsonResponse({"error": f"Unable to fetch ingredients for recipe {recipe_id}"}, status=500)
    

def get_random_recipe(request): 
    url = f"https://api.spoonacular.com/recipes/random?apiKey={API_KEY}"
    print(url)
    response = requests.get(url)
    print(response.status_code)
    
    if response.status_code == 200:
       data = response.json()
       recipes = data.get("recipes", [])

       recipe = recipes[0]
       ingredients = recipe.get("extendedIngredients", [])

       for ingredient_data in ingredients:
           Ingredient.objects.update_or_create(
               name=ingredient_data['name'],
               defaults={
                   'id_ingredient': ingredient_data.get('id', None),   
                   'image_url': f"https://spoonacular.com/cdn/ingredients_100x100/{ingredient_data.get('image', '')}"
               }
           )
 
       return JsonResponse(recipe, safe=False)
    else:
        return JsonResponse({"error": "Unable to fetch recipe data"}, status=500)
