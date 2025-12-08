# modal_api.py
from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import random
import uuid
from enum import Enum

# Create FastAPI app
app = FastAPI(title="Sample Modal API", version="1.0.0")

# ========== Data Models ==========
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    role: UserRole = UserRole.USER
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
    stock_quantity: int = 0
    tags: List[str] = []

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    products: List[Dict[str, Any]]  # List of product IDs with quantities
    total_amount: float
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ========== Simulated Database ==========
class SimulatedDatabase:
    def __init__(self):
        self.users = self._generate_sample_users()
        self.products = self._generate_sample_products()
        self.orders = []
    
    def _generate_sample_users(self):
        return [
            User(id="user_001", username="alice_w", email="alice@example.com", role=UserRole.ADMIN),
            User(id="user_002", username="bob_smith", email="bob@example.com", role=UserRole.USER),
            User(id="user_003", username="charlie_b", email="charlie@example.com", role=UserRole.GUEST),
        ]
    
    def _generate_sample_products(self):
        return [
            Product(
                id="prod_001",
                name="Wireless Headphones",
                description="Noise-cancelling wireless headphones",
                price=199.99,
                category="Electronics",
                stock_quantity=50,
                tags=["audio", "wireless", "tech"]
            ),
            Product(
                id="prod_002",
                name="Coffee Maker",
                description="Programmable drip coffee maker",
                price=89.99,
                category="Home & Kitchen",
                stock_quantity=25,
                tags=["kitchen", "appliance", "coffee"]
            ),
            Product(
                id="prod_003",
                name="Yoga Mat",
                description="Eco-friendly non-slip yoga mat",
                price=29.99,
                category="Fitness",
                stock_quantity=100,
                tags=["fitness", "yoga", "exercise"]
            ),
        ]

db = SimulatedDatabase()

# ========== Helper Functions ==========
def create_api_response(success: bool, message: str, data: Any = None):
    return ApiResponse(
        success=success,
        message=message,
        data=data,
        timestamp=datetime.now()
    )

# ========== API Endpoints ==========
@app.get("/")
async def root():
    return {
        "message": "Welcome to Sample Modal API",
        "endpoints": {
            "users": "/api/users",
            "products": "/api/products",
            "orders": "/api/orders",
            "health": "/health",
            "simulate_error": "/simulate-error"
        }
    }

@app.get("/health")
async def health_check():
    """Check API health status"""
    return create_api_response(
        success=True,
        message="API is running normally",
        data={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    )

@app.get("/api/users", response_model=ApiResponse)
async def get_users(
    role: Optional[UserRole] = None,
    active_only: bool = True,
    limit: int = Query(10, ge=1, le=100)
):
    """Get all users with optional filtering"""
    users = db.users
    
    if role:
        users = [u for u in users if u.role == role]
    
    if active_only:
        users = [u for u in users if u.is_active]
    
    users = users[:limit]
    
    return create_api_response(
        success=True,
        message=f"Retrieved {len(users)} users",
        data=[user.dict() for user in users]
    )

@app.get("/api/users/{user_id}", response_model=ApiResponse)
async def get_user(user_id: str):
    """Get a specific user by ID"""
    user = next((u for u in db.users if u.id == user_id), None)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return create_api_response(
        success=True,
        message="User retrieved successfully",
        data=user.dict()
    )

@app.post("/api/users", response_model=ApiResponse)
async def create_user(user: User):
    """Create a new user"""
    # Check if username or email already exists
    if any(u.username == user.username for u in db.users):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if any(u.email == user.email for u in db.users):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db.users.append(user)
    
    return create_api_response(
        success=True,
        message="User created successfully",
        data=user.dict()
    )

@app.get("/api/products", response_model=ApiResponse)
async def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    in_stock: bool = True,
    tag: Optional[str] = None
):
    """Get products with filtering options"""
    products = db.products
    
    if category:
        products = [p for p in products if p.category.lower() == category.lower()]
    
    if min_price is not None:
        products = [p for p in products if p.price >= min_price]
    
    if max_price is not None:
        products = [p for p in products if p.price <= max_price]
    
    if in_stock:
        products = [p for p in products if p.in_stock and p.stock_quantity > 0]
    
    if tag:
        products = [p for p in products if tag.lower() in [t.lower() for t in p.tags]]
    
    return create_api_response(
        success=True,
        message=f"Retrieved {len(products)} products",
        data=[product.dict() for product in products]
    )

