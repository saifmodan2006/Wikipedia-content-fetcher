#!/usr/bin/env python
"""Test Wikipedia data fetching directly"""

from wikipedia_manager import WikipediaManager

print("=" * 60)
print("DIRECT WIKIPEDIA DATA FETCHING TEST")
print("=" * 60)

# Initialize Wikipedia manager
wiki = WikipediaManager()

# Test 1: Search Wikipedia
print("\n[TEST 1] Searching for 'Python Programming'...")
print("-" * 60)
search_result = wiki.search_wikipedia('Python')
print(f"Result: {search_result}")

# Test 2: Fetch full content
print("\n[TEST 2] Fetching content for 'Machine Learning'...")
print("-" * 60)
result = wiki.fetch_wikipedia_content('Machine Learning')

if result['success']:
    print(f"✓ SUCCESS!")
    print(f"  Title: {result['title']}")
    print(f"  URL: {result['url']}")
    print(f"  Content length: {len(result['content'])} characters")
    print(f"  Categories: {len(result['categories'])}")
    print(f"  References: {len(result['references'])}")
    print(f"\n  First 200 characters of content:")
    print(f"  {result['content'][:200]}...")
else:
    print(f"✗ FAILED!")
    print(f"  Error: {result}")

# Test 3: Another search
print("\n[TEST 3] Fetching content for 'Artificial Intelligence'...")
print("-" * 60)
result = wiki.fetch_wikipedia_content('Artificial Intelligence')

if result['success']:
    print(f"✓ SUCCESS!")
    print(f"  Title: {result['title']}")
    print(f"  URL: {result['url']}")
    print(f"  Content length: {len(result['content'])} characters")
    print(f"  Summary: {result.get('summary', 'N/A')[:100]}...")
else:
    print(f"✗ FAILED!")
    print(f"  Error: {result}")

# Test 4: Test with a different topic
print("\n[TEST 4] Fetching content for 'Quantum Computing'...")
print("-" * 60)
result = wiki.fetch_wikipedia_content('Quantum Computing')

if result['success']:
    print(f"✓ SUCCESS!")
    print(f"  Title: {result['title']}")
    print(f"  Content length: {len(result['content'])} characters")
    print(f"  Categories found: {len(result['categories'])}")
else:
    print(f"✗ FAILED!")
    print(f"  Error: {result}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
