import grpc
import sys
import weather_pb2
import weather_pb2_grpc


def run():
    if len(sys.argv) < 2:
        print("Usage: python client.py <city_name>")
        sys.exit(1)
    
    city = sys.argv[1]
    
    channel = grpc.insecure_channel('localhost:50052')
    stub = weather_pb2_grpc.WeatherServiceStub(channel)
    
    request = weather_pb2.WeatherRequest(city=city)
    
    print(f"Receiving weather forecast for {city}...\n")
    
    try:
        for response in stub.GetWeatherForecast(request):
            print(f"[Day {response.day}] {response.forecast}")
    except grpc.RpcError as e:
        print(f"Error: {e.code()}")
    
    channel.close()


if __name__ == '__main__':
    run()

