import requests

def chatWithCohere(token, message, history, preamble="You are Cohere's chatbot, Coral, in a bot called AIDA, which stands for Artificial Intelligence Discord Assistant."):
    url = "https://api.cohere.ai/v1/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "message": message,
        "chat_history": history,
        "stream": False,
        "preamble_override": preamble
    }

    response = requests.post(url, headers=headers, json=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        text = response_json.get('text', 'No text found in the response')
        print(text)
        return text
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None
