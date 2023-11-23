import requests
import os 
from dotenv import load_dotenv

load_dotenv()

KEYCLOAK_URL = os.getenv("KEYCLOAK_SERVER_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM_NAME")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
KEYCLOAK_ADMIN = os.getenv("KEYCLOAK_ADMIN_USERNAME")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD")




def get_user_token(username, password):
    data = {
        'grant_type': 'password',
        'client_id': KEYCLOAK_CLIENT_ID,
        'client_secret': KEYCLOAK_CLIENT_SECRET,
        'username': username,
        'password': password,
    }
    try:
        response = requests.post(f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token", data=data)
        return response.json()
    except Exception as e:
        return {"message": str(e)}        

def create_user(user):
    admin_token = get_user_token(KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD)
    headers = {
        'Authorization': f'Bearer {admin_token["access_token"]}',
        'Content-Type': 'application/json',
    }
    try:
        response = requests.post(f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users", headers=headers, json=user)
    except Exception as e:
        return {"message": str(e)}
    return response.status_code
