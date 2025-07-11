import pytest
from app import models, schema

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get('/posts/')

    posts = [schema.PostOut(**post) for post in res.json()]

    assert res.status_code == 200
    assert len(posts) == len(test_posts)

def test_get_all_posts_unauthorized(client, test_posts):
    res = client.get('/posts/')

    assert res.status_code == 401

def test_get_one_posts_unauthorized(client, test_posts):
    res = client.get(f'/posts/{test_posts[0].id}')

    assert res.status_code == 401

def test_get_one_post_invalid(authorized_client, test_posts):
    res = authorized_client.get('posts/9865195')

    assert res.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f'/posts/{test_posts[0].id}')

    post = schema.PostOut(**res.json())

    assert res.status_code == 200
    assert post.post.id == test_posts[0].id
    assert post.post.title == test_posts[0].title
    assert post.post.content == test_posts[0].content

@pytest.mark.parametrize("title, content, published", [
    ("title1", "content1", True),
    ("title2", "content2", False)
])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    post_info = {
        "title": title,
        "content": content,
        "published": published
    }
    res = authorized_client.post('/posts', json=post_info)

    post = schema.Post(**res.json())

    assert res.status_code == 201
    assert post.title == title
    assert post.content == content
    assert post.published == published
    assert post.owner_id == test_user[0]['id']

def test_create_post_default_pubished(authorized_client, test_user, test_posts):
    post_info = {
        "title": 'title1',
        "content": 'content1'
    }
    res = authorized_client.post('/posts', json=post_info)

    post = schema.Post(**res.json())

    assert res.status_code == 201
    assert post.published == True


def test_create_post_unauthorized(client, test_user, test_posts):
    post_info = {
        "title": 'title1',
        "content": 'content'
    }
    res = client.post('/posts', json=post_info)

    assert res.status_code == 401

def test_delete_post_unauthorized(client, test_user, test_posts):
    res = client.delete(f'/posts/{test_posts[0].id}')

    assert res.status_code == 401

def test_delete_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f'/posts/{test_posts[0].id}')

    assert res.status_code == 204

def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete('/posts/654123555')

    assert res.status_code == 404

def test_delete_other_user_post(client, test_user, test_posts):
    """
    Right now all posts are from user1, we'll login with user2
    and try to delete any post
    """

    login_res = client.post('/login', data={"username": test_user[1]['email'], "password":test_user[1]['password']})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {login_res.json().get('access_token')}"
    }
    
    res = client.delete(f'/posts/{test_posts[0].id}')
    
    assert res.status_code == 403

def test_update_post(authorized_client, test_user, test_posts):
    new_data = {
        'id':test_posts[0].id,
        'title': 'new_title', 
        'content': test_posts[0].content, 
        'published': test_posts[0].published
        }
    res = authorized_client.put(f'/posts/{test_posts[0].id}', json=new_data)

    updated_post = schema.Post(**res.json())

    assert res.status_code == 200
    assert updated_post.title == new_data['title']
    assert updated_post.content == new_data['content']
    assert updated_post.published == new_data['published']

def test_update_other_user_post(client, test_user, test_posts):
    """
    Right now all posts are from user1, we'll login with user2
    and try to update any post
    """

    login_res = client.post('/login', data={"username": test_user[1]['email'], "password":test_user[1]['password']})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {login_res.json().get('access_token')}"
    }
    
    new_data = {
        'id':test_posts[0].id,
        'title': 'new_title', 
        'content': test_posts[0].content, 
        'published': test_posts[0].published
        }
    res = client.put(f'/posts/{test_posts[0].id}', json=new_data)

    
    assert res.status_code == 403


def test_update_post_unauthorized(client, test_user, test_posts):
    new_data = {
        'id':test_posts[0].id,
        'title': 'new_title', 
        'content': test_posts[0].content, 
        'published': test_posts[0].published
        }
    res = client.put(f'/posts/{test_posts[0].id}', json=new_data)

    
    assert res.status_code == 401

def test_update_post_non_exist(authorized_client, test_user, test_posts):
    new_data = {
        'id':8545346515,
        'title': 'new_title', 
        'content': 'content', 
        'published': True
        }
    res = authorized_client.put(f'/posts/{new_data['id']}', json=new_data)

    assert res.status_code == 404