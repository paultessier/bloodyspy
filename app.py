from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from pydantic import BaseModel
from typing import Optional
# import numpy as np
import pandas as pd

# interface graphique de l'API
# http://localhost:8000/docs
# http://localhost:8000/redoc

# Manifeste OpenAPI (Json des fonctions)
# http://localhost:8000/openapi.json


api = FastAPI(
    title="API - test questions",
    description="This API, powered by FastAPI, aims to manage a serie of tests.",
    version="1.0.1")

test_db = pd.read_csv('questions.csv')

creds = {
  "alice": "wonderland",
  "bob": "builder",
  "clementine": "mandarine",
  "admin":"4dm1N"
}

rights = {
  "alice": "read",
  "bob": "read",
  "clementine": "read",
  "admin":"admin"
}

class Test(BaseModel):
    use: str
    subjects: Optional[list]
    N_questions: Optional[int]

class Question(BaseModel):
    question: str
    use: str
    subject: str
    correct: str
    repA: str
    repB: str
    repC: str
    repD: Optional[str]
    remark: Optional[str]

    

# ==== API STATUS ===================================================================

@api.get('/api/public_status', name='Verify status of the API')
def get_status():
    """Returns a success status if the API is working.
    """
    return {
  "status": "success",
  "msg": "Hello from a public endpoint! You don't need to be authenticated to see this."
}



# curl -X GET -i 'http://127.0.0.1:8000/api/public_status'




# ===== AUTHENTIFICATION TEST ===================================================================
@api.get('/auth', name='Get all uses and subjects')
def get_headers(req: Request):
    auth=req.headers["authorization"]
    username=auth.split('=')[0]
    pwd=auth.split('=')[1]
    return {'detail':req.headers,'auth':auth,'user':username,'pwd':pwd}

# curl -X GET -i 'http://127.0.0.1:8000/auth' -H 'authorization:alice=wonderland'

# ===== INFO ROUTES ===================================================================

# -------------------------------------------------------------------
# 1/ Upload files
# -------------------------------------------------------------------

@api.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}

@api.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

# -------------------------------------------------------------------
# 1/ Get information on all uses available in the test database
# -------------------------------------------------------------------

@api.get('/tests', name='Get all types of tests')
def get_test_uses():
    """Returns all uses of the test database.
    """
    # uses = [x for x in test_db.use.unique()]
    uses = list(test_db.use.unique())
    return {'uses':uses}

# curl -X GET -i 'http://127.0.0.1:8000/tests'

# -------------------------------------------------------------------
# 2/ Get information on all subjects available for a specific use
# -------------------------------------------------------------------

@api.post('/tests', name='Get all subjects of test for a given type of use')
def post_test_subject(test: Test):
    """Returns the list of subjects for a given use.
    """
    q2 = test_db[test_db.use == test.use]
    subjects = list(q2.subject.unique())
    return {
        'use': test.use,
        'subjects':subjects
        }

# curl -X POST -i 'http://127.0.0.1:8000/tests' -H 'Content-Type: application/json' -d '{"use":"Test de positionnement"}'

# -------------------------------------------------------------------
# 3/ Get direct information of all available categories
# -------------------------------------------------------------------

@api.get('/all_categories', name='Get all uses and subjects')
def get_all_categories():
    """Returns the list of uses and subjects.
    """
    d2=dict()
    for i,u in enumerate(list(test_db.use.unique())):
        d2['category n°'+str(i+1)]={
        'use':u,
        'subjects':list(test_db[test_db.use == u].subject.unique())}
    return d2

# curl -X GET -i 'http://127.0.0.1:8000/all_categories'


# ==== CREATE A TEST ===========================================================================================

