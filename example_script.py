#!/usr/bin/env python3
"""
Wikipedia Content Fetcher - Simple Example Script

This script demonstrates how to use the Wikipedia Content Fetcher API
to fetch, search, and download Wikipedia content.
"""

import requests
import json
from typing import Optional, Dict, List


class WikipediaFetcher:
    """Simple client for Wikipedia Content Fetcher API"""
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
        }
        if api_key:
            self.headers['X-API-Key'] = api_key
    
    def generate_api_key(self, name: str = "Generated Key") -> Dict:
        """Generate a new API key"""
        response = requests.post(
            f"{self.base_url}/api/keys/generate",
            headers={'Content-Type': 'application/json'},
            json={'name': name}
        )
        return response.json()
    
    def list_api_keys(self) -> Dict:
        """List all API keys"""
        response = requests.get(f"{self.base_url}/api/keys/list")
        return response.json()
    
    def search_wikipedia(self, topic: str) -> Dict:
        """Search for a topic on Wikipedia"""
        if not self.api_key:
            return {'success': False, 'error': 'API key required'}
        
        response = requests.post(
            f"{self.base_url}/api/wikipedia/search",
            headers=self.headers,
            json={'topic': topic}
        )
        return response.json()
    
    def fetch_wikipedia_content(self, topic: str) -> Dict:
        """Fetch complete Wikipedia content for a topic"""
        if not self.api_key:
            return {'success': False, 'error': 'API key required'}
        
        response = requests.post(
            f"{self.base_url}/api/wikipedia/fetch",
            headers=self.headers,
            json={'topic': topic}
        )
        return response.json()
    
    def get_cached_content(self, topic: str) -> Dict:
        """Get cached content for a topic"""
        if not self.api_key:
            return {'success': False, 'error': 'API key required'}
        
        response = requests.get(
            f"{self.base_url}/api/wikipedia/cached/{topic}",
            headers=self.headers
        )
        return response.json()
    
    def search_cache(self, query: str = "") -> Dict:
        """Search cached Wikipedia content"""
        if not self.api_key:
            return {'success': False, 'error': 'API key required'}
        
        params = {'q': query} if query else {}
        response = requests.get(
            f"{self.base_url}/api/wikipedia/cache/search",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def download_content(self, content_id: int, format_type: str = 'pdf') -> bytes:
        """Download cached content in specified format"""
        if not self.api_key:
            return b''
        
        response = requests.get(
            f"{self.base_url}/api/wikipedia/download/{content_id}",
            headers=self.headers,
            params={'format': format_type}
        )
        return response.content


def print_result(result: Dict, show_full: bool = False):
    """Pretty print API result"""
    if result.get('success'):
        print("✓ Success!")
        if show_full:
            print(json.dumps(result, indent=2))
        else:
            # Print summary
            if 'title' in result:
                print(f"  Title: {result['title']}")
            if 'url' in result:
                print(f"  URL: {result['url']}")
            if 'summary' in result:
                print(f"  Summary: {result['summary'][:200]}...")
            if 'categories' in result and result['categories']:
                print(f"  Categories: {', '.join(result['categories'][:5])}")
    else:
        print("✗ Failed!")
        print(f"  Error: {result.get('error') or result.get('message')}")


def example_workflow():
    """Demonstrate the basic workflow"""
    
    print("=" * 60)
    print("Wikipedia Content Fetcher - Example Workflow")
    print("=" * 60)
    
    # Step 1: Generate API Key
    print("\n[Step 1] Generating API Key...")
    fetcher_client = WikipediaFetcher()
    key_result = fetcher_client.generate_api_key("Example Script Key")
    
    if key_result.get('success'):
        api_key = key_result['data']['key']
        print(f"✓ Generated API Key: {api_key}")
        
        # Update fetcher with API key
        fetcher = WikipediaFetcher(api_key=api_key)
    else:
        print("✗ Failed to generate API key")
        return
    
    # Step 2: Search Wikipedia
    print("\n[Step 2] Searching Wikipedia for 'Python'...")
    search_result = fetcher.search_wikipedia("Python")
    print_result(search_result)
    
    # Step 3: Fetch Complete Content
    print("\n[Step 3] Fetching complete content for 'Python'...")
    fetch_result = fetcher.fetch_wikipedia_content("Python")
    print_result(fetch_result, show_full=False)
    
    # Step 4: Search Cached Content
    print("\n[Step 4] Searching cached content...")
    cache_result = fetcher.search_cache("python")
    if cache_result.get('success'):
        print(f"✓ Found {cache_result['count']} cached items")
        if cache_result['data']:
            for item in cache_result['data'][:3]:
                print(f"  - {item['title']}")
    else:
        print(f"✗ Error: {cache_result.get('error')}")
    
    # Step 5: Download Content
    print("\n[Step 5] Example download commands...")
    if cache_result.get('success') and cache_result['data']:
        content_id = cache_result['data'][0]['id']
        print(f"To download content ID {content_id}:")
        print(f"  fetcher.download_content({content_id}, 'pdf')")
        print(f"  fetcher.download_content({content_id}, 'markdown')")
        print(f"  fetcher.download_content({content_id}, 'text')")
    
    print("\n" + "=" * 60)
    print("Workflow completed!")
    print("=" * 60)


def interactive_mode():
    """Interactive mode for exploring the API"""
    
    print("=" * 60)
    print("Wikipedia Content Fetcher - Interactive Mode")
    print("=" * 60)
    
    # Generate API key
    print("\n[1] Generating API Key...")
    fetcher_client = WikipediaFetcher()
    key_result = fetcher_client.generate_api_key("Interactive Session")
    
    if not key_result.get('success'):
        print("Failed to generate API key")
        return
    
    api_key = key_result['data']['key']
    print(f"API Key: {api_key}\n")
    
    fetcher = WikipediaFetcher(api_key=api_key)
    
    # Interactive loop
    while True:
        print("\nOptions:")
        print("1. Search Wikipedia")
        print("2. Fetch Content")
        print("3. View Cached Content")
        print("4. Search Cache")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            topic = input("Enter topic to search: ").strip()
            if topic:
                result = fetcher.search_wikipedia(topic)
                print_result(result)
        
        elif choice == '2':
            topic = input("Enter topic to fetch: ").strip()
            if topic:
                result = fetcher.fetch_wikipedia_content(topic)
                if result.get('success'):
                    print("✓ Content fetched successfully!")
                    print(f"  Title: {result['title']}")
                    print(f"  Categories: {len(result.get('categories', []))}")
                    print(f"  References: {len(result.get('references', []))}")
                else:
                    print(f"✗ Error: {result.get('message')}")
        
        elif choice == '3':
            topic = input("Enter topic: ").strip()
            if topic:
                result = fetcher.get_cached_content(topic)
                print_result(result)
        
        elif choice == '4':
            query = input("Enter search query (or leave empty for all): ").strip()
            result = fetcher.search_cache(query)
            if result.get('success'):
                print(f"✓ Found {result['count']} cached items:")
                for item in result.get('data', []):
                    print(f"  - {item['title']} (ID: {item['id']})")
            else:
                print(f"✗ Error: {result.get('error')}")
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid option")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_mode()
    else:
        example_workflow()
