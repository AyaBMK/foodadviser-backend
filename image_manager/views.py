from django.shortcuts import render
from django.http import JsonResponse
from .models import UploadedImage
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']

        uploaded_image = UploadedImage.objects.create(
            image=image
        )

        return JsonResponse({'message': 'Image uploaded successfully!'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)
