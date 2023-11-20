import requests
from dotenv import load_dotenv
import os
import random

async def query_jug(payload):
    API_URL = "https://api-inference.huggingface.co/models/openskyml/dalle-3-xl"
    load_dotenv()
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE')}"}
    payload['seed'] = random.randint(0, 2**32 - 1)
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content
