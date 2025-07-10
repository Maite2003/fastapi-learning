
from .. import schema, oauth2
from app import models
from ..database import SessionDep

from sqlalchemy import func, select
from typing import List
from fastapi import Response, status, HTTPException, APIRouter, Depends

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

"""
@{name of the app}.{method the user has to use}("{path of the url}")
"""

@router.get("/", response_model=List[schema.PostOut])
def get_posts(db: SessionDep, current_user: models.User = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: str = ""): # type: ignore
    my_posts_query = select(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).where(
            models.Post.title.contains(search)).group_by(models.Post.id).offset(skip).limit(limit)

    result = db.execute(my_posts_query).all() # Returns a list of tuples with tuples = (post, number of votes)
    return [{"post": post, "votes": votes} for post, votes in result]

@router.get("/{id}", response_model=schema.PostOut) # ID it is always going to be a string
def get_post(id : int, db: SessionDep, current_user: models.User = Depends(oauth2.get_current_user)): # type: ignore
    """
    id : int makes sure that the id passed to the path can be converted to a string 
    and it alsos converts it to a string
    """
    my_post_query = select(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).where(models.Post.id == id).group_by(models.Post.id)
    post = db.execute(my_post_query).first()

    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with {id} was not found")
    # If no error, send the post
    print(post)
    return {"post": post[0], "votes": post[1]}

"""
The ORDER of the request here matters, because if we want to do
@app.get("/posts/latest") here
is always going to be an error because it is trying to 
match it to @app.get("/posts/{id}")
"""



# PUT pass all the fields
# PATCH only pass the field that changed

"""
the status_code indicates what status code is sent with the return statement
putting get_current user as a dependency forces the user to authenticate
"""
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Post) # 201 used for creating things
def create_posts(post: schema.PostCreate, db: SessionDep, current_user: models.User = Depends(oauth2.get_current_user)): # type: ignore

    new_post = models.Post(**post.model_dump(), owner_id = current_user.id)
    # model_dump() gives a dictionary, the ** makes it so it has the format
    # that it needs to be parameters
    db.add(new_post)
    db.commit()
    db.refresh(new_post) # retrieve new post created and store it new_post
    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT) # 204 used for delete
def delete_post(id: int, db: SessionDep, current_user: models.User = Depends(oauth2.get_current_user)): # type: ignore
    
    post_query = select(models.Post).where(models.Post.id == id)
    post = db.scalar(post_query)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perfomed requested action")

    db.delete(post)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT) 
"""
204 status is no content so we should be sending information. if we do there
is going to be an error. what we do is send the status 204
"""



@router.put("/{id}", response_model=schema.Post)
def update_post(id : int, post: schema.PostCreate, db: SessionDep, current_user: models.User = Depends(oauth2.get_current_user)): # type: ignore
    
    post_query = select(models.Post).where(models.Post.id == id)
    old_post = db.scalar(post_query)

    if not old_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
    
    if old_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perfome requested action")

    old_post.title = post.title
    old_post.content = post.content
    old_post.published = post.published

    db.commit()

    return post_query.first()

