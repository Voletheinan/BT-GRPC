"""
REST API Gateway
Client chỉ gọi REST API, REST API gọi nội bộ gRPC service
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import grpc
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import user_pb2
import user_pb2_grpc

app = FastAPI(
    title="REST API Gateway",
    description="REST API Gateway that communicates with gRPC User Service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# gRPC connection
GRPC_SERVER = os.getenv("GRPC_SERVER", "localhost:50056")
channel = grpc.insecure_channel(GRPC_SERVER)
stub = user_pb2_grpc.UserServiceStub(channel)


class UserCreate(BaseModel):
    name: str
    email: str
    role: str


class UserUpdate(BaseModel):
    name: str = None
    email: str = None
    role: str = None


@app.get("/")
def root():
    return {
        "message": "REST API Gateway for gRPC User Service",
        "endpoints": {
            "POST /api/users": "Create a new user",
            "GET /api/users/{id}": "Get user by ID",
            "PUT /api/users/{id}": "Update user",
            "DELETE /api/users/{id}": "Delete user",
            "GET /api/users": "List all users with pagination"
        }
    }


@app.post("/api/users", status_code=201)
def create_user(user: UserCreate):
    """Create a new user via gRPC"""
    try:
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
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    """Get user by ID via gRPC"""
    try:
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
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.put("/api/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    """Update user via gRPC"""
    try:
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
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    """Delete user via gRPC"""
    try:
        request = user_pb2.DeleteUserRequest(id=user_id)
        response = stub.DeleteUser(request)
        if not response.success:
            raise HTTPException(status_code=404, detail=response.message)
        return {"message": "User deleted successfully"}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.get("/api/users")
def list_users(page: int = 1, page_size: int = 10):
    """List users with pagination via gRPC"""
    try:
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
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test gRPC connection
        request = user_pb2.ListUsersRequest(page=1, page_size=1)
        stub.ListUsers(request)
        return {"status": "healthy", "grpc_service": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

