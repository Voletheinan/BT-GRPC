"""
Inventory Service - gRPC Microservice
Quản lý tồn kho sản phẩm
"""
import grpc
from concurrent import futures
from sqlalchemy.orm import Session
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import inventory_pb2
import inventory_pb2_grpc
from database import InventorySessionLocal, Inventory, init_inventory_db


class InventoryServiceServicer(inventory_pb2_grpc.InventoryServiceServicer):
    def GetInventory(self, request, context):
        db = InventorySessionLocal()
        try:
            inv = db.query(Inventory).filter(Inventory.product_id == request.product_id).first()
            if not inv:
                return inventory_pb2.InventoryResponse(
                    success=False,
                    message=f"Inventory for product {request.product_id} not found"
                )
            
            return inventory_pb2.InventoryResponse(
                success=True,
                message="Inventory retrieved successfully",
                inventory=inventory_pb2.Inventory(
                    product_id=inv.product_id,
                    quantity=inv.quantity,
                    updated_at=int(inv.updated_at * 1000)
                )
            )
        except Exception as e:
            return inventory_pb2.InventoryResponse(
                success=False,
                message=f"Error retrieving inventory: {str(e)}"
            )
        finally:
            db.close()
    
    def UpdateInventory(self, request, context):
        db = InventorySessionLocal()
        try:
            inv = db.query(Inventory).filter(Inventory.product_id == request.product_id).first()
            
            if inv:
                inv.quantity = request.quantity
                inv.updated_at = time.time()
            else:
                inv = Inventory(
                    product_id=request.product_id,
                    quantity=request.quantity,
                    updated_at=time.time()
                )
                db.add(inv)
            
            db.commit()
            db.refresh(inv)
            
            return inventory_pb2.InventoryResponse(
                success=True,
                message="Inventory updated successfully",
                inventory=inventory_pb2.Inventory(
                    product_id=inv.product_id,
                    quantity=inv.quantity,
                    updated_at=int(inv.updated_at * 1000)
                )
            )
        except Exception as e:
            db.rollback()
            return inventory_pb2.InventoryResponse(
                success=False,
                message=f"Error updating inventory: {str(e)}"
            )
        finally:
            db.close()
    
    def GetInventories(self, request, context):
        db = InventorySessionLocal()
        try:
            inventories = db.query(Inventory).filter(
                Inventory.product_id.in_(request.product_ids)
            ).all()
            
            inv_list = [
                inventory_pb2.Inventory(
                    product_id=inv.product_id,
                    quantity=inv.quantity,
                    updated_at=int(inv.updated_at * 1000)
                )
                for inv in inventories
            ]
            
            return inventory_pb2.InventoriesResponse(inventories=inv_list)
        except Exception as e:
            return inventory_pb2.InventoriesResponse(inventories=[])
        finally:
            db.close()


def serve():
    init_inventory_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(
        InventoryServiceServicer(), server
    )
    server.add_insecure_port('[::]:50063')
    server.start()
    print("Inventory Service started on port 50063")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

