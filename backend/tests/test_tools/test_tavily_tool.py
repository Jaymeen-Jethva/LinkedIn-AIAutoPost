#!/usr/bin/env python3
"""
Test script for Tavily web search integration
"""

import os
from tavily_search import tavily_search

def test_tavily_search():
    """Test basic Tavily search functionality"""

    print("🔍 Testing Tavily Web Search Integration")
    print("=" * 50)

    # Check if Tavily is available
    if not tavily_search.is_available():
        print("❌ Tavily search not available - TAVILY_API_KEY not found in environment")
        print("Please add TAVILY_API_KEY to your .env file to enable web search")
        return False

    print("✅ Tavily search is available")

    # Test basic search
    print("\n🧪 Testing basic web search...")
    try:
        results = tavily_search.search_web("latest AI developments 2025", max_results=3)
        if results:
            print(f"✅ Found {len(results)} search results")
            for i, result in enumerate(results[:2], 1):  # Show first 2 results
                print(f"\nResult {i}:")
                print(f"  Title: {result.get('title', 'No title')}")
                print(f"  URL: {result.get('url', 'No URL')}")
                print(f"  Score: {result.get('score', 0):.2f}")
        else:
            print("❌ No search results found")
            return False
    except Exception as e:
        print(f"❌ Basic search failed: {e}")
        return False

    # Test AI news search
    print("\n🧪 Testing AI news search...")
    try:
        ai_results = tavily_search.search_ai_news("quantum computing")
        if ai_results:
            print(f"✅ Found {len(ai_results)} AI news results")
            print(f"Top result: {ai_results[0].get('title', 'No title')}")
        else:
            print("❌ No AI news results found")
    except Exception as e:
        print(f"❌ AI news search failed: {e}")
        return False

    # Test technical info search
    print("\n🧪 Testing technical info search...")
    try:
        tech_results = tavily_search.search_technical_info("machine learning best practices")
        if tech_results:
            print(f"✅ Found {len(tech_results)} technical results")
            print(f"Top result: {tech_results[0].get('title', 'No title')}")
        else:
            print("❌ No technical results found")
    except Exception as e:
        print(f"❌ Technical search failed: {e}")
        return False

    # Test search result formatting
    print("\n🧪 Testing search result formatting...")
    try:
        formatted = tavily_search.format_search_results_for_ai(results[:2])
        if formatted and len(formatted) > 100:
            print("✅ Search results formatted successfully")
            print(f"Formatted length: {len(formatted)} characters")
        else:
            print("❌ Search result formatting failed")
            return False
    except Exception as e:
        print(f"❌ Formatting failed: {e}")
        return False

    print("\n🎉 All Tavily search tests passed!")
    print("Web search integration is working correctly.")
    return True

if __name__ == "__main__":
    success = test_tavily_search()
    exit(0 if success else 1)
