import grpc
import sys
import hello_pb2
import hello_pb2_grpc


def run():
    if len(sys.argv) < 2:
        print("Usage: python client.py <name>")
        sys.exit(1)
    
    name = sys.argv[1]
    
    channel = grpc.insecure_channel('localhost:50051')
    stub = hello_pb2_grpc.GreeterStub(channel)
    
    request = hello_pb2.HelloRequest(name=name)
    response = stub.SayHello(request)
    
    print(response.message)
    
    channel.close()


if __name__ == '__main__':
    run()

