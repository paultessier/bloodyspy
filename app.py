from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from typing import List
# from pydantic import BaseModel
# from typing import Optional
import cv2
import tensorflow as tf
# from keras.preprocessing import image
import numpy as np
# import pandas as pd

# interface graphique de l'API
# http://localhost:8000/docs
# http://localhost:8000/redoc

# Manifeste OpenAPI (Json des fonctions)
# http://localhost:8000/openapi.json

# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
#SOLVING ISSUE : rebuild TensorFlow with the appropriate compiler flags
#Your kernel may have been built without NUMA support


api = FastAPI(
    title="API - bloody spy",
    description="This API aims to categorize blood cells",
    version="1.0.1",
    # port =8001
)


# ==== PARAMETERS ===================================================================

# On crée la liste des noms des différents dossiers de types de cellules présents dans le dossier data_samples
cell_types = ['neutrophil', 'eosinophil', 'ig', 'platelet', 'erythroblast', 'monocyte','basophil','lymphocyte']
# On crée la liste des noms des différentes types de cellules que l'on souhaite afficher à l'avenir
cell_types2 = ['neutrophil', 'eosinophil', 'immature granulocyte', 'platelet', 'erythroblast', 'monocyte','basophil','lymphocyte']


# ==== API STATUS ===================================================================

@api.get('/api/status', name='Verify status of the API')
def get_status():
    """Returns a success status if the API is working.
    """
    return {
            "status": "success",
            "message": "Hello from a public endpoint! You don't need to be authenticated to see this."
    }


# ===== INFO ROUTES ===================================================================

# -------------------------------------------------------------------
# 1/ Upload file
# -------------------------------------------------------------------

@api.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}

@api.post("/uploadfile/")
async def create_upload_file(file: UploadFile):

    if not file:
        return {"message": "No upload file sent"}
    
    extension = file.filename.split('.')[-1]
    tmp_filename = f"tmp/tmp_img.{extension}"
    with open(tmp_filename, "wb+") as file_object:
        file_object.write(file.file.read())

    # On stocke l'image en RGB
    img_rgb = cv2.imread(tmp_filename,cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)

    # resize and filter
    img_f = cv2.resize(img_rgb,dsize = (60,60))

    # Normalization of pixels value
    # img_tf = image.img_to_array(img_f)/255
    img_tf = tf.keras.utils.img_to_array(img_f)/255
    print(img_tf.shape)

    #On ajoute une dimension à l'image
    # img_tf = np.expand_dims(img_tf.tolist(), axis = 0)
    # img_tf = np.expand_dims(img_tf, axis = 0)
    img_tf = np.expand_dims(img_tf, axis = 0)
    print(img_tf.shape)

    # On charge le modèle choisit par l'utilisateur
    k=0
    available_models=['FS','ResNet50','VGG16','VGG19','Xception']
    model = tf.keras.models.load_model('./models/Save_model_CNN_'+available_models[k]+'_60x60_rgb.h5')

    # On stocke les valeurs de probabilité des classes de l'image
    probas = model.predict(img_tf)[0]
    probabilities = {c:p for c,p in zip(cell_types2,probas)}

    # On stocke la classe retournée et la proba
    pred_proba = np.max(probas)*100
    pred_cell_type = cell_types2[np.argmax(probas)]

    return {
        "filename": file.filename,
        "model":available_models[k],
        "predictions":probabilities,
        "predicted_blood_cell_type":pred_cell_type,
        "prediction_probability":pred_proba
    }


@api.post("/uploadfile2/")
async def create_upload_file(file: UploadFile):
    # print(dir(file))
    extension = file.filename.split('.')[-1]
    tmp_filename = f"tmp/tmp_img.{extension}"
    with open(tmp_filename, "wb+") as file_object:
        file_object.write(file.file.read())

    return {
        "filename": file.filename,
        "content":file.content_type,
        "file":file.file,
        "headers":file.headers
    }


# -------------------------------------------------------------------
# 1/ Upload files
# -------------------------------------------------------------------

@api.post("/uploadfiles/")
async def create_upload_files(
    files: List[UploadFile] = File(description="Multiple files as UploadFile"),
):
    return {"filenames": [file.filename for file in files]}






