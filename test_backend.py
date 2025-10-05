#!/usr/bin/env python3
"""
Simple test script to verify the backend API is working correctly.
"""

import requests
import json

# Test data - sample explanation
test_explanation = """
This is a Flask-based REST API application with three main layers:

1. **Routes Layer** - Handles HTTP requests
   - auth.py: User authentication and login
   - users.py: User management endpoints
   - products.py: Product CRUD operations

2. **Services Layer** - Business logic
   - auth_service.py: JWT token generation
   - payment_service.py: Stripe payment integration

3. **Models Layer** - Database models
   - User: User authentication data
   - Product: Product catalog
   - Order: Order management

External dependencies:
- PostgreSQL database for data storage
- Stripe API for payment processing

Data flows from routes → services → models → database.
"""

def test_health():
    """Test the health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Health check passed\n")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}\n")
        return False

def test_generate_diagram():
    """Test the diagram generation endpoint"""
    print("Testing /generate-diagram endpoint...")
    try:
        response = requests.post(
            'http://localhost:5000/generate-diagram',
            headers={'Content-Type': 'application/json'},
            json={'explanation': test_explanation}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ Diagram generated successfully!")
                print(f"\nMermaid code preview (first 200 chars):")
                print(data['mermaid'][:200] + "...")
                print()
                return True
            else:
                print(f"✗ Failed: {data.get('error')}")
                return False
        else:
            print(f"✗ Request failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}\n")
        return False

def main():
    print("=" * 60)
    print("Backend API Test Suite")
    print("=" * 60)
    print()
    
    # Test health endpoint
    health_ok = test_health()
    
    # Test diagram generation
    if health_ok:
        diagram_ok = test_generate_diagram()
        
        if diagram_ok:
            print("=" * 60)
            print("✓ All tests passed!")
            print("=" * 60)
        else:
            print("=" * 60)
            print("✗ Some tests failed")
            print("=" * 60)
    else:
        print("✗ Backend server not reachable")
        print("Make sure to run: python backend.py")

if __name__ == '__main__':
    main()
