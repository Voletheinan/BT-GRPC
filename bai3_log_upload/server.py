import grpc
from concurrent import futures
import time
import log_pb2
import log_pb2_grpc


class LogServiceServicer(log_pb2_grpc.LogServiceServicer):
    def UploadLog(self, request_iterator, context):
        total_lines = 0
        total_size = 0
        start_time = None
        end_time = None
        
        print("Receiving log stream...")
        
        for log_request in request_iterator:
            if start_time is None:
                start_time = log_request.timestamp
            
            total_lines += 1
            total_size += len(log_request.line.encode('utf-8'))
            end_time = log_request.timestamp
            
            print(f"Received line {total_lines}: {log_request.line[:50]}...")
        
        duration = (end_time - start_time) / 1e9 if start_time else 0.0
        
        print(f"\nUpload complete!")
        print(f"Total lines: {total_lines}")
        print(f"Total size: {total_size} bytes")
        
        return log_pb2.LogResponse(
            total_lines=total_lines,
            total_size=total_size,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    log_pb2_grpc.add_LogServiceServicer_to_server(
        LogServiceServicer(), server
    )
    server.add_insecure_port('[::]:50053')
    server.start()
    print("Log Server started on port 50053")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

