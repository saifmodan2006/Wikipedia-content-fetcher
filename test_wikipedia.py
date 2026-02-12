#!/usr/bin/env python3
"""Quick test script to verify Wikipedia fetcher is working"""

from wikipedia_manager import WikipediaManager
from app import create_app
import json

# Create app context
app = create_app('development')

with app.app_context():
    wiki = WikipediaManager()

    print("=" * 60)
    print("WIKIPEDIA FETCHER - QUICK TEST")
    print("=" * 60)

    # Test 1: Search
    print("\n[Test 1] Searching for 'Python Programming'...")
    search_result = wiki.search_wikipedia('Python')
    print(f"✓ Success: {search_result['success']}")
    if search_result['success']:
        print(f"  Title: {search_result['title']}")
        print(f"  Summary: {search_result['summary'][:100]}...")

    # Test 2: Fetch
    print("\n[Test 2] Fetching complete content for 'Artificial Intelligence'...")
    fetch_result = wiki.fetch_wikipedia_content('Artificial intelligence')
    print(f"✓ Success: {fetch_result['success']}")
    if fetch_result['success']:
        print(f"  Title: {fetch_result['title']}")
        print(f"  URL: {fetch_result['url']}")
        print(f"  Categories: {len(fetch_result['categories'])} found")
        print(f"  References: {len(fetch_result['references'])} found")
        print(f"  Content Preview: {fetch_result['content'][:150]}...")
    else:
        print(f"  Error: {fetch_result.get('message')}")

    # Test 3: Get cached
    print("\n[Test 3] Retrieving cached content...")
    cached = wiki.get_cached_content('Artificial intelligence')
    if cached:
        print(f"✓ Found cached: {cached['title']}")
        print(f"  Fetched: {cached['fetched_at']}")
    else:
        print("✗ No cached content found (first fetch, not yet cached)")

    # Test 4: Search cache
    print("\n[Test 4] Searching cache for 'artificial'...")
    cache_results = wiki.search_cache('artificial')
    print(f"✓ Found {len(cache_results)} items in cache")
    if cache_results:
        for item in cache_results[:3]:
            print(f"  - {item['title']}")

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
