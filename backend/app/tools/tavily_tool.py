"""
Tavily Web Search Integration for LinkedIn AI Post Automation

This module provides web search capabilities using Tavily API to enhance
content generation with real-time web data and latest information.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TavilySearchTool:
    """Tavily search tool for web research and latest information gathering"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Tavily search client"""
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY")
        self.client = None

        if self.api_key:
            try:
                self.client = TavilyClient(api_key=self.api_key)
                logging.info("Tavily search client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize Tavily client: {e}")
                self.client = None
        else:
            logging.warning("TAVILY_API_KEY not found in environment variables")

    def is_available(self) -> bool:
        """Check if Tavily search is available and configured"""
        return self.client is not None

    def search_web(self, query: str, max_results: int = 7, search_depth: str = "advanced") -> List[Dict[str, Any]]:
        """
        Search the web using Tavily API

        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 7 for "context 7")
            search_depth: Search depth - "basic" or "advanced"

        Returns:
            List of search results with title, content, url, and metadata
        """
        if not self.is_available():
            logging.warning("Tavily search not available - API key not configured")
            return []

        try:
            logging.info(f"Searching web for: {query}")

            # Execute search with Tavily
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                include_images=False,  # Focus on text content
                include_answer=False,  # We want raw results for AI processing
                max_results=max_results
            )

            # Process and structure results
            results = []
            if response and 'results' in response:
                for result in response['results']:
                    processed_result = {
                        'title': result.get('title', ''),
                        'content': result.get('content', ''),
                        'url': result.get('url', ''),
                        'published_date': result.get('published_date', ''),
                        'score': result.get('score', 0),
                        'search_query': query,
                        'searched_at': datetime.now().isoformat()
                    }
                    results.append(processed_result)

            logging.info(f"Found {len(results)} search results for query: {query}")
            return results

        except Exception as e:
            logging.error(f"Tavily search failed for query '{query}': {e}")
            return []

    def search_ai_news(self, topic: str) -> List[Dict[str, Any]]:
        """Search for AI and technology news related to the topic"""
        search_queries = [
            f"latest AI news {topic}",
            f"recent developments in {topic}",
            f"{topic} technology trends 2025",
            f"{topic} AI advancements"
        ]

        all_results = []
        for query in search_queries:
            results = self.search_web(query, max_results=5)
            all_results.extend(results)

        # Remove duplicates and sort by relevance score
        seen_urls = set()
        unique_results = []
        for result in sorted(all_results, key=lambda x: x.get('score', 0), reverse=True):
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)

        return unique_results[:7]  # Return top 7 results

    def search_technical_info(self, topic: str) -> List[Dict[str, Any]]:
        """Search for technical information and best practices"""
        search_queries = [
            f"{topic} best practices",
            f"{topic} tutorial guide",
            f"{topic} implementation examples",
            f"current {topic} standards"
        ]

        all_results = []
        for query in search_queries:
            results = self.search_web(query, max_results=4)
            all_results.extend(results)

        # Remove duplicates and sort by relevance
        seen_urls = set()
        unique_results = []
        for result in sorted(all_results, key=lambda x: x.get('score', 0), reverse=True):
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)

        return unique_results[:7]

    def format_search_results_for_ai(self, results: List[Dict[str, Any]], max_context_length: int = 40000) -> str:
        """
        Format search results for AI consumption

        Args:
            results: List of search results
            max_context_length: Maximum context length to prevent token overflow

        Returns:
            Formatted string containing search results for AI context
        """
        if not results:
            return "No recent web search results available."

        formatted_results = []
        current_length = 0

        for i, result in enumerate(results, 1):
            # Create formatted result entry
            entry = f"""--- SEARCH RESULT {i} ---
                    Title: {result.get('title', 'No title')}
                    URL: {result.get('url', 'No URL')}
                    Published: {result.get('published_date', 'No date')}
                    Relevance Score: {result.get('score', 0):.2f}

                    Content: {result.get('content', 'No content available')}

                    """

            # Check if adding this entry would exceed context limit
            if current_length + len(entry) > max_context_length:
                logging.warning(f"Context limit reached. Stopping at {i-1} results.")
                break

            formatted_results.append(entry)
            current_length += len(entry)

        # Add summary header
        summary = f"""WEB SEARCH RESULTS SUMMARY
Found {len(formatted_results)} relevant results from recent web search.
Use this information to ensure content accuracy and include latest developments.

{''.join(formatted_results)}
--- END OF SEARCH RESULTS ---
"""

        return summary

def create_search_enhanced_prompt(base_prompt: str, search_results: str, topic: str) -> str:
    """
    Create an enhanced prompt that includes web search results

    Args:
        base_prompt: Original prompt without search context
        search_results: Formatted search results
        topic: Original topic for context

    Returns:
        Enhanced prompt with web search context
    """
    enhanced_prompt = f"""{base_prompt}

        IMPORTANT: I have access to recent web search results about "{topic}". Use this latest information to ensure accuracy and relevance:

        {search_results}

        When creating content:
        1. Reference current trends and recent developments when relevant
        2. Include specific facts, statistics, or examples from the search results
        3. Ensure all technical information is up-to-date
        4. If the search results contradict any assumptions, prioritize the web data
        5. Maintain professional tone while incorporating latest insights

        Generate the LinkedIn post using both your knowledge and these current web search results."""

    return enhanced_prompt

# Global search tool instance
tavily_search = TavilySearchTool()
