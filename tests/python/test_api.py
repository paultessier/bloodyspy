import os
import requests
import base64
import numpy as np
from datetime import datetime
import time

# ========================================================
#     Initialization
# ========================================================

# ============= API Address definition ===================

if os.getenv('DEV_MODE')=='OFF':
    time.sleep(8) # wait for 8 secondes, to let time to the api container to launch
    # api_address = 'bloodyspy-container' # name of the fast API container within the network
    api_address =  os.getenv('API_CONTAINER_NAME') # name of the fast API container within the network
else:
    # api_address = '0.0.0.0'
    api_address = 'localhost'

api_port = 8000 # port de l'API
url_api = 'http://{address}:{port}'.format(address=api_address, port=api_port)

# ============= Fix parameters ===========================

test ={
    'status': {
        'endpoint': '/bloodyspy/status'
    },
    'authorization': {
        'endpoint': '/bloodyspy/authorization',
        'usernames': ['root','alice','paul'],
        'passwords': ['root_password','wonderland','hello_pwd']
    },
    'content': {
        'endpoint': '/bloodyspy/image',
        'Authorization': 'Basic cGF1bDpoZWxsb19wd2Q=',
        'files' : [
            'data/sample/basophil/BA_53335.jpg',
            'data/sample/eosinophil/EO_676281.jpg',
            'data/sample/erythroblast/ERB_507848.jpg',
            'data/sample/ig/MMY_677451.jpg',
            'data/sample/lymphocyte/LY_301320.jpg',
            'data/sample/monocyte/MO_254452.jpg',
            'data/sample/neutrophil/BNE_436569.jpg',
            'data/sample/platelet/PLATELET_38734.jpg'
        ],
        'cell_types' : [
            'basophil',
            'eosinophil',
            'erythroblast',
            'immature granulocyte',
            'lymphocyte',
            'monocyte',
            'neutrophil',
            'platelet'
        ],
    }
}

success =[]

def add_output(old_result,result):
    print(result)
    new_result=old_result+result
    return(new_result)


# ========================================================
#     Print Date & Time
# ========================================================

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# Initialize results with the DATE AND TIME
output = add_output('', '''
========================================================
REQUEST DATE TIME : {}
========================================================
'''.format(dt_string)
)


# ========================================================
#     Test /status endpoint
# ========================================================

# Request the API
r = requests.get(
    url=url_api+test['status']['endpoint']
)

# Get JSON from the request and calculate result variables
result_json = r.json()
test_status = 'SUCCESS' if result_json['status']==1 else 'FAILURE'
success.append((test_status=='SUCCESS')*1)

# Save the formated output
output = add_output(output, '''
========================================================
    Status test
========================================================

    request status_code: {status_code}
    status: {status}
    message: {message}
    ==>  {test_status}
    '''.format(
        status_code = r.status_code,
        status = result_json['status'],
        message = result_json['message'],
        test_status = test_status
    )
)

# ========================================================
#     Test /authorization endpoint
# ========================================================

output = add_output(output,'''
========================================================
    Authorization test
========================================================

'''
)

for username, pwd in zip(test['authorization']['usernames'],test['authorization']['passwords']):

    auth = '{}:{}'.format(username,pwd)
    auth_encoded = base64.b64encode(bytes(auth, "utf-8")).decode("utf-8") 

    # Request the API
    r = requests.get(
        url=url_api+test['authorization']['endpoint'],
        headers = {
                'Authorization': 'Basic {}'.format(auth_encoded)
            }
    )

    # Get JSON from the request and calculate result variables
    result_json = r.json()
    test_status = 'SUCCESS' if result_json['status']==1 else 'FAILURE'
    success.append((test_status=='SUCCESS')*1)

    # Save the formated output
    output = add_output(output, '''
    request status code: {status_code}
    status: {status}
    message: {message}
    ==>  {test_status}

        '''.format(
            status_code = r.status_code,
            status = result_json['status'],
            message = result_json['message'],
            test_status = test_status
        )
    )

# ========================================================
#     Test /image endpoint 
# ========================================================

output = add_output(output, '''
========================================================
    Content test
========================================================

# LOGIN USED
    | username : paul
    | Authorization : Basic cGF1bDpoZWxsb19wd2Q=

    '''
)

for k in range(len(test['content']['files'])):

    filename = test['content']['files'][k]
    exp_cell_type = test['content']['cell_types'][k]

    # Request the API
    r = requests.post(
        url=url_api+test['content']['endpoint'],
        headers = {
            'Authorization': test['content']['Authorization']
        },
        files = {'file': open(filename, 'rb')},
    )

    # print(r.text)
    result_json = r.json()

    # get the predictions from the model
    pred_cell_type = result_json['predicted']
    proba = result_json['probability']

    # calculate results
    test_status = 'SUCCESS' if pred_cell_type == exp_cell_type else 'FAILURE'
    success.append((test_status=='SUCCESS')*1)

    # Save the formated output
    output = add_output(output, '''
--- FILE N°{num} -----------------------------
--- "{filename}"
    request status code: {status_code}
    expected blood cell type: {exp_cell_type}
    predicted blood cell type: {pred_cell_type}
    probability: {proba} %
    ==>  {test_status}
        '''.format(
            num=str(k+1),
            filename=filename,
            status_code=r.status_code,
            exp_cell_type=exp_cell_type,
            pred_cell_type=pred_cell_type,
            proba=proba,
            test_status=test_status
        )
    )


# ========================================================
#     Overall results
# ========================================================

# Save the formated output
output = add_output(output, '''
========================================================
    Test overview
========================================================

    Test results: {}
    ==> Overall test success: {}
    '''.format(
        success,
        np.prod(success)==1
    )
)

# ========================================================
#     Save to the log file
# ========================================================

if int(os.getenv('SAVE_LOG'))==1:

    with open('log/api_tests_py.log', 'a') as file: # to add at the end of the log file
    # with open('log/'+filename, 'w') as file: # to overwrite last log file
        file.write(output)
        file.close()

    output_summary = 'Date: {}. Results: {}. Overall: {}\n'.format(dt_string,success,'OK' if np.prod(success)==1 else 'NOK')
    with open('log/api_tests_py_summary.log', 'a') as file: # to add at the end of the log file
    # with open('log/'+filename, 'w') as file: # to overwrite last log file
        file.write(output_summary)
        file.close()
    
    print("""

========================================================
    log/{} created successfully.
    log/summary_{} created successfully.
        
    """.format(filename,filename)
    )