import grpc
from concurrent import futures
import threading
import time
import chat_pb2
import chat_pb2_grpc


class ChatServiceServicer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.clients = {}  # client_id -> queue of messages
        self.lock = threading.Lock()
    
    def Chat(self, request_iterator, context):
        client_id = None
        
        try:
            # Nhận message đầu tiên để lấy client_id
            for request in request_iterator:
                if client_id is None:
                    client_id = request.client_id
                    with self.lock:
                        self.clients[client_id] = []
                    print(f"Client {client_id} joined the chat")
                    
                    # Broadcast join message
                    join_msg = chat_pb2.ChatMessage(
                        client_id="SERVER",
                        message=f"{client_id} joined the chat",
                        timestamp=int(time.time() * 1000),
                        type=chat_pb2.MessageType.JOIN
                    )
                    self._broadcast(join_msg, exclude_client=client_id)
                
                # Xử lý message từ client
                if request.type == chat_pb2.MessageType.PRIVATE:
                    # Private message
                    if request.target_client_id in self.clients:
                        self._send_private(request, request.target_client_id)
                    else:
                        error_msg = chat_pb2.ChatMessage(
                            client_id="SERVER",
                            message=f"User {request.target_client_id} not found",
                            timestamp=int(time.time() * 1000),
                            type=chat_pb2.MessageType.BROADCAST
                        )
                        self._send_private(error_msg, client_id)
                else:
                    # Broadcast message
                    self._broadcast(request, exclude_client=client_id)
                
                # Gửi messages từ queue đến client này
                with self.lock:
                    if client_id in self.clients:
                        for msg in self.clients[client_id]:
                            yield msg
                        self.clients[client_id] = []
                
        except Exception as e:
            print(f"Error in chat stream: {e}")
        finally:
            if client_id:
                with self.lock:
                    if client_id in self.clients:
                        del self.clients[client_id]
                
                leave_msg = chat_pb2.ChatMessage(
                    client_id="SERVER",
                    message=f"{client_id} left the chat",
                    timestamp=int(time.time() * 1000),
                    type=chat_pb2.MessageType.LEAVE
                )
                self._broadcast(leave_msg, exclude_client=client_id)
                print(f"Client {client_id} left the chat")
    
    def _broadcast(self, message, exclude_client=None):
        with self.lock:
            for cid, queue in self.clients.items():
                if cid != exclude_client:
                    queue.append(message)
    
    def _send_private(self, message, target_client_id):
        with self.lock:
            if target_client_id in self.clients:
                self.clients[target_client_id].append(message)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(
        ChatServiceServicer(), server
    )
    server.add_insecure_port('[::]:50054')
    server.start()
    print("Chat Server started on port 50054")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

