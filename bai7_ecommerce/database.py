from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Product database
PRODUCT_DB_URL = os.getenv("PRODUCT_DB_URL", "sqlite:///./products.db")
product_engine = create_engine(
    PRODUCT_DB_URL,
    connect_args={"check_same_thread": False} if "sqlite" in PRODUCT_DB_URL else {}
)
ProductSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=product_engine)

# Price database
PRICE_DB_URL = os.getenv("PRICE_DB_URL", "sqlite:///./prices.db")
price_engine = create_engine(
    PRICE_DB_URL,
    connect_args={"check_same_thread": False} if "sqlite" in PRICE_DB_URL else {}
)
PriceSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=price_engine)

# Inventory database
INVENTORY_DB_URL = os.getenv("INVENTORY_DB_URL", "sqlite:///./inventories.db")
inventory_engine = create_engine(
    INVENTORY_DB_URL,
    connect_args={"check_same_thread": False} if "sqlite" in INVENTORY_DB_URL else {}
)
InventorySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=inventory_engine)

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    inventory = Column(Integer, default=0)


class Price(Base):
    __tablename__ = "prices"
    
    product_id = Column(Integer, primary_key=True, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String, default="VND")
    updated_at = Column(Float)


class Inventory(Base):
    __tablename__ = "inventories"
    
    product_id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, default=0)
    updated_at = Column(Float)


def init_product_db():
    Base.metadata.create_all(bind=product_engine, tables=[Product.__table__])

def init_price_db():
    Base.metadata.create_all(bind=price_engine, tables=[Price.__table__])

def init_inventory_db():
    Base.metadata.create_all(bind=inventory_engine, tables=[Inventory.__table__])

def init_db():
    # Initialize all databases (for convenience)
    init_product_db()
    init_price_db()
    init_inventory_db()


# Convenience functions for each service
def get_product_db():
    db = ProductSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_price_db():
    db = PriceSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_inventory_db():
    db = InventorySessionLocal()
    try:
        yield db
    finally:
        db.close()

