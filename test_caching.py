#!/usr/bin/env python3
"""
Test script to inspect HTTP caching headers from the Flask server
"""

import requests
import json
from datetime import datetime

def test_debug_endpoint():
    """Test the debug cache endpoint"""
    debug_url = "http://127.0.0.1:8000/api/debug/cache"

    print("\n" + "=" * 80)
    print("Debug Cache Configuration Endpoint")
    print("=" * 80)

    try:
        response = requests.get(debug_url)
        if response.status_code == 200:
            data = response.json()
            print(f"\nCache Enabled: {data.get('cache_enabled')}")
            print(f"Debug Mode: {data.get('debug_mode')}")
            print(f"Disable Cache Flag: {data.get('disable_cache_flag')}")

            print("\nSample Headers that would be sent:")
            for header, value in data.get('sample_headers', {}).items():
                if header in ['Cache-Control', 'Pragma', 'Expires']:
                    print(f"  {header}: {value}")

            print("\nTips:")
            for tip, description in data.get('tips', {}).items():
                print(f"  - {description}")
        else:
            print(f"Debug endpoint returned: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to debug endpoint")


def test_caching():
    """Test HTTP caching behavior"""
    url = "http://127.0.0.1:8000/"

    print("=" * 80)
    print("HTTP Caching Debug Test")
    print("=" * 80)

    # First request
    print("\n1. First Request (should be 200):")
    print("-" * 80)
    try:
        # Test debug endpoint first
        test_debug_endpoint()

        print("\n" + "=" * 80)
        print("Testing Actual HTTP Responses")
        print("=" * 80)

        response1 = requests.get(url)
        print(f"\nStatus Code: {response1.status_code}")
        print(f"\nResponse Headers:")
        for header, value in response1.headers.items():
            if header.lower() in ['etag', 'last-modified', 'cache-control', 'expires', 'pragma', 'date']:
                print(f"  {header}: {value}")

        # Store caching headers for conditional request
        etag = response1.headers.get('ETag')
        last_modified = response1.headers.get('Last-Modified')
        cache_control = response1.headers.get('Cache-Control', '')

        print(f"\n2. Second Request with Conditional Headers:")
        print("-" * 80)

        # Build conditional request headers
        headers = {}
        if etag:
            headers['If-None-Match'] = etag
            print(f"Sending If-None-Match: {etag}")
        if last_modified:
            headers['If-Modified-Since'] = last_modified
            print(f"Sending If-Modified-Since: {last_modified}")

        response2 = requests.get(url, headers=headers)
        print(f"\nStatus Code: {response2.status_code}")
        print(f"Content Length: {len(response2.content)} bytes")

        if response2.status_code == 304:
            print("✓ Browser would use cached version (no content transferred)")
        else:
            print("✓ Full content sent (cache bypassed or disabled)")

        print("\n3. Fresh Request without Conditional Headers:")
        print("-" * 80)
        response3 = requests.get(url)
        print(f"Status Code: {response3.status_code}")
        print(f"Content Length: {len(response3.content)} bytes")

        print("\n" + "=" * 80)
        print("Summary:")
        print("=" * 80)
        print(f"ETag header present: {'Yes' if etag else 'No'}")
        print(f"Last-Modified header present: {'Yes' if last_modified else 'No'}")
        print(f"Cache-Control: {cache_control if cache_control else 'Not set'}")
        print(f"304 responses: {'Working' if response2.status_code == 304 else 'Disabled/Not working'}")

        if 'no-cache' in cache_control.lower() or 'no-store' in cache_control.lower():
            print("\n⚠ Caching is DISABLED (no-cache/no-store in Cache-Control)")
            print("  This means:")
            print("  - Browser won't cache responses")
            print("  - Every request gets fresh content (200 response)")
            print("  - Good for development, bad for production")
        elif response2.status_code == 304:
            print("\n✓ Caching is ENABLED and working properly")
            print("  This means:")
            print("  - First request: 200 with full content")
            print("  - Subsequent requests: 304 with no content (browser uses cache)")
            print("  - Reduces bandwidth and improves performance")

        print("=" * 80)

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server at http://127.0.0.1:8000/")
        print("Make sure the Flask server is running:")
        print("  python3 Dashboard/server.py")
        print("\nOr to disable caching:")
        print("  python3 Dashboard/server.py --no-cache")
        print("  python3 Dashboard/server.py --debug")

if __name__ == '__main__':
    test_caching()
