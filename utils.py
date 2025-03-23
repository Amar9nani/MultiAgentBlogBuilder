import re
import logging
import time
from typing import List, Dict, Any, Tuple
from langchain.prompts import PromptTemplate
import os

logger = logging.getLogger(__name__)

def create_markdown_blog(title: str, sections: List[Dict[str, Any]]) -> str:
    """
    Creates a well-formatted Markdown blog post from a title and sections.
    
    Args:
        title: The blog post title
        sections: List of dictionaries with 'heading', 'subheadings', and 'content'
        
    Returns:
        A formatted Markdown string
    """
    blog_md = f"# {title}\n\n"
    
    for section in sections:
        if 'heading' in section and section['heading']:
            blog_md += f"## {section['heading']}\n\n"
            
        if 'content' in section and section['content']:
            blog_md += f"{section['content']}\n\n"
            
        if 'subheadings' in section and section['subheadings']:
            for subheading in section['subheadings']:
                if 'title' in subheading and subheading['title']:
                    blog_md += f"### {subheading['title']}\n\n"
                    
                if 'content' in subheading and subheading['content']:
                    blog_md += f"{subheading['content']}\n\n"
    
    return blog_md

def count_words(text: str) -> int:
    """
    Count the number of words in a text string.
    
    Args:
        text: The input text
        
    Returns:
        Word count as an integer
    """
    return len(re.findall(r'\b\w+\b', text))

def calculate_keyword_density(text: str, keywords: List[str]) -> float:
    """
    Calculate keyword density in a text.
    
    Args:
        text: The text to analyze
        keywords: List of keywords to check
        
    Returns:
        Keyword density as a float
    """
    if not keywords or not text:
        return 0.0
        
    word_count = count_words(text)
    if word_count == 0:
        return 0.0
        
    keyword_count = 0
    text_lower = text.lower()
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        keyword_count += len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', text_lower))
    
    return keyword_count / word_count

def extract_keywords_from_text(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract potential keywords from text based on frequency.
    
    Args:
        text: The text to analyze
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of potential keywords
    """
    # Remove common stop words
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
        'to', 'of', 'in', 'for', 'with', 'on', 'at', 'by', 'from', 'about',
        'as', 'into', 'like', 'through', 'after', 'over', 'between', 'out',
        'this', 'that', 'these', 'those', 'there', 'here', 'how', 'why',
        'when', 'where', 'who', 'whom', 'which', 'what', 'would', 'could',
        'should', 'will', 'shall', 'may', 'might', 'must', 'can', 'then'
    }
    
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = {}
    
    for word in words:
        if len(word) > 3 and word not in stop_words:
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Return top keywords
    return [word for word, freq in sorted_words[:max_keywords]]

def retry_with_exponential_backoff(func, max_retries=5, initial_delay=1, exponential_base=2, jitter=True):
    """
    Decorator for implementing retry logic with exponential backoff.
    
    Args:
        func: The function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries in seconds
        exponential_base: Base of the exponential backoff
        jitter: Whether to add random jitter to the delay time
        
    Returns:
        The decorated function
    """
    import random
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        num_retries = 0
        delay = initial_delay
        
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                num_retries += 1
                if num_retries > max_retries:
                    logger.error(f"Maximum retries ({max_retries}) exceeded. Last error: {str(e)}")
                    raise
                
                # Calculate delay with optional jitter
                if jitter:
                    delay = delay * exponential_base * (1 + random.random())
                else:
                    delay = delay * exponential_base
                    
                logger.warning(f"Retry {num_retries}/{max_retries} after error: {str(e)}. Waiting {delay:.2f} seconds...")
                time.sleep(delay)
    
    return wrapper

def get_env_variable(name: str, default: str = "") -> str:
    """
    Get environment variable or return default value.
    
    Args:
        name: Name of the environment variable
        default: Default value if environment variable is not set
        
    Returns:
        The value of the environment variable or the default
    """
    return os.environ.get(name, default)

def split_text_into_chunks(text: str, max_tokens: int = 4000, overlap: int = 200) -> List[str]:
    """
    Split text into chunks respecting token limits.
    
    Args:
        text: The text to split
        max_tokens: Maximum tokens per chunk (approximately 4 chars per token)
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Approximate tokens by characters (4 chars ~= 1 token)
    max_chars = max_tokens * 4
    
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chars
        
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        # Try to find a good breaking point (paragraph or sentence)
        paragraph_break = text.rfind('\n\n', start, end)
        sentence_break = text.rfind('. ', start, end)
        
        if paragraph_break > start + (max_chars // 2):
            # Break at paragraph if it's reasonably far into the chunk
            end = paragraph_break + 2
        elif sentence_break > start + (max_chars // 3):
            # Break at sentence if it's reasonably far into the chunk
            end = sentence_break + 2
        else:
            # Fall back to word boundary
            space_position = text.rfind(' ', start, end)
            if space_position > start:
                end = space_position + 1
        
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks
