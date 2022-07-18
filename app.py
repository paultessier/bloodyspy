from fastapi import FastAPI, File, UploadFile
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from typing import List
# from fastapi import Request
# from pydantic import BaseModel
# from typing import Optional
import cv2
import tensorflow as tf
import numpy as np
import re
import os

# interface graphique de l'API
# http://localhost:8000/docs
# http://localhost:8000/redoc

# Manifeste OpenAPI (Json des fonctions)
# http://localhost:8000/openapi.json

# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
#SOLVING ISSUE : rebuild TensorFlow with the appropriate compiler flags
#Your kernel may have been built without NUMA support





# ==== PARAMETERS ===================================================================

# List of blood cell types
cell_types = ['neutrophil', 'eosinophil', 'immature granulocyte', 'platelet', 'erythroblast', 'monocyte','basophil','lymphocyte']

model_code2name={
    'FS':'CNN',
    'ResNet50':'TL ResNet50',
    'VGG16':'TL VGG16',
    'VGG19':'TL VGG19',
    'Xception':'TL Xception'
}



# ==== MAIN ===================================================================

api = FastAPI(
    title="bloodyspy API",
    description="This API classes images among {} blood cell types :\n{}"
    .format(
        len(cell_types),
        '\n'.join(['  - '+c for c in cell_types])
        ),
    version="1.0.0"
)

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = {

    "root" : {
        "username" :  "root",
        "name" : "Root user",
        "hashed_password" : pwd_context.hash('root_password'),
    },

    "alice": {
        "username": "alice",
        "name": "Alice in wonderland",
        "hashed_password": pwd_context.hash('wonderland'),
    },

    "paul" : {
        "username" :  "paul",
        "name" : "paul tessier",
        "hashed_password" : pwd_context.hash('hello_pwd'),
    }

}

# class PATH(BaseModel):
#     path: str


# ==== FUNCTIONS ===================================================================

def get_prediction(file, entrytype='file', model_code='VGG19'):

    if entrytype=='file':
        extension = file.filename.split('.')[-1]
        tmp_filename = f"tmp/tmp_img.{extension}"
        with open(tmp_filename, "wb+") as file_object:
            file_object.write(file.file.read())
            file_object.close()

    elif entrytype=='name':
        tmp_filename = file

    else:
        return 'error: bad entry_type option. should be file or name'

    # On stocke l'image en RGB
    img_rgb = cv2.imread(tmp_filename,cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)

    # resize and filter
    img_f = cv2.resize(img_rgb,dsize = (60,60))

    # Normalization of pixels value
    img_tf = tf.keras.utils.img_to_array(img_f)/255
    # print(img_tf.shape)

    #On ajoute une dimension à l'image
    img_tf = np.expand_dims(img_tf, axis = 0)
    # print(img_tf.shape)

    # we load the chosen model
    model = tf.keras.models.load_model('./models/Save_model_CNN_'+model_code+'_60x60_rgb.h5')

    # probabilities for the image to be part of each class (=blood cell type)
    probas = model.predict(img_tf)[0]
    
    # We store probabilities, and get the predicted blood cell type with its probability
    # probabilities = {c:p*100 for c,p in zip(cell_types,probas)}
    # pred_proba = np.max(probas)*100
    probabilities = {c:round(p*100,2) for c,p in zip(cell_types,probas)}
    pred_proba = round(np.max(probas)*100,2)
    pred_cell_type = cell_types[np.argmax(probas)]

    return {
        "filename": file.filename,
        "model":model_code2name[model_code],
        "predictions":probabilities,
        "predicted":pred_cell_type,
        "probability":pred_proba
    }


def is_img(filename):

    regex = "([^\\s]+(\\.(?i)(jpe?g|png|gif|bmp))$)" # Regex to check valid image file extension.
    p = re.compile(regex) # Compile the ReGex
    if re.search(p, filename):
        return True
    else:
        return False


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    if not(users.get(username)) or not(pwd_context.verify(credentials.password, users[username]['hashed_password'])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ===== ROUTES ===================================================================

# -------------------------------------------------------------------
# 1/ Status
# -------------------------------------------------------------------

@api.get('/bloodyspy/status', name='Verify status of the API')
def get_status():
    """Returns a status=1 if the API is working.
    """
    return {
            "status": 1,
            "message": "Hello from a public endpoint. You don't need to be authenticated to see this message."
    }


# -------------------------------------------------------------------
# 2/ Upload image and get blood cell type
# -------------------------------------------------------------------

# @api.post("/files/")
# async def create_file(file: bytes = File()):
#     return {"file_size": len(file)}

@api.post("/bloodyspy/image/", name='Get the cell type of the image uploaded')
async def predict_img(
    file: UploadFile,
    username: str = Depends(get_current_user)
):
    """Returns basic information from the model, applied on a single image file.
    """

    if not file:
        return {'username':username,'error': 'No file sent'}
    
    if is_img(file.filename):
        print(file.filename)
        result = get_prediction(file)
        result['username']=username
    else:
        return {
            'username':username,
            'filename':file.filename,
            'error':'not an image'
        }
    
    return result


# -------------------------------------------------------------------
# 3/ Upload several images and get blood cell types
# -------------------------------------------------------------------

@api.post("/bloodyspy/images/", name='Get the cell type of several images uploaded')
async def predict_imgs(
    files: List[UploadFile] = File(description="Multiple files as UploadFile"),
    username: str = Depends(get_current_user)
):
    """Returns basic information from the model, applied on several image files.
    """

    if not files:
        return {'username':username,'error': 'No file sent'}

    result=dict()
    result['username']=username
    for file in files:
        if is_img(file.filename):
            result[file.filename]=get_prediction(file)
        else:
            result[file.filename]={'filename':file.filename,'error':'not an image'}
            
    return result

# -------------------------------------------------------------------
# 3/ Browse a folder
# -------------------------------------------------------------------

# @api.post("/bloodyspy/path/")
# async def predict_imgsInfolder(data : PATH):

#     for root, _, files in os.walk(data.path):
#         img_files=[]
#         for file in files:
#             if is_img(file):
#                 img_files.append(os.path.join(root,file))

#     print(img_files[:20])

#     result=dict()
#     for filename in img_files:
#         print(filename)
#         result[filename]=get_prediction(file,entrytype='name')

#     return result







