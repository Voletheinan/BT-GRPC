import grpc
import sys
import user_pb2
import user_pb2_grpc


def create_user(stub, name, email, role):
    request = user_pb2.CreateUserRequest(name=name, email=email, role=role)
    response = stub.CreateUser(request)
    if response.success:
        print(f"✓ User created: ID={response.user.id}, Name={response.user.name}, Email={response.user.email}, Role={response.user.role}")
    else:
        print(f"✗ Error: {response.message}")
    return response


def get_user(stub, user_id):
    request = user_pb2.GetUserRequest(id=user_id)
    response = stub.GetUser(request)
    if response.success:
        print(f"✓ User found: ID={response.user.id}, Name={response.user.name}, Email={response.user.email}, Role={response.user.role}")
    else:
        print(f"✗ Error: {response.message}")
    return response


def update_user(stub, user_id, name=None, email=None, role=None):
    request = user_pb2.UpdateUserRequest(id=user_id)
    if name:
        request.name = name
    if email:
        request.email = email
    if role:
        request.role = role
    
    response = stub.UpdateUser(request)
    if response.success:
        print(f"✓ User updated: ID={response.user.id}, Name={response.user.name}, Email={response.user.email}, Role={response.user.role}")
    else:
        print(f"✗ Error: {response.message}")
    return response


def delete_user(stub, user_id):
    request = user_pb2.DeleteUserRequest(id=user_id)
    response = stub.DeleteUser(request)
    if response.success:
        print(f"✓ User deleted successfully")
    else:
        print(f"✗ Error: {response.message}")
    return response


def list_users(stub, page=1, page_size=10):
    request = user_pb2.ListUsersRequest(page=page, page_size=page_size)
    response = stub.ListUsers(request)
    print(f"\nUsers (Page {page}, Total: {response.total}):")
    print("-" * 60)
    for user in response.users:
        print(f"ID: {user.id} | Name: {user.name} | Email: {user.email} | Role: {user.role}")
    print("-" * 60)
    return response


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python client.py create <name> <email> <role>")
        print("  python client.py get <id>")
        print("  python client.py update <id> [name] [email] [role]")
        print("  python client.py delete <id>")
        print("  python client.py list [page] [page_size]")
        sys.exit(1)
    
    channel = grpc.insecure_channel('localhost:50055')
    stub = user_pb2_grpc.UserServiceStub(channel)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "create":
            if len(sys.argv) != 5:
                print("Usage: python client.py create <name> <email> <role>")
                sys.exit(1)
            create_user(stub, sys.argv[2], sys.argv[3], sys.argv[4])
        
        elif command == "get":
            if len(sys.argv) != 3:
                print("Usage: python client.py get <id>")
                sys.exit(1)
            get_user(stub, int(sys.argv[2]))
        
        elif command == "update":
            if len(sys.argv) < 3:
                print("Usage: python client.py update <id> [name] [email] [role]")
                sys.exit(1)
            user_id = int(sys.argv[2])
            name = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "None" else None
            email = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "None" else None
            role = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != "None" else None
            update_user(stub, user_id, name, email, role)
        
        elif command == "delete":
            if len(sys.argv) != 3:
                print("Usage: python client.py delete <id>")
                sys.exit(1)
            delete_user(stub, int(sys.argv[2]))
        
        elif command == "list":
            page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            page_size = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            list_users(stub, page, page_size)
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()}")
    finally:
        channel.close()


if __name__ == '__main__':
    main()