@app.get("/api/products/{product_id}", response_model=ApiResponse)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    product = next((p for p in db.products if p.id == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return create_api_response(
        success=True,
        message="Product retrieved successfully",
        data=product.dict()
    )

@app.post("/api/orders", response_model=ApiResponse)
async def create_order(order_data: dict = Body(...)):
    """Create a new order"""
    # Validate user exists
    user = next((u for u in db.users if u.id == order_data.get("user_id")), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate products
    products = []
    total_amount = 0
    
    for item in order_data.get("products", []):
        product_id = item.get("product_id")
        quantity = item.get("quantity", 1)
        
        product = next((p for p in db.products if p.id == product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        
        if product.stock_quantity < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}"
            )
        
        # Update stock
        product.stock_quantity -= quantity
        if product.stock_quantity == 0:
            product.in_stock = False
        
        products.append({
            "product_id": product_id,
            "name": product.name,
            "quantity": quantity,
            "price": product.price,
            "subtotal": product.price * quantity
        })
        
        total_amount += product.price * quantity
    
    # Create order
    order = Order(
        user_id=user.id,
        products=products,
        total_amount=total_amount,
        status="confirmed"
    )
    
    db.orders.append(order)
    
    return create_api_response(
        success=True,
        message="Order created successfully",
        data=order.dict()
    )

@app.get("/api/orders/{order_id}", response_model=ApiResponse)
async def get_order(order_id: str):
    """Get a specific order by ID"""
    order = next((o for o in db.orders if o.id == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return create_api_response(
        success=True,
        message="Order retrieved successfully",
        data=order.dict()
    )

@app.get("/api/stats", response_model=ApiResponse)
async def get_statistics():
    """Get API statistics"""
    stats = {
        "total_users": len(db.users),
        "total_products": len(db.products),
        "total_orders": len(db.orders),
        "active_users": len([u for u in db.users if u.is_active]),
        "in_stock_products": len([p for p in db.products if p.in_stock]),
        "total_inventory_value": sum(p.price * p.stock_quantity for p in db.products),
        "recent_orders": len([o for o in db.orders 
                             if (datetime.now() - o.created_at).days < 7])
    }
    
    return create_api_response(
        success=True,
        message="Statistics retrieved",
        data=stats
    )

@app.get("/api/simulate/random-data")
async def generate_random_data(
    data_type: str = Query("users", regex="^(users|products|orders)$"),
    count: int = Query(5, ge=1, le=20)
):
    """Generate random sample data"""
    random_data = []
    
    if data_type == "users":
        first_names = ["John", "Jane", "Alex", "Emily", "Chris", "Sarah", "Mike", "Lisa"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller"]
        domains = ["example.com", "test.org", "demo.net"]
        
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            username = f"{first.lower()}_{last.lower()}"
            email = f"{username}@{random.choice(domains)}"
            
            user = User(
                username=username,
                email=email,
                role=random.choice(list(UserRole)),
                is_active=random.choice([True, False])
            )
            random_data.append(user.dict())
    
    elif data_type == "products":
        categories = ["Electronics", "Books", "Clothing", "Home", "Sports", "Toys"]
        adjectives = ["Premium", "Standard", "Deluxe", "Basic", "Advanced", "Professional"]
        nouns = ["Widget", "Gadget", "Device", "Tool", "Equipment", "Accessory"]
        
        for i in range(count):
            product = Product(
                name=f"{random.choice(adjectives)} {random.choice(nouns)}",
                description=f"Description for {random.choice(adjectives).lower()} product",
                price=round(random.uniform(10, 500), 2),
                category=random.choice(categories),
                stock_quantity=random.randint(0, 200),
                tags=[random.choice(["new", "sale", "featured", "bestseller"])]
            )
            product.in_stock = product.stock_quantity > 0
            random_data.append(product.dict())
    
    return create_api_response(
        success=True,
        message=f"Generated {count} random {data_type}",
        data=random_data
    )

@app.get("/simulate-error")
async def simulate_error():
    """Endpoint to simulate various HTTP errors"""
    error_types = [
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (404, "Not Found"),
        (500, "Internal Server Error"),
        (503, "Service Unavailable")
    ]
    
    error = random.choice(error_types)
    raise HTTPException(status_code=error[0], detail=error[1])

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return create_api_response(
        success=False,
        message=f"Error: {exc.detail}",
        data={"status_code": exc.status_code}
    )

# ========== Run the Server ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)