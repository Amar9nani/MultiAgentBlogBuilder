import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # LLM configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    DEFAULT_MODEL = "gpt-3.5-turbo"  # Using a widely available model
    FALLBACK_MODEL = "gpt-3.5-turbo-16k"
    
    # Agent configuration
    MAX_RESEARCH_SOURCES = 5
    CONTENT_MAX_TOKENS = 4096  # For generating content
    CONTENT_TARGET_WORDS = 2000  # Target word count for blog posts
    
    # SEO configuration
    SEO_KEYWORD_DENSITY = 0.02  # Recommended keyword density (2%)
    SEO_MIN_HEADINGS = 5  # Minimum number of headings
    SEO_MAX_PARAGRAPH_LENGTH = 300  # Maximum paragraph length in words
    
    # Logging
    LOG_LEVEL = "DEBUG"
    
    # Web search settings
    SEARCH_API_KEY = os.environ.get("SERPAPI_API_KEY", "")
    SEARCH_ENGINE = "serpapi"  # Can be changed based on availability
    
    # Blog formatting
    BLOG_FORMATS = ["markdown", "html", "txt"]
    DEFAULT_FORMAT = "markdown"
    
    # HR Topics for fallback if research fails
    FALLBACK_HR_TOPICS = [
        "Employee Retention Strategies",
        "Remote Work Best Practices",
        "Diversity and Inclusion in the Workplace",
        "Performance Management Systems",
        "Employee Wellness Programs",
        "HR Technology Trends",
        "Recruitment Automation",
        "Workplace Culture Development",
        "Employee Engagement Strategies",
        "HR Compliance Updates"
    ]