@api.post('/new_test', name='Create a test')
def post_questions(req: Request, test: Test):
    """Returns a test with a list of N questions
    """

    # Authentification
    auth=req.headers["authorization"]
    username=auth.split('=')[0]
    pwd=auth.split('=')[1]
    print(username)

    try:

        auth0 = (creds[username] == pwd)
        if auth0==False:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: wrong password."
            )

    except KeyError:
        auth0=False
        raise HTTPException(
            status_code=401,
            detail='Unknown username {}.'.format(username)
        )
    
    
    if auth0:
    
        # Select the questions in the database, based on use, subjects and N_questions parameters
        q = test_db[test_db.use == test.use]
        if test.subjects:
            q = q[q['subject'].isin(test.subjects)]
        if test.N_questions:
            if test.N_questions in [5,10,20]:
                q = q.sample(n=test.N_questions,replace=True)
            else:
                return "You must choose a number of questions within 5, 10 or 20."

        # format questions as a list
        d = []
        q=q.fillna("/")
        for i in range(len(q)):
            if q.iloc[i]['responseD'] != "/":
                d.append({
                    'question':q.iloc[i]['question'],
                    'responseA':q.iloc[i]['responseA'],
                    'responseB':q.iloc[i]['responseB'],
                    'responseC':q.iloc[i]['responseC'],
                    'responseD':q.iloc[i]['responseD']
                })
            else:
                d.append({
                    'question':q.iloc[i]['question'],
                    'responseA':q.iloc[i]['responseA'],
                    'responseB':q.iloc[i]['responseB'],
                    'responseC':q.iloc[i]['responseC']
                })

        return {
            'username':username,
            'password':pwd,
            'access':'Authorized',
            'use':test.use,
            'subjects':test.subjects,
            'test':d
            }

# curl -X POST -i 'http://127.0.0.1:8000/new_test' -H 'Content-Type: application/json' -H 'authorization:alice=wonderland' -d '{"use":"Test de validation","subjects":["Classification","Automation"],"N_questions":10}'
# curl -X POST -i 'http://127.0.0.1:8000/new_test' -H 'Content-Type: application/json' -H 'authorization:alice=wonder' -d '{"use":"Test de positionnement","subjects":["BDD"],"N_questions":5}'
# curl -X POST -i 'http://127.0.0.1:8000/new_test' -H 'Content-Type: application/json' -H 'authorization:Toto=lasticot' -d '{"use":"Test de positionnement","subjects":["BDD"],"N_questions":5}'



# ==== ADD A NEW QUESTION TO THE DATABASE ===========================================================================================

@api.put('/new_question', name='Insert a new question. You need to have admin rights')
def put_new_question(req: Request, question: Question):

    # Authentification
    auth=req.headers["authorization"]
    username=auth.split('=')[0]
    pwd=auth.split('=')[1]
    print(username)

    try:

        auth0 = (creds[username] == pwd)
        if auth0==False:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: wrong password."
            )
        else:
            auth0 = (rights[username] == 'admin')
            if auth0==False:
                raise HTTPException(
                status_code=401,
                detail="Unauthorized: you do not have admin rights.")

    except KeyError:
        auth0=False
        raise HTTPException(
            status_code=401,
            detail='Unknown username {}.'.format(username)
        )
    
    if auth0:

        new_q = {
            'question': question.question,
            'subject': question.subject,
            'use': question.use,
            'correct': question.correct,
            'responseA': question.repA,
            'responseB': question.repB,
            'responseC': question.repC,
            'responseD': question.repD,
            'remark':question.remark
        }

        df_new_q = pd.DataFrame(new_q,index=[len(test_db)])
        test_db=pd.concat([test_db,df_new_q])

    return {'status':'added successfully',
            'added row to DB':new_q }


# curl -X PUT -i 'http://127.0.0.1:8000/new_question' \
# -H 'Content-Type: application/json' \
# -H 'authorization:admin=4dm1N' \
# -d '{"question":"Au cours de quel évènement historique fut crée le pancake ?", \
#      "subject":"Streaming de données", \
#      "use":"Test de validation", \
#     "correct":"A,B,C,D", \
#     "repA":"En 1618, pendant la guerre des croissants au beurre", \
#     "repB":"En 1702, pendant le massacre de la Saint-Panini", \
#     "repC": "En 112 avant Céline Dion, pendant la prise de la Brioche", \
#     "repD":"La réponse D", \
#     "remark":"C est votre ultime bafouille, Guy ?" }'






