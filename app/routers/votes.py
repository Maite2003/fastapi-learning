
from .. import schema, oauth2
from app import models
from ..database import SessionDep

from fastapi import status, HTTPException, APIRouter, Depends
from sqlalchemy import select


router = APIRouter(prefix="/vote", tags=['Vote'])

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schema.Vote, db: SessionDep, current_user: int = Depends(oauth2.get_current_user)): # type: ignore
    post_query = select(models.Post).where(models.Post.id == vote.post_id)
    post = db.scalar(post_query)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {vote.post_id} does not exists")
    
    vote_query = select(models.Vote).where(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = db.scalar(vote_query)
    if (vote.dir == 1): # Create a vote
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.id} has already voted on post {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()

        return {"message": "Successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exits")
        db.delete(found_vote)
        db.commit()

        return {"message": "Successfully deleted vote"}