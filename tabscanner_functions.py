import requests
import json
from dotenv import load_dotenv
import os

# load your environment containing the api key
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

def callProcess(API_KEY, image_path):

    endpoint = "https://api.tabscanner.com/api/2/process"
    receipt_image = image_path
    print("receipt_image: " + receipt_image)

    payload = {"documentType":"receipt"}
    files = {'file': open(receipt_image, encoding="utf8", errors='ignore')}
    print(files['file'])
    headers = {'apikey':API_KEY}

    print(endpoint)

    response = requests.post( endpoint,
                              files=files,
                              data=payload,
                              headers=headers)
    result = json.loads(response.text)

    return result