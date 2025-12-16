import grpc
from concurrent import futures
import time
import weather_pb2
import weather_pb2_grpc


class WeatherServiceServicer(weather_pb2_grpc.WeatherServiceServicer):
    def GetWeatherForecast(self, request, context):
        city = request.city
        forecasts = [
            {"day": 1, "temp": "25°C", "condition": "Sunny"},
            {"day": 2, "temp": "23°C", "condition": "Partly Cloudy"},
            {"day": 3, "temp": "22°C", "condition": "Rainy"},
            {"day": 4, "temp": "24°C", "condition": "Sunny"},
            {"day": 5, "temp": "26°C", "condition": "Clear"},
        ]
        
        for forecast in forecasts:
            if context.is_active():
                response = weather_pb2.WeatherResponse(
                    city=city,
                    forecast=f"Day {forecast['day']}: {forecast['temp']}, {forecast['condition']}",
                    day=forecast['day'],
                    temperature=forecast['temp'],
                    condition=forecast['condition']
                )
                yield response
                time.sleep(1)  # Gửi mỗi 1 giây
            else:
                break


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(
        WeatherServiceServicer(), server
    )
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Weather Server started on port 50052")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

