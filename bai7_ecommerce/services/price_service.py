"""
Price Service - gRPC Microservice
Quản lý giá sản phẩm
"""
import grpc
from concurrent import futures
from sqlalchemy.orm import Session
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import price_pb2
import price_pb2_grpc
from database import PriceSessionLocal, Price, init_price_db


class PriceServiceServicer(price_pb2_grpc.PriceServiceServicer):
    def GetPrice(self, request, context):
        db = PriceSessionLocal()
        try:
            price_obj = db.query(Price).filter(Price.product_id == request.product_id).first()
            if not price_obj:
                return price_pb2.PriceResponse(
                    success=False,
                    message=f"Price for product {request.product_id} not found"
                )
            
            return price_pb2.PriceResponse(
                success=True,
                message="Price retrieved successfully",
                price=price_pb2.Price(
                    product_id=price_obj.product_id,
                    price=price_obj.price,
                    currency=price_obj.currency,
                    updated_at=int(price_obj.updated_at.timestamp() * 1000)
                )
            )
        except Exception as e:
            return price_pb2.PriceResponse(
                success=False,
                message=f"Error retrieving price: {str(e)}"
            )
        finally:
            db.close()
    
    def UpdatePrice(self, request, context):
        db = PriceSessionLocal()
        try:
            price_obj = db.query(Price).filter(Price.product_id == request.product_id).first()
            
            if price_obj:
                price_obj.price = request.price
                price_obj.currency = request.currency
                price_obj.updated_at = time.time()
            else:
                price_obj = Price(
                    product_id=request.product_id,
                    price=request.price,
                    currency=request.currency,
                    updated_at=time.time()
                )
                db.add(price_obj)
            
            db.commit()
            db.refresh(price_obj)
            
            return price_pb2.PriceResponse(
                success=True,
                message="Price updated successfully",
                price=price_pb2.Price(
                    product_id=price_obj.product_id,
                    price=price_obj.price,
                    currency=price_obj.currency,
                    updated_at=int(price_obj.updated_at * 1000)
                )
            )
        except Exception as e:
            db.rollback()
            return price_pb2.PriceResponse(
                success=False,
                message=f"Error updating price: {str(e)}"
            )
        finally:
            db.close()
    
    def GetPrices(self, request, context):
        db = PriceSessionLocal()
        try:
            prices = db.query(Price).filter(Price.product_id.in_(request.product_ids)).all()
            
            price_list = [
                price_pb2.Price(
                    product_id=p.product_id,
                    price=p.price,
                    currency=p.currency,
                    updated_at=int(p.updated_at * 1000)
                )
                for p in prices
            ]
            
            return price_pb2.PricesResponse(prices=price_list)
        except Exception as e:
            return price_pb2.PricesResponse(prices=[])
        finally:
            db.close()


def serve():
    init_price_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    price_pb2_grpc.add_PriceServiceServicer_to_server(
        PriceServiceServicer(), server
    )
    server.add_insecure_port('[::]:50062')
    server.start()
    print("Price Service started on port 50062")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

