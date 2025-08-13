import requests
import json
import os


AUTH_API_URL = 'https://servicos.crea-pr.org.br/services.auth/connect/token'
USERNAME = 'ES-0046904/D'
PASSWORD = 'Becus2023!'
GRANT_TYPE = 'password'
SCOPE = 'creapr.api.services offline_access'
CLIENT_ID = 'dc4dfcf1-6513-4e3f-b3c4-28b2122ef645'
CLIENT_SECRET = 'zrbaNTmS5eBunFWhHjogPf5D33u581mL'
ORIGIN = 'profissional'
TOKENRECAPTCHA = None


TOKEN_FILE = "token.json"
API_TEST_URL = "https://servicos.crea-pr.org.br/services/api/unidademedida/ativos"

def crea_auth():
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "grant_type": GRANT_TYPE,
        "scope": SCOPE,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "origin": ORIGIN,
        "tokenRecaptcha": TOKENRECAPTCHA
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(AUTH_API_URL, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao autenticar: {response.status_code}")
        print(response.text)
        return None
    

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            try:
                return json.load(f).get('access_token')
            except json.JSONDecodeError:
                return None
    return None

def test_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(API_TEST_URL, headers=headers)
    return response.status_code == 200

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f)

def get_valid_token():
    token = load_token()
    if not token or not test_token(token):
        print("Token ausente ou inválido. Autenticando novamente...")
        token = crea_auth()
        if token:
            save_token(token)
            return token.get('access_token')
            
    return token
