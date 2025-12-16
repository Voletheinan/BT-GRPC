"""
REST API Gateway cho E-Commerce Product Service
Tích hợp Product Service, Price Service và Inventory Service
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import grpc
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import product_pb2
import product_pb2_grpc
import price_pb2
import price_pb2_grpc
import inventory_pb2
import inventory_pb2_grpc

app = FastAPI(
    title="E-Commerce Product API Gateway",
    description="REST API Gateway integrating Product, Price, and Inventory Services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# gRPC connections
PRODUCT_SERVICE = os.getenv("PRODUCT_SERVICE", "localhost:50061")
PRICE_SERVICE = os.getenv("PRICE_SERVICE", "localhost:50062")
INVENTORY_SERVICE = os.getenv("INVENTORY_SERVICE", "localhost:50063")

product_channel = grpc.insecure_channel(PRODUCT_SERVICE)
product_stub = product_pb2_grpc.ProductServiceStub(product_channel)

price_channel = grpc.insecure_channel(PRICE_SERVICE)
price_stub = price_pb2_grpc.PriceServiceStub(price_channel)

inventory_channel = grpc.insecure_channel(INVENTORY_SERVICE)
inventory_stub = inventory_pb2_grpc.InventoryServiceStub(inventory_channel)


class ProductCreate(BaseModel):
    name: str
    description: str = ""
    category: str
    price: float


class ProductUpdate(BaseModel):
    name: str = None
    description: str = None
    category: str = None
    price: float = None


def enrich_product_with_details(product):
    """Lấy thêm thông tin price và inventory từ các services khác"""
    try:
        # Get price
        price_request = price_pb2.GetPriceRequest(product_id=product.id)
        price_response = price_stub.GetPrice(price_request)
        if price_response.success:
            product.price = price_response.price.price
        
        # Get inventory
        inv_request = inventory_pb2.GetInventoryRequest(product_id=product.id)
        inv_response = inventory_stub.GetInventory(inv_request)
        if inv_response.success:
            product.inventory = inv_response.inventory.quantity
    except:
        pass  # Ignore errors, use default values
    return product


@app.get("/")
def root():
    return {
        "message": "E-Commerce Product API Gateway",
        "services": {
            "product": PRODUCT_SERVICE,
            "price": PRICE_SERVICE,
            "inventory": INVENTORY_SERVICE
        },
        "endpoints": {
            "GET /api/products/{id}": "Get product details",
            "GET /api/products": "List products",
            "POST /api/products": "Create product",
            "GET /api/products/search?q={query}": "Search products",
            "PUT /api/products/{id}/price": "Update product price",
            "PUT /api/products/{id}/inventory": "Update product inventory"
        }
    }


@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    """Get product with price and inventory"""
    try:
        request = product_pb2.GetProductRequest(id=product_id)
        response = product_stub.GetProduct(request)
        if not response.success:
            raise HTTPException(status_code=404, detail=response.message)
        
        product = enrich_product_with_details(response.product)
        
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "price": product.price,
            "inventory": product.inventory
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.get("/api/products")
def list_products(page: int = 1, page_size: int = 10, category: str = None):
    """List products with pagination"""
    try:
        request = product_pb2.ListProductsRequest(
            page=page,
            page_size=page_size,
            category=category or ""
        )
        response = product_stub.ListProducts(request)
        
        # Enrich with price and inventory
        enriched_products = []
        for product in response.products:
            enriched_product = enrich_product_with_details(product)
            enriched_products.append({
                "id": enriched_product.id,
                "name": enriched_product.name,
                "description": enriched_product.description,
                "category": enriched_product.category,
                "price": enriched_product.price,
                "inventory": enriched_product.inventory
            })
        
        return {
            "products": enriched_products,
            "total": response.total,
            "page": page,
            "page_size": page_size
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.post("/api/products", status_code=201)
def create_product(product: ProductCreate):
    """Create a new product"""
    try:
        request = product_pb2.CreateProductRequest(
            name=product.name,
            description=product.description,
            category=product.category,
            price=product.price
        )
        response = product_stub.CreateProduct(request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        # Set initial price
        price_request = price_pb2.UpdatePriceRequest(
            product_id=response.product.id,
            price=product.price,
            currency="VND"
        )
        price_stub.UpdatePrice(price_request)
        
        # Set initial inventory to 0
        inv_request = inventory_pb2.UpdateInventoryRequest(
            product_id=response.product.id,
            quantity=0
        )
        inventory_stub.UpdateInventory(inv_request)
        
        return {
            "id": response.product.id,
            "name": response.product.name,
            "description": response.product.description,
            "category": response.product.category,
            "price": response.product.price,
            "inventory": 0
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.get("/api/products/search")
def search_products(q: str, page: int = 1, page_size: int = 10):
    """Search products"""
    try:
        request = product_pb2.SearchProductRequest(
            query=q,
            page=page,
            page_size=page_size
        )
        response = product_stub.SearchProduct(request)
        
        # Enrich with price and inventory
        enriched_products = []
        for product in response.products:
            enriched_product = enrich_product_with_details(product)
            enriched_products.append({
                "id": enriched_product.id,
                "name": enriched_product.name,
                "description": enriched_product.description,
                "category": enriched_product.category,
                "price": enriched_product.price,
                "inventory": enriched_product.inventory
            })
        
        return {
            "products": enriched_products,
            "total": response.total,
            "page": page,
            "page_size": page_size,
            "query": q
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.put("/api/products/{product_id}/price")
def update_price(product_id: int, price: float, currency: str = "VND"):
    """Update product price"""
    try:
        request = price_pb2.UpdatePriceRequest(
            product_id=product_id,
            price=price,
            currency=currency
        )
        response = price_stub.UpdatePrice(request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        return {
            "product_id": response.price.product_id,
            "price": response.price.price,
            "currency": response.price.currency,
            "updated_at": response.price.updated_at
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.put("/api/products/{product_id}/inventory")
def update_inventory(product_id: int, quantity: int):
    """Update product inventory"""
    try:
        request = inventory_pb2.UpdateInventoryRequest(
            product_id=product_id,
            quantity=quantity
        )
        response = inventory_stub.UpdateInventory(request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        return {
            "product_id": response.inventory.product_id,
            "quantity": response.inventory.quantity,
            "updated_at": response.inventory.updated_at
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC Error: {e.code()}")


@app.get("/health")
def health_check():
    """Health check for all services"""
    status = {
        "status": "healthy",
        "services": {}
    }
    
    try:
        # Check Product Service
        request = product_pb2.ListProductsRequest(page=1, page_size=1)
        product_stub.ListProducts(request)
        status["services"]["product"] = "connected"
    except:
        status["services"]["product"] = "disconnected"
        status["status"] = "unhealthy"
    
    try:
        # Check Price Service
        request = price_pb2.GetPricesRequest(product_ids=[])
        price_stub.GetPrices(request)
        status["services"]["price"] = "connected"
    except:
        status["services"]["price"] = "disconnected"
        status["status"] = "unhealthy"
    
    try:
        # Check Inventory Service
        request = inventory_pb2.GetInventoriesRequest(product_ids=[])
        inventory_stub.GetInventories(request)
        status["services"]["inventory"] = "connected"
    except:
        status["services"]["inventory"] = "disconnected"
        status["status"] = "unhealthy"
    
    return status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

