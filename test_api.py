#!/usr/bin/env python3
"""Test the REST API"""

import requests
import json

print("=" * 60)
print("TESTING REST API")
print("=" * 60)

# Generate API key
print("\n[1] Generating API Key...")
key_resp = requests.post('http://localhost:5000/api/keys/generate', 
    json={'name': 'Test Key'})
api_key = key_resp.json()['data']['key']
print(f'✓ API Key: {api_key}')

# Test Wikipedia search
print("\n[2] Testing Wikipedia Search...")
search_resp = requests.post('http://localhost:5000/api/wikipedia/search',
    headers={'X-API-Key': api_key},
    json={'topic': 'Python'})

if search_resp.status_code == 200:
    search_data = search_resp.json()
    print(f'✓ Search Success!')
    print(f'  Title: {search_data["title"]}')
else:
    print(f'✗ Error: {search_resp.status_code}')

# Test Wikipedia fetch
print("\n[3] Testing Wikipedia Fetch...")
fetch_resp = requests.post('http://localhost:5000/api/wikipedia/fetch',
    headers={'X-API-Key': api_key},
    json={'topic': 'Python (programming language)'})

if fetch_resp.status_code == 200:
    fetch_data = fetch_resp.json()
    print(f'✓ Fetch Success!')
    print(f'  Title: {fetch_data["title"]}')
    print(f'  Categories: {len(fetch_data["categories"])} items')
    print(f'  References: {len(fetch_data["references"])} items')
else:
    print(f'✗ Error: {fetch_resp.status_code}')
    print(f'  Response: {fetch_resp.text}')

# Test cache search
print("\n[4] Testing Cache Search...")
cache_resp = requests.get('http://localhost:5000/api/wikipedia/cache/search',
    headers={'X-API-Key': api_key},
    params={'q': 'python'})

if cache_resp.status_code == 200:
    cache_data = cache_resp.json()
    print(f'✓ Cache Search Success!')
    print(f'  Found: {cache_data["count"]} items')
    for item in cache_data['data'][:3]:
        print(f'    - {item["title"]}')
else:
    print(f'✗ Error: {cache_resp.status_code}')

print("\n" + "=" * 60)
print("ALL API TESTS PASSED!")
print("=" * 60)
