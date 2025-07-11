import jwt
import pytest
from app import schema
from app.config import get_settings

def test_create_user(client):
    email = "maite101@gmail.com"
    password = "password123"
    user_info = {"email": email,
                 "password": password}
    response = client.post('/users/', json=user_info)

    assert response.status_code == 201
    new_user = schema.UserOut(**response.json())
    assert new_user.email == email

def test_login_user(client, test_user):
    # Try to log in
    res = client.post('/login', data={"username": test_user[0]['email'],
                 "password": test_user[0]['password']})

    login_res = schema.Token(**res.json())
    settings = get_settings()
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id: str = payload.get("user_id")
    
    assert id == test_user[0]['id']
    assert login_res.token_type == "Bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [
    ('wrong_email@gmail.com', 'password', 403),
    ('test@gmail.com', 'wrongpass', 403),
    ('wrongemail@gmail.com', 'wrongpass', 403),
    (None, 'password', 403),
    ('test@gmail.com', None, 403)
])
def test_incorrect_login_user(client, email, password, status_code):
    # Try to log in
    res = client.post('/login', data={"username": email,
                 "password": password})

    assert res.status_code == status_code
    assert res.json().get('detail') == "Invalid credentials"

"""
def test_get_all_users(client):
    response = client.get('/')
    
    assert response.status_code == 200
    assert response.json() == {"message": "welcome to my api"}
"""

def test_get_one_user(client, test_user):
    res = client.get(f'/users/{test_user[0]['id']}')
    
    user_out = schema.UserOut(**res.json())

    assert res.status_code == 200
    assert user_out.email == test_user[0]['email']
    assert user_out.id == test_user[0]['id']

def test_incorrect_get_one_user(client, test_user):
    res = client.get(f'/users/155')
    
    assert res.status_code == 404

    


