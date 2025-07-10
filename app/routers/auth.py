from fastapi import APIRouter, status, HTTPException, Response, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..database import SessionDep
from .. import schema, models, utils, oauth2

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schema.Token)
def login(db: SessionDep, user_credentials: OAuth2PasswordRequestForm = Depends()): # type: ignore

    """
    OAuth2PasswordRequestForm returns a username and a password.
    The username is the email in our case
    """

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    # 403 when user gives wrong credentials
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    
    # Create token
    acces_token = oauth2.create_access_token(data = {'user_id': user.id})

    # Return token
    return {"access_token": acces_token, "token_type": "Bearer"}

    
