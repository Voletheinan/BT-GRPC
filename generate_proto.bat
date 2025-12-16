@echo off
REM Script để generate Python code từ proto files cho Windows

echo Generating proto files...

REM Bài 1
echo Generating bai1_hello...
cd bai1_hello
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. hello.proto
cd ..

REM Bài 2
echo Generating bai2_weather...
cd bai2_weather
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. weather.proto
cd ..

REM Bài 3
echo Generating bai3_log_upload...
cd bai3_log_upload
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. log.proto
cd ..

REM Bài 4
echo Generating bai4_chat...
cd bai4_chat
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. chat.proto
cd ..

REM Bài 5
echo Generating bai5_user_profile...
cd bai5_user_profile
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto
cd ..

REM Bài 6
echo Generating bai6_api_gateway...
cd bai6_api_gateway
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto
cd ..

REM Bài 7
echo Generating bai7_ecommerce...
cd bai7_ecommerce
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. product.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. price.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. inventory.proto
cd ..

echo Done!

