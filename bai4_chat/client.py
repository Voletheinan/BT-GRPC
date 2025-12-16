import grpc
import sys
import threading
import time
import uuid
import chat_pb2
import chat_pb2_grpc


class ChatClient:
    def __init__(self, client_id=None):
        self.client_id = client_id or f"client_{uuid.uuid4().hex[:8]}"
        self.channel = grpc.insecure_channel('localhost:50054')
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self.running = True
    
    def send_message(self, message, target_id=None):
        msg_type = chat_pb2.MessageType.PRIVATE if target_id else chat_pb2.MessageType.BROADCAST
        return chat_pb2.ChatMessage(
            client_id=self.client_id,
            message=message,
            target_client_id=target_id or "",
            timestamp=int(time.time() * 1000),
            type=msg_type
        )
    
    def receive_messages(self, request_iterator):
        try:
            for response in self.stub.Chat(request_iterator):
                if response.client_id == "SERVER":
                    print(f"\n[SERVER] {response.message}")
                elif response.type == chat_pb2.MessageType.PRIVATE:
                    print(f"\n[PRIVATE from {response.client_id}] {response.message}")
                else:
                    print(f"\n[{response.client_id}] {response.message}")
        except grpc.RpcError as e:
            print(f"Error receiving messages: {e.code()}")
    
    def start(self):
        def message_generator():
            # Gửi join message đầu tiên
            yield self.send_message("", "")
            
            while self.running:
                try:
                    user_input = input()
                    if not self.running:
                        break
                    
                    if user_input.startswith("/private "):
                        # Format: /private <client_id> <message>
                        parts = user_input.split(" ", 2)
                        if len(parts) == 3:
                            target_id, msg = parts[1], parts[2]
                            yield self.send_message(msg, target_id)
                        else:
                            print("Usage: /private <client_id> <message>")
                    elif user_input == "/quit":
                        self.running = False
                        break
                    else:
                        yield self.send_message(user_input)
                except EOFError:
                    self.running = False
                    break
        
        print(f"Connected as {self.client_id}")
        print("Type messages to broadcast, or '/private <client_id> <message>' for private chat")
        print("Type '/quit' to exit\n")
        
        # Thread để nhận messages
        receive_thread = threading.Thread(
            target=self.receive_messages,
            args=(message_generator(),),
            daemon=True
        )
        receive_thread.start()
        
        receive_thread.join()
        self.channel.close()


def run():
    client_id = sys.argv[1] if len(sys.argv) > 1 else None
    client = ChatClient(client_id)
    client.start()


if __name__ == '__main__':
    run()

