# api_client.py
import requests
import json
from typing import Dict, Any, Optional
import time

class ModalAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "SampleModalClient/1.0.0"
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request and handle response"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    return e.response.json()
                except:
                    return {"error": str(e)}
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._make_request("GET", "/health")
    
    def get_users(self, role: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Get users with optional filtering"""
        params = {"limit": limit}
        if role:
            params["role"] = role
        return self._make_request("GET", "/api/users", params=params)
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get specific user by ID"""
        return self._make_request("GET", f"/api/users/{user_id}")
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        return self._make_request("POST", "/api/users", json=user_data)
    
    def get_products(self, **filters) -> Dict[str, Any]:
        """Get products with optional filters"""
        valid_filters = ["category", "min_price", "max_price", "in_stock", "tag"]
        params = {k: v for k, v in filters.items() if k in valid_filters}
        return self._make_request("GET", "/api/products", params=params)
    
    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get specific product by ID"""
        return self._make_request("GET", f"/api/products/{product_id}")
    
    def create_order(self, user_id: str, products: list) -> Dict[str, Any]:
        """Create a new order"""
        order_data = {
            "user_id": user_id,
            "products": products
        }
        return self._make_request("POST", "/api/orders", json=order_data)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API statistics"""
        return self._make_request("GET", "/api/stats")
    
    def generate_random_data(self, data_type: str = "users", count: int = 5) -> Dict[str, Any]:
        """Generate random sample data"""
        params = {"data_type": data_type, "count": count}
        return self._make_request("GET", "/api/simulate/random-data", params=params)
    
    def test_all_endpoints(self):
        """Test all API endpoints"""
        print("=" * 50)
        print("Testing Modal API Endpoints")
        print("=" * 50)
        
        # 1. Health check
        print("\n1. Health Check:")
        health = self.health_check()
        print(f"   Status: {health.get('success', False)}")
        print(f"   Message: {health.get('message', 'No message')}")
        
        # 2. Get users
        print("\n2. Getting Users:")
        users = self.get_users(limit=3)
        if users.get('success'):
            print(f"   Found {len(users['data'])} users")
            for user in users['data'][:2]:  # Show first 2
                print(f"   - {user['username']} ({user['email']})")
        
        # 3. Get products
        print("\n3. Getting Products:")
        products = self.get_products(in_stock=True, limit=2)
        if products.get('success'):
            print(f"   Found {len(products['data'])} products")
            for product in products['data']:
                print(f"   - {product['name']}: ${product['price']}")
        
        # 4. Generate random data
        print("\n4. Generating Random Products:")
        random_data = self.generate_random_data("products", 2)
        if random_data.get('success'):
            for product in random_data['data']:
                print(f"   - {product['name']} (${product['price']})")
        
        # 5. Get statistics
        print("\n5. Getting Statistics:")
        stats = self.get_statistics()
        if stats.get('success'):
            data = stats['data']
            print(f"   Total Users: {data['total_users']}")
            print(f"   Total Products: {data['total_products']}")
            print(f"   In-stock Products: {data['in_stock_products']}")
        
        print("\n" + "=" * 50)
        print("Testing Complete!")
        print("=" * 50)

# Example usage
def example_usage():
    """Example of how to use the client"""
    
    # Initialize client
    client = ModalAPIClient("http://localhost:8000")
    
    # Quick test
    client.test_all_endpoints()
    
    # More detailed examples
    print("\nDetailed Examples:")
    print("-" * 30)
    
    # Example 1: Create a new user
    print("\nExample 1: Creating a new user")
    new_user = {
        "username": "test_user",
        "email": "test@example.com",
        "role": "user"
    }
    result = client.create_user(new_user)
    if result.get('success'):
        print(f"User created: {result['data']['username']} (ID: {result['data']['id']})")
    
    # Example 2: Create an order
    print("\nExample 2: Creating an order")
    order_products = [
        {"product_id": "prod_001", "quantity": 1},
        {"product_id": "prod_002", "quantity": 2}
    ]
    # Note: You'll need a valid user_id from your database
    # result = client.create_order("user_001", order_products)
    # if result.get('success'):
    #     print(f"Order created: ${result['data']['total_amount']}")
    
    # Example 3: Filter products
    print("\nExample 3: Filtering electronics products")
    electronics = client.get_products(category="Electronics")
    if electronics.get('success'):
        for product in electronics['data']:
            print(f"  {product['name']}: ${product['price']}")

if __name__ == "__main__":
    # Check if server is running
    try:
        example_usage()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure to run the server first:")
        print("1. Install requirements: pip install fastapi uvicorn pydantic")
        print("2. Run server: python modal_api.py")
        print("3. Then run this client: python api_client.py")