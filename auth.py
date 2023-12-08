from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import json
from pydantic import BaseModel
from passlib.hash import bcrypt
from typing import Annotated
import jwt
from typing import Union
from passlib.context import CryptContext
import requests

oauth2_router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
	id : int
	username : str
	admin : bool
	hashPass : str
	
class UserAccountInput(BaseModel):
    username: str
    password : str
    admin : bool

class UserAccountInputOutside(BaseModel):
    username: str
    password : str

json_filename="user.JSON"
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hash(password):
     return pwd_context.hash(password)

def verify_hash_and_password(password, hashpass):
     return pwd_context.verify(password, hashpass)


with open(json_filename,"r") as read_file:
	userdata = json.load(read_file)

@oauth2_router.post("/users")
async def add_user(user :UserAccountInput):
    username_found = False
    user_id = 0

    for item in userdata:
        if user_id <= item['id']:
              user_id = item['id'] + 1
        if user.username == item['username']:
            username_found = True
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken."
            )
    if not(username_found) :
        pass_hash = get_hash(user.password)
        insert_user = {"id" : user_id, "username" : user.username, "admin" : user.admin, "hashPass" : pass_hash}
        userdata.append(insert_user)
        with open(json_filename,"w") as write_file:
            json.dump(userdata, write_file)

    return "success"

def get_user_from_input(username:str, password:str):
    userfound = False
    for item in userdata:
          if username == item["username"]:
                if verify_hash_and_password(password, item["hashPass"]):
                    return item
                else: #Wrong Password
                     return False
    return False
                    
def add_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    data_to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_encode.update({"exp": expire})
    encodedJWT = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encodedJWT
     


@oauth2_router.post("/token", response_model=Token)
async def create_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user_from_input(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expiring = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = add_access_token(
    data={"sub": user["username"], "id" : user["id"]}, expires_delta=access_token_expiring
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token : Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        token_decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = token_decoded.get("sub")
        if username is None:
            raise credentials_exception

    except jwt.JWTError:
        raise credentials_exception

    for item in userdata:
        if item['username'] == username:
            return item
    raise credentials_exception

@oauth2_router.post("/token", response_model=Token)
async def create_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user_from_input(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expiring = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = add_access_token(
    data={"sub": user["username"], "id" : user["id"]}, expires_delta=access_token_expiring
    )
    return {"access_token": access_token, "token_type": "bearer"}


