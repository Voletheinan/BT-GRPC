import grpc
from concurrent import futures
from sqlalchemy.orm import Session
import user_pb2
import user_pb2_grpc
from database import SessionLocal, User, init_db


class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        db = SessionLocal()
        try:
            # Kiểm tra email đã tồn tại chưa
            existing_user = db.query(User).filter(User.email == request.email).first()
            if existing_user:
                return user_pb2.UserResponse(
                    success=False,
                    message=f"User with email {request.email} already exists"
                )
            
            user = User(
                name=request.name,
                email=request.email,
                role=request.role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return user_pb2.UserResponse(
                success=True,
                message="User created successfully",
                user=user_pb2.User(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    role=user.role
                )
            )
        except Exception as e:
            db.rollback()
            return user_pb2.UserResponse(
                success=False,
                message=f"Error creating user: {str(e)}"
            )
        finally:
            db.close()
    
    def GetUser(self, request, context):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == request.id).first()
            if not user:
                return user_pb2.UserResponse(
                    success=False,
                    message=f"User with id {request.id} not found"
                )
            
            return user_pb2.UserResponse(
                success=True,
                message="User retrieved successfully",
                user=user_pb2.User(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    role=user.role
                )
            )
        except Exception as e:
            return user_pb2.UserResponse(
                success=False,
                message=f"Error retrieving user: {str(e)}"
            )
        finally:
            db.close()
    
    def UpdateUser(self, request, context):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == request.id).first()
            if not user:
                return user_pb2.UserResponse(
                    success=False,
                    message=f"User with id {request.id} not found"
                )
            
            # Kiểm tra email mới có trùng không
            if request.email and request.email != user.email:
                existing_user = db.query(User).filter(User.email == request.email).first()
                if existing_user:
                    return user_pb2.UserResponse(
                        success=False,
                        message=f"Email {request.email} already exists"
                    )
            
            if request.name:
                user.name = request.name
            if request.email:
                user.email = request.email
            if request.role:
                user.role = request.role
            
            db.commit()
            db.refresh(user)
            
            return user_pb2.UserResponse(
                success=True,
                message="User updated successfully",
                user=user_pb2.User(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    role=user.role
                )
            )
        except Exception as e:
            db.rollback()
            return user_pb2.UserResponse(
                success=False,
                message=f"Error updating user: {str(e)}"
            )
        finally:
            db.close()
    
    def DeleteUser(self, request, context):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == request.id).first()
            if not user:
                return user_pb2.DeleteUserResponse(
                    success=False,
                    message=f"User with id {request.id} not found"
                )
            
            db.delete(user)
            db.commit()
            
            return user_pb2.DeleteUserResponse(
                success=True,
                message="User deleted successfully"
            )
        except Exception as e:
            db.rollback()
            return user_pb2.DeleteUserResponse(
                success=False,
                message=f"Error deleting user: {str(e)}"
            )
        finally:
            db.close()
    
    def ListUsers(self, request, context):
        db = SessionLocal()
        try:
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 10
            
            offset = (page - 1) * page_size
            users = db.query(User).offset(offset).limit(page_size).all()
            total = db.query(User).count()
            
            user_list = [
                user_pb2.User(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    role=user.role
                )
                for user in users
            ]
            
            return user_pb2.ListUsersResponse(
                users=user_list,
                total=total
            )
        except Exception as e:
            return user_pb2.ListUsersResponse(users=[], total=0)
        finally:
            db.close()


def serve():
    init_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserServiceServicer(), server
    )
    server.add_insecure_port('[::]:50055')
    server.start()
    print("User Service Server started on port 50055")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

