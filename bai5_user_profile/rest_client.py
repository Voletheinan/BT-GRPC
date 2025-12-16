"""
REST API Client cho User Service
Sử dụng FastAPI để tạo REST API gateway cho gRPC service
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import grpc
import user_pb2
import user_pb2_grpc

app = FastAPI(title="User Profile REST API")

# gRPC connection
channel = grpc.insecure_channel('localhost:50055')
stub = user_pb2_grpc.UserServiceStub(channel)


class UserCreate(BaseModel):
    name: str
    email: str
    role: str


class UserUpdate(BaseModel):
    name: str = None
    email: str = None
    role: str = None


@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    request = user_pb2.CreateUserRequest(
        name=user.name,
        email=user.email,
        role=user.role
    )
    response = stub.CreateUser(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return {
        "id": response.user.id,
        "name": response.user.name,
        "email": response.user.email,
        "role": response.user.role
    }


@app.get("/users/{user_id}")
def get_user(user_id: int):
    request = user_pb2.GetUserRequest(id=user_id)
    response = stub.GetUser(request)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.message)
    return {
        "id": response.user.id,
        "name": response.user.name,
        "email": response.user.email,
        "role": response.user.role
    }


@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    request = user_pb2.UpdateUserRequest(id=user_id)
    if user.name:
        request.name = user.name
    if user.email:
        request.email = user.email
    if user.role:
        request.role = user.role
    
    response = stub.UpdateUser(request)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return {
        "id": response.user.id,
        "name": response.user.name,
        "email": response.user.email,
        "role": response.user.role
    }


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    request = user_pb2.DeleteUserRequest(id=user_id)
    response = stub.DeleteUser(request)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.message)
    return {"message": "User deleted successfully"}


@app.get("/users")
def list_users(page: int = 1, page_size: int = 10):
    request = user_pb2.ListUsersRequest(page=page, page_size=page_size)
    response = stub.ListUsers(request)
    return {
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
            for user in response.users
        ],
        "total": response.total,
        "page": page,
        "page_size": page_size
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

