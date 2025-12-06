"""Test script to verify upload and process endpoints."""
import requests
import json

BASE_URL = "http://localhost:5000"

# Test 1: Upload PDF
print("Test 1: Uploading PDF...")
with open('../samples/request_for_repair.pdf', 'rb') as f:
    files = {'pdf': f}
    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
print(f"Status: {response.status_code}")
data = response.json()
print(f"Response: {json.dumps(data, indent=2)}")

if data.get('success'):
    pdf_id = data['pdf_id']
    print(f"\n✓ PDF uploaded successfully!")
    print(f"  PDF ID: {pdf_id}")
    print(f"  Pages: {len(data['pages'])}")
    
    # Test 2: Process form
    print(f"\nTest 2: Processing form...")
    form_data = {
        "date_prepared": "2025-12-06",
        "agreement_date": "2025-11-15",
        "property_address": "123 Main Street",
        "buyer_name": "John Doe",
        "seller_name": "Jane Smith",
        "repairs": ["Fix window", "Fix door"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/process",
        json={
            'pdf_id': pdf_id,
            'form_data': form_data
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:500]}...")
    
    if data.get('success'):
        print(f"\n✓ Form processed successfully!")
        print(f"  Placements: {len(data['placements'])}")
    else:
        print(f"\n✗ Error: {data.get('error')}")
else:
    print(f"\n✗ Upload failed: {data.get('error')}")
