import httpx
import pytest
from fastapi import status

BASE_URL = "http://localhost:8000"  # Update if your app runs on a different URL or port

# Helper function to authenticate and get token
def get_auth_token(client, username, password):
    response = client.post(f"{BASE_URL}/login", data={"username": username, "password": password})
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def client():
    with httpx.Client() as client:
        yield client

@pytest.fixture(scope="module")
def auth_token(client):
    return get_auth_token(client, "testuser", "testpassword")  # Replace with valid credentials

def test_get_current_user(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(f"{BASE_URL}/apis/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()

def test_get_all_users(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(f"{BASE_URL}/apis/all_users", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_patch_current_user(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    user_data = {"fname": "UpdatedName"}
    response = client.patch(f"{BASE_URL}/apis/me", json=user_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["fname"] == "UpdatedName"

def test_delete_current_user(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.delete(f"{BASE_URL}/apis/me", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_user_type(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    userid = 1  # Replace with a valid user ID
    user_type = {"user_type": "hospital"}
    response = client.post(f"{BASE_URL}/apis/me/type/{userid}", json=user_type, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user_type"] == "hospital"
