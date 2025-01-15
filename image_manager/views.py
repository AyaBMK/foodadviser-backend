from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UploadedImage
from .services.yolo import detect_ingredients_yolo, detect_ingredients_openai
import os

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']

        uploaded_image = UploadedImage.objects.create(image=image)

        image_path = uploaded_image.image.path

        try:
            # detected_objects = detect_ingredients_yolo(image_path)
            detected_objects = detect_ingredients_openai(image_path)
            print("avant de retourner : ", detected_objects)
            return JsonResponse({'message': 'Image uploaded successfully!', 'detected_objects': detected_objects}, status=200)
        except Exception as e:
            print("Erreur : ", str(e))
            return JsonResponse({'error': f'Erreur lors de la détection des objets : {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
