"""
Search and research tools for the Deep Researcher Agent
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Represents a search result"""
    title: str
    url: str
    snippet: str
    relevance_score: float = 0.0

class GoogleSearchTool:
    """Google Search tool for external research"""
    
    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """
        Perform Google search for the given query
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            if not self.api_key or not self.search_engine_id:
                logger.warning("Google Search API not configured, returning mock results")
                return self._mock_search_results(query, num_results)
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)  # Google API limit
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('snippet', ''),
                    relevance_score=1.0  # Could implement relevance scoring
                )
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return self._mock_search_results(query, num_results)
    
    def _mock_search_results(self, query: str, num_results: int) -> List[SearchResult]:
        """Generate mock search results for testing/fallback"""
        mock_results = [
            SearchResult(
                title=f"Industry Best Practices for {query}",
                url="https://example.com/best-practices",
                snippet=f"Comprehensive guide to {query} implementation and industry standards...",
                relevance_score=0.9
            ),
            SearchResult(
                title=f"Market Analysis: {query} Solutions",
                url="https://example.com/market-analysis",
                snippet=f"Current market trends and pricing for {query} technologies...",
                relevance_score=0.8
            ),
            SearchResult(
                title=f"Technical Documentation: {query}",
                url="https://example.com/tech-docs",
                snippet=f"Technical specifications and implementation details for {query}...",
                relevance_score=0.7
            )
        ]
        
        return mock_results[:num_results]

class TechnologyResearchTool:
    """Tool for researching specific technologies and their market context"""
    
    def __init__(self, search_tool: GoogleSearchTool):
        self.search_tool = search_tool
        
    def research_technology(self, technology: str) -> Dict[str, Any]:
        """
        Research a specific technology mentioned in the RFP
        
        Args:
            technology: Technology name to research
            
        Returns:
            Dictionary with research findings
        """
        try:
            # Search for technology information
            search_queries = [
                f"{technology} best practices implementation",
                f"{technology} market rates pricing",
                f"{technology} security considerations",
                f"{technology} scalability performance"
            ]
            
            research_data = {
                'technology': technology,
                'best_practices': [],
                'market_info': [],
                'security_considerations': [],
                'performance_notes': []
            }
            
            for query in search_queries:
                results = self.search_tool.search(query, num_results=3)
                
                if 'best practices' in query:
                    research_data['best_practices'].extend([r.snippet for r in results])
                elif 'market rates' in query:
                    research_data['market_info'].extend([r.snippet for r in results])
                elif 'security' in query:
                    research_data['security_considerations'].extend([r.snippet for r in results])
                elif 'scalability' in query:
                    research_data['performance_notes'].extend([r.snippet for r in results])
            
            return research_data
            
        except Exception as e:
            logger.error(f"Technology research failed for {technology}: {e}")
            return {
                'technology': technology,
                'best_practices': [f"Standard implementation practices for {technology}"],
                'market_info': [f"Competitive market rates for {technology} development"],
                'security_considerations': [f"Standard security practices for {technology}"],
                'performance_notes': [f"Scalability considerations for {technology}"]
            }

class ClientResearchTool:
    """Tool for researching client background and industry context"""
    
    def __init__(self, search_tool: GoogleSearchTool):
        self.search_tool = search_tool
        
    def research_client(self, client_name: str, industry: str = "") -> Dict[str, Any]:
        """
        Research client background and industry context
        
        Args:
            client_name: Name of the client organization
            industry: Industry sector (if known)
            
        Returns:
            Dictionary with client research findings
        """
        try:
            search_queries = [
                f"{client_name} company background",
                f"{client_name} technology stack",
                f"{industry} industry standards" if industry else "enterprise technology trends"
            ]
            
            client_data = {
                'client_name': client_name,
                'industry': industry,
                'background': [],
                'tech_preferences': [],
                'industry_context': []
            }
            
            for query in search_queries:
                results = self.search_tool.search(query, num_results=2)
                
                if 'background' in query:
                    client_data['background'].extend([r.snippet for r in results])
                elif 'technology stack' in query:
                    client_data['tech_preferences'].extend([r.snippet for r in results])
                elif 'industry' in query:
                    client_data['industry_context'].extend([r.snippet for r in results])
            
            return client_data
            
        except Exception as e:
            logger.error(f"Client research failed for {client_name}: {e}")
            return {
                'client_name': client_name,
                'industry': industry,
                'background': [f"Established organization in {industry} sector"],
                'tech_preferences': ["Modern technology stack preferences"],
                'industry_context': [f"Standard practices in {industry} industry"]
            }

# Factory function to create search tools
def create_search_tools(google_api_key: Optional[str] = None, 
                       search_engine_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create and configure search tools
    
    Args:
        google_api_key: Google Custom Search API key
        search_engine_id: Google Custom Search Engine ID
        
    Returns:
        Dictionary of configured search tools
    """
    google_search = GoogleSearchTool(google_api_key, search_engine_id)
    
    return {
        'google_search': google_search,
        'technology_research': TechnologyResearchTool(google_search),
        'client_research': ClientResearchTool(google_search)
    }