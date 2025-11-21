from fastapi import APIRouter,Request,Depends,HTTPException,Response
from database.schemas import UserDataCreate
from fastapi.responses import JSONResponse
from database.database import get_db
from database.crud import create_user_data_entry
from api_utils.auth_utils import decode_token,create_access_token
from database.models import UserData
from pydantic import BaseModel
from api_utils.auth_utils import hash_password , verify_password


class LoginData(BaseModel):
    email:str
    password:str

auth_router = APIRouter()

@auth_router.post('/signup')
async def register(request:Request,data:UserDataCreate,db=Depends(get_db))->JSONResponse:
    try:
        existing = db.query(UserData).filter(UserData.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400,detail="user already exists.")
        data.password = hash_password(data.password)
        user = create_user_data_entry(db,data)
        return JSONResponse(content={"message":f"User created successfully.","ref_id":user.id})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to register user. {e}")
    
@auth_router.post('/login')
async def login(request:Request,response:Response,data:LoginData,db=Depends(get_db))->Response:
    try:
        user = db.query(UserData).filter(UserData.email == data.email).first()
        if not user:
            raise HTTPException(status_code=404,detail="User not found.")
        
        if verify_password(data.password,user.password):
            token = create_access_token({'email':user.email,'role':user.role,"name":user.name})
            response = JSONResponse(content={
                'email':user.email,
                'role':user.role,
                'name':user.name,
            })
            response.set_cookie(
                key="auth_token",
                value=token,
                httponly=False,
                secure=False,
                samesite='lax',
                max_age=3600*3,
                path='/'
            )
            return response
        raise HTTPException(status_code=400,detail="Wrong email or password.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Login Failed. {e}")
    
@auth_router.get('/logout')
async def logout(request:Request,response:Response,user=Depends(decode_token))->JSONResponse:
    try:
        response = JSONResponse(content={"message": "Logged out successfully"})
        response.delete_cookie(
            key="auth_token",
            httponly=False,
            secure=False, 
            samesite='lax',
            path="/"
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to logout. {e}")

