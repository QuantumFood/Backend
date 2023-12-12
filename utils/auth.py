from fastapi import HTTPException
from jose import jwt,JWTError
from dotenv import load_dotenv
import requests
import os
from datetime import datetime, timedelta


load_dotenv()

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
KEYCLOAK_ADMIN = os.getenv("KEYCLOAK_ADMIN")
KEYCLOAK_ADMIN_EMAIL = os.getenv("EYCLOAK_ADMIN_EMAIL")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
ALGORITHM = os.getenv("ALGORITHM")
AUDIENCE = os.getenv("AUDIENCE")
DECODE_KEY = os.getenv("DECODE_KEY")


def get_user_token(email, password):
    data = {
        'grant_type': 'password',
        'client_id': KEYCLOAK_CLIENT_ID,
        'client_secret': KEYCLOAK_CLIENT_SECRET,
        'username': email,
        'password': password,
    }
    response = requests.post(
        f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token", data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return response.json()
   

admin_token = get_user_token(KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD)
expire_date = datetime.now() + timedelta(seconds=admin_token.get('expires_in'))

def refresh_admin_token(token):
    if datetime.now() > expire_date:
        response = get_user_token(KEYCLOAK_ADMIN, KEYCLOAK_ADMIN_PASSWORD)
        return response
    return token
    
        

DECODE_KEY= "-----BEGIN PUBLIC KEY-----\n" + PUBLIC_KEY + "\n-----END PUBLIC KEY-----"
def verify_token(token):
    try:
        payload = jwt.decode(token, key=DECODE_KEY, audience=AUDIENCE, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))


def get_user_id(username):
    admin_access_token = refresh_admin_token(admin_token).get('access_token')
    headers = {
        'Authorization': f'Bearer {admin_access_token}',
    }
    params = {
        'username': username,
    }
    response = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users", headers=headers, params=params)
    user_data = response.json()
    if user_data:
        return user_data[0]['id']
    else:
        return None



def create_user(user):
    admin_access_token = refresh_admin_token(admin_token).get('access_token')
    headers = {
        'Authorization': f'Bearer {admin_access_token}',
        'Content-Type': 'application/json',
    }
    try:
        response = requests.post(
            f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users", headers=headers, json=user)
    except Exception as e:
        return {"message": str(e)}
    return response.status_code


def username_exists_in_keycloak(username):
    admin_access_token = refresh_admin_token(admin_token).get('access_token')
    headers = {
        'Authorization': f'Bearer {admin_access_token}',
    }
    params = {
        'username': username,
    }
    response = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users", headers=headers, params=params)
    return len(response.json()) > 0

def email_exists_in_keycloak(email):
    admin_access_token = refresh_admin_token(admin_token).get('access_token')
    headers = {
        'Authorization': f'Bearer {admin_access_token}',
    }
    params = {
        'email': email,
    }
    response = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users", headers=headers, params=params)
    return len(response.json()) > 0

def user_exists_in_keycloak(username, email):
    return username_exists_in_keycloak(username) or email_exists_in_keycloak(email)

def is_user_logged_in(username):
    user_id = get_user_id(username)
    if user_id is None:
        return False
    admin_access_token = refresh_admin_token(admin_token).get('access_token')
    headers = {
        'Authorization': f'Bearer {admin_access_token}',
    }
    response = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}/sessions", headers=headers)
    return len(response.json()) > 0


def logout_user(username):
    user_id = get_user_id(username)
    admin_access_token = refresh_admin_token(admin_token).get('access_token')
    headers = {
        'Authorization': f'Bearer {admin_access_token}',
    }
    response =  requests.post(
        f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}/logout", headers=headers)
    if response.status_code != 204:
        raise HTTPException(status_code=500, detail="Error logging out user")
    return {"detail": "User logged out successfully"}
    


def delete_keycloak_user(username):
    user_id = get_user_id(username)
    admin_access_token = refresh_admin_token(admin_token).get('access_token')
    headers = {
        'Authorization': f'Bearer {admin_access_token}',
    }
    try:
        response = requests.delete(
            f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}", headers=headers)
        if response.status_code != 204:
                raise HTTPException(status_code=500, detail="Error deleting user")
    except Exception as e:
        return {"message": str(e)}