import logging
import trafilatura
import requests
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
import time
import random
from utils import retry_with_exponential_backoff

logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    Extract clean text content from a website URL.
    
    Args:
        url: The URL to extract content from
        
    Returns:
        Extracted text content
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.warning(f"Failed to download content from {url}")
            return ""
            
        text = trafilatura.extract(downloaded)
        if not text:
            logger.warning(f"Failed to extract text from {url}")
            return ""
            
        return text
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return ""

@retry_with_exponential_backoff
def search_web(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the web for a given query and return results.
    
    Args:
        query: Search query
        num_results: Maximum number of results to return
        
    Returns:
        List of dictionaries with search results
    """
    try:
        # User agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Use a free search endpoint
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=headers)
        
        if response.status_code != 200:
            logger.warning(f"Search request failed with status code {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = []
        
        # Extract search results
        for result in soup.select('div.g')[:num_results]:
            title_element = result.select_one('h3')
            link_element = result.select_one('a')
            snippet_element = result.select_one('div.VwiC3b')
            
            if title_element and link_element and link_element.has_attr('href'):
                title = title_element.text
                link = link_element['href']
                snippet = snippet_element.text if snippet_element else ""
                
                if link.startswith('/url?q='):
                    link = link.split('/url?q=')[1].split('&')[0]
                
                search_results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet
                })
        
        return search_results
    except Exception as e:
        logger.error(f"Error during web search: {str(e)}")
        return []

def search_latest_hr_trends() -> List[Dict[str, str]]:
    """
    Search specifically for the latest HR trends.
    
    Returns:
        List of search results about HR trends
    """
    current_year = time.strftime("%Y")
    queries = [
        f"latest HR trends {current_year}",
        f"human resources challenges {current_year}",
        f"trending topics in HR {current_year}",
        "employee engagement strategies",
        "remote work HR challenges",
        "HR technology innovations"
    ]
    
    all_results = []
    for query in queries:
        results = search_web(query, num_results=3)
        all_results.extend(results)
        time.sleep(2)  # Avoid rate limiting
    
    # Remove duplicates by URL
    unique_results = []
    seen_urls = set()
    
    for result in all_results:
        if result['link'] not in seen_urls:
            unique_results.append(result)
            seen_urls.add(result['link'])
    
    return unique_results[:10]  # Return top 10 unique results

def scrape_multiple_sources(urls: List[str]) -> List[Tuple[str, str]]:
    """
    Scrape content from multiple URLs.
    
    Args:
        urls: List of URLs to scrape
        
    Returns:
        List of tuples with URL and extracted content
    """
    results = []
    
    for url in urls:
        try:
            logger.info(f"Scraping content from {url}")
            content = get_website_text_content(url)
            
            if content:
                results.append((url, content))
                
            # Random delay to be respectful to websites
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
    
    return results
