from fastapi import FastAPI, HTTPException, Depends, status, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from passlib.context import CryptContext
from typing import Optional, Dict
from uuid import uuid4
from need import *

app = FastAPI()

client = MongoClient(MONGODB_URL)
db = client['user_info']
users_collection = db['users']

# In-memory session storage (for demonstration purposes)
sessions = {}

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class User(BaseModel):
    id: str
    nickname: str
    password: str
    age: int
    gender: str
    party: Optional[Dict] = None
    community: str

class UserInDB(User):
    hashed_password: str

# Utility functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(user: User):
    id = user.id
    if users_collection.find_one({"id": id}):
        return None
    else:
        hashed_password = get_password_hash(user.password)
        return UserInDB(id=user.id, nickname=user.nickname, password=user.password, age=user.age, gender=user.gender, party=user.party, community=user.community, hashed_password=hashed_password)

# Endpoints
@app.post("/signup", response_model=dict)
async def sign_up(user: User):
    # Check if user already exists (replace with actual database check)
    existing_user = await get_user(user)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Save user to database
    user_data = user.dict()
    print(hashed_password)
    user_data.update({"hashed_password": hashed_password})
    del user_data['password']  # Remove plain password before saving
    
    # Insert user into MongoDB
    result = users_collection.insert_one(user_data)
    print(f"User registered: {user.id}, {user.nickname}, {hashed_password}, {user.age}, {user.gender}")
    
    return {"msg": "User created successfully"}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create session ID
    session_id = str(uuid4())
    
    # Store session ID in memory (replace with actual session storage)
    sessions[session_id] = user.id
    
    return {"msg": "Logged in successfully", "session_id": session_id}

@app.get("/users/me", response_model=User)
async def read_users_me(session_id: str = Cookie(None), current_user: User = Depends()):
    # Check if session ID exists in memory (replace with actual session check)
    if session_id not in sessions or sessions[session_id] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or expired",
        )
    
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
