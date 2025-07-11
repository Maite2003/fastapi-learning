from sqlalchemy import select
from ..main import app
from app.database import get_session, Base
from app import models, schema
import pytest
from fastapi.testclient import TestClient

from .database import TestingSessionLocal, engine
from app.oauth2 import create_access_token

"""
All files in the same package have access to the fixtures here
without having to import
"""

@pytest.fixture
def session():
    # Clearing out database for next test
    Base.metadata.drop_all(bind=engine)
    # Creating tables
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def client(session): # session it's initialized
    def override_get_session():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)

@pytest.fixture
def test_user(client):
    users_info = [
        {"email": "test@gmail.com", 
         "password": "password"},
        {"email": "test2@gmail.com", 
         "password": "password"}
    ]
    
    res1 = client.post('/users/', json=users_info[0])
    res2 = client.post('/users/', json=users_info[1])

    client1 = schema.UserOut(**res1.json())
    client2 = schema.UserOut(**res2.json())

    users_info[0]['id'] = client1.id
    users_info[0]['created_at'] = client1.created_at
    users_info[1]['id'] = client2.id
    users_info[1]['created_at'] = client2.created_at
        
    return users_info

@pytest.fixture
def token(test_user):
    token = create_access_token(data={'user_id': test_user[0]['id']})
    return token

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client

@pytest.fixture
def test_posts(test_user, session):
    posts_data = [
        {'title':'title1',
         'content':'content1',
         'owner_id': test_user[0]['id']},
         {'title':'title2',
         'content':'content2',
         'owner_id':test_user[0]['id']},
         {'title':'title3',
         'content':'content3',
         'owner_id':test_user[0]['id']}
    ]
    
    session.add_all([models.Post(**post) for post in posts_data])
    session.commit()

    return session.scalars(select(models.Post)).all()