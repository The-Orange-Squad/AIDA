import requests
from dotenv import load_dotenv
import os
import random

async def query_dreamshaper(payload):
    API_URL = "https://api-inference.huggingface.co/models/Lykon/dreamshaper-8"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE')}"}
    load_dotenv()
    payload['seed'] = random.randint(0, 2**32 - 1)
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content
