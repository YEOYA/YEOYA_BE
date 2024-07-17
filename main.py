from fastapi import FastAPI, HTTPException, Depends, status, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from passlib.context import CryptContext
from typing import Optional, Dict
from uuid import uuid4
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET
from bson import ObjectId
from need import *
from crawling import get_news
import httpx
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],   # 모든 HTTP 메서드 허용
    allow_headers=["*"],   # 모든 헤더 허용
)

openapi_url = "https://open.assembly.go.kr/portal/openapi/nwvrqwxyaytdsfvhu?"
api_key = OPENAPI_KEY

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
    pwcheck: str
    age: int
    gender: str
    party: dict = {"name": "없음", "color": ""}
    community: str = "없음"
    following: list = []


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
        return UserInDB(id=user.id, nickname=user.nickname, password=user.password, pwcheck=user.pwcheck, age=user.age, gender=user.gender, party=user.party, community=user.community, hashed_password=hashed_password)

class UserInDB(User):
    hashed_password: str

# Endpoints
@app.post("/signup")
async def sign_up(user: User):
    # Check if user already exists (replace with actual database check)
    existing_user = await get_user(user)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
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
    user = users_collection.find_one({"id": form_data.username})
    # if not user or not verify_password(form_data.password, user.hashed_password):
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Incorrect email or password",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
    
    # Create session ID
    # session_id = str(uuid4())
    
    # Store session ID in memory (replace with actual session storage)
    # sessions[session_id] = user.id
    
    # return {"msg": "Logged in successfully", "session_id": session_id, "userId": user.id}
    if user['id'] == form_data.username:
        return {"userID": user['id']}
    else:
        raise HTTPException(status_code=404, detail={"user not found"})
    
    
@dataclass
class Politition:
    name: str # 이름
    poly_name: str # 정당명
    birth: str # 생년월일
    sex: str # 성별
    job_res: str # 직책명
    orig: str # 선거구
    units: str # 당선
    mem_title: str # 약력

def convert_to_politician(data):
    politicians = []
    for item in data:
        politician = Politition(
            name=item.get("HG_NM", ""),
            poly_name=item.get("POLY_NM", ""),
            birth=item.get("BTH_DATE", ""),
            sex=item.get("SEX_GBN_NM", ""),
            job_res=item.get("JOB_RES_NM", ""),
            orig=item.get("ORIG_NM", ""),
            units=item.get("UNITS", ""),
            mem_title=item.get("MEM_TITLE", ""),
        )
        politicians.append(politician)
    return politicians

@dataclass
class ListResponse:
    data: list

def convert_to_list_response(dat):
    return ListResponse(data=dat)

@app.get("/search_members/")
async def search_members(name: str):
    try:
        params = {
            "KEY": api_key,
            "Type": "json",
            "pIndex": 1,
            "HG_NM": name,
            "pSize": 5
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(openapi_url, params=params)

        if response.status_code == 200:
            data = json.loads(response.text)['nwvrqwxyaytdsfvhu']
            list_count = data[0]['head'][0]['list_total_count'] # 검색 의원 갯수
            politition = data[1]['row']

            results = convert_to_politician(politition)

            response_dict = asdict(convert_to_list_response(results))
            json_string = json.dumps(response_dict, indent=2, ensure_ascii=False)

            activity = get_news.find_news(name)


            return {"data": json_string, "activities": activity}
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")
    except:
        try:
            activity = get_news.find_news(name)
            print(activity)
            return {"data": "", "activities": activity}
        except:
            return {"data": '', "activities": ""}

@app.get("/user/{id}") # db user 정보 가져오기
async def getUserById(id: str):
    user_data = users_collection.find_one({"id": id})
    
    if user_data:
        return {"nickname": user_data["nickname"], "age": user_data["age"], "gender": user_data["gender"], "party": user_data["party"], "community": user_data["community"], "folling": user_data["folling"]}
    else:
        raise HTTPException(status_code=404, detail={"message": "user not found"})

@app.post("/plus-follower")
async def following_increase(id: str, name: str, poly_name: str):
    user = users_collection.find_one({'id': id})
    user.following.append({'name': 'poly_name'})

    return {"message": "appended successfully"}

# Pydantic models
class User(BaseModel):
    id: str
    nickname: str
    password: str
    age: int
    gender: str
    party: Optional[dict] = None
    community: str
    folling: list = []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5632, reload=True)