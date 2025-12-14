#!/usr/bin/env python3
"""
MockBank API Test Script

Tests all API endpoints to verify they work correctly.

Usage:
    cd MockBank/testing
    uv run python test_api.py
    
Make sure the server is running:
    uv run uvicorn server:app --reload --port 8080
"""

import requests
import json

BASE_URL = "http://localhost:8080"


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_response(response):
    print(f"  Status: {response.status_code}")
    try:
        data = response.json()
        print(f"  Response: {json.dumps(data, indent=4)}")
    except:
        print(f"  Response: {response.text[:200]}")


def test_get_transactions():
    print_header("GET /api/transactions")
    response = requests.get(f"{BASE_URL}/api/transactions")
    print_response(response)
    return response.status_code == 200


def test_get_transactions_since():
    print_header("GET /api/transactions?since=2025-12-01")
    response = requests.get(f"{BASE_URL}/api/transactions", params={"since": "2025-12-01"})
    print_response(response)
    return response.status_code == 200


def test_create_transaction():
    print_header("POST /api/transactions")
    data = {
        "date": "2025-12-07",
        "description": "API TEST TRANSACTION",
        "amount": -99.99,
        "currency": "CHF"
    }
    print(f"  Sending: {json.dumps(data)}")
    response = requests.post(f"{BASE_URL}/api/transactions", json=data)
    print_response(response)
    return response.status_code == 200


def test_get_stocks():
    print_header("GET /api/stocks")
    response = requests.get(f"{BASE_URL}/api/stocks")
    print_response(response)
    return response.status_code == 200


def test_get_single_stock():
    print_header("GET /api/stocks/AAPL")
    response = requests.get(f"{BASE_URL}/api/stocks/AAPL")
    print_response(response)
    return response.status_code == 200


def test_get_nonexistent_stock():
    print_header("GET /api/stocks/FAKE (non-existent)")
    response = requests.get(f"{BASE_URL}/api/stocks/FAKE")
    print_response(response)
    return response.status_code == 200


def test_buy_stock():
    print_header("POST /api/stocks/AAPL/add (Buy 2 shares for 400 CHF)")
    data = {
        "quantity": 2,
        "price": 400.00
    }
    print(f"  Sending: {json.dumps(data)}")
    response = requests.post(f"{BASE_URL}/api/stocks/AAPL/add", json=data)
    print_response(response)
    return response.status_code == 200


def test_sell_stock():
    print_header("POST /api/stocks/AAPL/remove (Sell 1 share for 210 CHF)")
    data = {
        "quantity": 1,
        "price": 210.00
    }
    print(f"  Sending: {json.dumps(data)}")
    response = requests.post(f"{BASE_URL}/api/stocks/AAPL/remove", json=data)
    print_response(response)
    return response.status_code == 200


def test_buy_new_stock():
    print_header("POST /api/stocks/GME/add (Buy new stock: 10 shares for 150 CHF)")
    data = {
        "quantity": 10,
        "price": 150.00
    }
    print(f"  Sending: {json.dumps(data)}")
    response = requests.post(f"{BASE_URL}/api/stocks/GME/add", json=data)
    print_response(response)
    return response.status_code == 200


def main():
    print("\n" + "="*60)
    print("  MockBank API Test Suite")
    print("="*60)
    print(f"\n  Base URL: {BASE_URL}")
    
    # Check if server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n  ERROR: Server is not running!")
        print("  Start it with: uv run uvicorn server:app --reload --port 8080")
        return
    
    tests = [
        ("Get all transactions", test_get_transactions),
        ("Get transactions since date", test_get_transactions_since),
        ("Create transaction", test_create_transaction),
        ("Get all stocks", test_get_stocks),
        ("Get single stock (AAPL)", test_get_single_stock),
        ("Get non-existent stock", test_get_nonexistent_stock),
        ("Buy stock (AAPL)", test_buy_stock),
        ("Sell stock (AAPL)", test_sell_stock),
        ("Buy new stock (GME)", test_buy_new_stock),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"  Error: {e}")
            results.append((name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {name}")
    
    print(f"\n  Results: {passed}/{total} passed")
    
    if passed == total:
        print("\n  All tests passed!")
    else:
        print(f"\n  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

