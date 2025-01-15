from ultralytics import YOLO
import cv2
import numpy as np
import base64
import openai 
import json 
import os

model = YOLO('yolov8n.pt')

def detect_ingredients_yolo(image_path):
    """
    Effectue la détection d'objets sur une image donnée et formate les résultats.
    Args:
        image_path (str): Chemin de l'image.
    Returns:
        list: Liste unique des objets détectés.
    """
    
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image non trouvée au chemin : {image_path}")

    results = model(image)

    detected_objects = []
    for r in results[0].boxes.data:  
        _, _, _, _, confidence, class_id = r.cpu().numpy()
        label = results[0].names[int(class_id)]  

        detected_objects.append({"name": label})

    unique_detected_objects = list({obj["name"]: obj for obj in detected_objects}.values())

    return unique_detected_objects 

# Getting the base64 string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    

def detect_ingredients_openai(image_path):
    openai.api_key = os.getenv("OPENAI_API_KEY_IMG")
    print(openai.api_key)
    print("Entréé")
    base64_image = encode_image(image_path)

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"""
                    You will analyze the image and return only the ingredients in JSON format.
                    The JSON should follow this structure:
                    {{
                        "ingredients": [
                            {{"name": "ingredient_name"}}
                        ]
                    }}
                    Do not add any text or explanation outside this JSON structure.

                    Here is the image:
                    ![image](data:image/jpeg;base64,{base64_image})
                """
                        }
                    ],
    )


    response_content = response.choices[0].message.content
    print(response_content)
    try:
        cleaned_content = response_content.strip("```json").strip("```").strip()
        response_json = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        print("Erreur de parsing JSON :", str(e))
        print("Contenu à parser :", response_content)
        raise ValueError("La réponse de l'API n'est pas au format JSON valide.")
 
    if isinstance(response_json, dict) and "ingredients" in response_json:
        ingredients = response_json["ingredients"]
        if not isinstance(ingredients, list):
            raise ValueError("La clé 'ingredients' ne contient pas une liste.")
        return json.dumps(ingredients, indent=4)
    else:
        print("Structure inattendue :", response_json)
        raise ValueError("La réponse JSON ne contient pas la clé 'ingredients'.")