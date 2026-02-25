import os
import json
import uuid
import requests

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# PROMPTS
def summarize_technologies(file_input: str):
    summarization = f"""
    Task: Gven text below extract all the technologies, following the instructions\n
    Text: {file_input}\n
    INSTRUCTION: Give an answer of the form that is similar to example
    EXAMPLE: LLM and their usage in the modern world. But how do you actually write code
    that is similar to code in production? Using Git, of course. The models are usually trained using
    the optimizers: like Adam, SGD and many other 
    
    LLM (their usage in the modern world) Git (code in production) Optimizers (Adam, SGD for training models)

    WHAT NOT TO DO: Write any additional text that is not related to technologies extracted  
"""
    return summarization

def suggest_additions(tech: str, additional_text: str) -> str:
    augmented_with_chunks = f"""
    Given the technologies and additional information, write suggestions of technologies to add base on information\n
    TECHNOLOGIES: {tech}\n
    INFORMATION: {additional_text}\n
    WHAT NOT TO DO:
    Write something besides the technologies to add
"""
    return augmented_with_chunks
# TOKENS
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

# Functions
def get_access_token(auth_token):
  url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

  payload = 'scope=GIGACHAT_API_PERS'
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': f'{str(uuid.uuid4())}',
    'Authorization': f'Basic {auth_token}'
  }

  response = requests.request("POST", url, headers=headers, data=payload, verify=False)

  ACCCESS = response.text
  ACCCESS_TOKEN = json.loads(ACCCESS)["access_token"]
  return ACCCESS_TOKEN


def generate_tokens(prompt: str, access_token: str = get_access_token(AUTH_TOKEN)) -> str:
    rq_uid = str(uuid.uuid4())
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    payload = json.dumps({
    "model": "GigaChat",
    "messages": [
        {
        "role": "user",
        "content": prompt,
        }
    ],
    "temperature": 1,
    "top_p": 0.1,
    "stream": False,
    "n": 1,
    "max_tokens": 2048,
    "repetition_penalty": 1,
    "update_interval": 0
    })
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    "RqUID": rq_uid,
    'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    return json.loads(response.text)["choices"][0]["message"]["content"]

def get_similar_db_chunks(content: str) -> str:
    pass

# API class
app = FastAPI()

class TokenRequest(BaseModel):
    text: str

class TokenResponse(BaseModel):
    tokens: str

@app.post("/generate-tokens", response_model = TokenResponse)
def create_token(request: TokenRequest):
    technology_summary = generate_tokens(summarize_technologies(request.text))
    augmentation = requests.request("POST", "http://localhost:8001/similar_chunks", json={"text": technology_summary})
    augmented_with_info = suggest_additions(technology_summary, augmentation)
    suggestion_answer = generate_tokens(augmented_with_info)
    return TokenResponse(tokens=suggestion_answer)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)