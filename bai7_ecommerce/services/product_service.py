"""
Product Service - gRPC Microservice
Quản lý thông tin sản phẩm
"""
import grpc
from concurrent import futures
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import product_pb2
import product_pb2_grpc
from database import ProductSessionLocal, Product, init_product_db


class ProductServiceServicer(product_pb2_grpc.ProductServiceServicer):
    def GetProduct(self, request, context):
        db = ProductSessionLocal()
        try:
            product = db.query(Product).filter(Product.id == request.id).first()
            if not product:
                return product_pb2.ProductResponse(
                    success=False,
                    message=f"Product with id {request.id} not found"
                )
            
            return product_pb2.ProductResponse(
                success=True,
                message="Product retrieved successfully",
                product=product_pb2.Product(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    category=product.category,
                    price=product.price,
                    inventory=product.inventory
                )
            )
        except Exception as e:
            return product_pb2.ProductResponse(
                success=False,
                message=f"Error retrieving product: {str(e)}"
            )
        finally:
            db.close()
    
    def ListProducts(self, request, context):
        db = ProductSessionLocal()
        try:
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 10
            
            offset = (page - 1) * page_size
            query = db.query(Product)
            
            if request.category:
                query = query.filter(Product.category == request.category)
            
            products = query.offset(offset).limit(page_size).all()
            total = query.count()
            
            product_list = [
                product_pb2.Product(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    category=p.category,
                    price=p.price,
                    inventory=p.inventory
                )
                for p in products
            ]
            
            return product_pb2.ListProductsResponse(
                products=product_list,
                total=total
            )
        except Exception as e:
            return product_pb2.ListProductsResponse(products=[], total=0)
        finally:
            db.close()
    
    def CreateProduct(self, request, context):
        db = ProductSessionLocal()
        try:
            product = Product(
                name=request.name,
                description=request.description,
                category=request.category,
                price=request.price,
                inventory=0  # Mặc định inventory = 0, sẽ được cập nhật bởi Inventory Service
            )
            db.add(product)
            db.commit()
            db.refresh(product)
            
            return product_pb2.ProductResponse(
                success=True,
                message="Product created successfully",
                product=product_pb2.Product(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    category=product.category,
                    price=product.price,
                    inventory=product.inventory
                )
            )
        except Exception as e:
            db.rollback()
            return product_pb2.ProductResponse(
                success=False,
                message=f"Error creating product: {str(e)}"
            )
        finally:
            db.close()
    
    def SearchProduct(self, request, context):
        db = ProductSessionLocal()
        try:
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 10
            
            offset = (page - 1) * page_size
            query = request.query.lower()
            
            products = db.query(Product).filter(
                (Product.name.ilike(f"%{query}%")) |
                (Product.description.ilike(f"%{query}%")) |
                (Product.category.ilike(f"%{query}%"))
            ).offset(offset).limit(page_size).all()
            
            total = db.query(Product).filter(
                (Product.name.ilike(f"%{query}%")) |
                (Product.description.ilike(f"%{query}%")) |
                (Product.category.ilike(f"%{query}%"))
            ).count()
            
            product_list = [
                product_pb2.Product(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    category=p.category,
                    price=p.price,
                    inventory=p.inventory
                )
                for p in products
            ]
            
            return product_pb2.ListProductsResponse(
                products=product_list,
                total=total
            )
        except Exception as e:
            return product_pb2.ListProductsResponse(products=[], total=0)
        finally:
            db.close()


def serve():
    init_product_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_pb2_grpc.add_ProductServiceServicer_to_server(
        ProductServiceServicer(), server
    )
    server.add_insecure_port('[::]:50061')
    server.start()
    print("Product Service started on port 50061")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

