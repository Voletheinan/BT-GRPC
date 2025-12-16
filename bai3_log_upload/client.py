import grpc
import sys
import time
import log_pb2
import log_pb2_grpc


def run():
    if len(sys.argv) < 2:
        print("Usage: python client.py <log_file.txt>")
        sys.exit(1)
    
    log_file = sys.argv[1]
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{log_file}' not found")
        sys.exit(1)
    
    channel = grpc.insecure_channel('localhost:50053')
    stub = log_pb2_grpc.LogServiceStub(channel)
    
    def generate_log_requests():
        start_time = time.time_ns()
        for line in lines:
            request = log_pb2.LogRequest(
                line=line.strip(),
                timestamp=time.time_ns()
            )
            yield request
    
    print(f"Uploading {len(lines)} lines from {log_file}...\n")
    
    try:
        response = stub.UploadLog(generate_log_requests())
        print("\n" + "="*50)
        print("Upload Summary:")
        print(f"Total lines received: {response.total_lines}")
        print(f"Total size: {response.total_size} bytes ({response.total_size/1024:.2f} KB)")
        print(f"Duration: {response.duration_seconds:.2f} seconds")
        print("="*50)
    except grpc.RpcError as e:
        print(f"Error: {e.code()}")
    
    channel.close()


if __name__ == '__main__':
    run()

