import logging
import random
import time
from typing import Dict, List, Tuple, Optional, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import json

from web_scraper import search_web, get_website_text_content, search_latest_hr_trends, scrape_multiple_sources
from config import Config
from utils import extract_keywords_from_text, split_text_into_chunks

logger = logging.getLogger(__name__)

class ResearchAgent:
    """Agent responsible for researching HR topics and gathering relevant information."""
    
    def __init__(self):
        """Initialize the Research Agent with necessary tools and LLM."""
        self.config = Config()
        
        # Initialize language model
        try:
            self.llm = ChatOpenAI(
                model_name=self.config.DEFAULT_MODEL,
                temperature=0.3,
                max_tokens=1000,
                api_key=self.config.OPENAI_API_KEY
            )
            logger.info("Research Agent initialized with primary model")
        except Exception as e:
            logger.warning(f"Failed to initialize primary model: {str(e)}. Using fallback model.")
            self.llm = ChatOpenAI(
                model_name=self.config.FALLBACK_MODEL,
                temperature=0.3,
                max_tokens=1000,
                api_key=self.config.OPENAI_API_KEY
            )
        
        # Define prompt templates
        self.trend_analysis_prompt = PromptTemplate(
            template="""You are a professional HR researcher. Based on the following information about current HR trends, 
            identify the most interesting and relevant trending topic that would make for an engaging HR blog post. 
            Choose a specific topic rather than a broad area, and make sure it's relevant to current HR professionals.
            
            Current HR Trend Information:
            {trend_data}
            
            Return ONLY the topic name without any additional text or explanation.
            """,
            input_variables=["trend_data"]
        )
        
        self.research_synthesis_prompt = PromptTemplate(
            template="""You are a professional HR researcher. Based on the following information about the HR topic "{topic}", 
            synthesize the most important points, statistics, insights, and trends into a comprehensive research summary.
            
            Research Data:
            {research_data}
            
            Your summary should:
            1. Identify key trends and patterns
            2. Highlight important statistics and data points
            3. Note conflicting viewpoints or approaches if present
            4. Include any relevant case studies or examples
            5. Consider implications for HR professionals
            
            Focus on factual information and insights that would be valuable for writing an SEO-optimized blog post on this topic.
            If keyword suggestions are provided, incorporate relevant information about these keywords: {keywords}
            
            Format your response as detailed research notes that will be used to create a blog outline.
            """,
            input_variables=["topic", "research_data", "keywords"]
        )
        
        # Create chains
        self.trend_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.trend_analysis_prompt
        )
        
        self.research_synthesis_chain = LLMChain(
            llm=self.llm,
            prompt=self.research_synthesis_prompt
        )
        
        logger.info("Research Agent initialized successfully")
    
    def find_trending_topic(self) -> Tuple[str, Dict[str, Any]]:
        """
        Find a trending HR topic and gather research about it.
        
        Returns:
            tuple: (topic name, research data dictionary)
        """
        logger.info("Searching for trending HR topics")
        
        try:
            # Search for latest HR trends
            trend_results = search_latest_hr_trends()
            
            if not trend_results:
                logger.warning("No trend results found. Using fallback topic.")
                selected_topic = random.choice(self.config.FALLBACK_HR_TOPICS)
                return selected_topic, self.research_topic(selected_topic)
            
            # Scrape content from top results
            trend_urls = [result['link'] for result in trend_results[:5]]
            scraped_data = scrape_multiple_sources(trend_urls)
            
            # Combine scraped content
            combined_trend_data = "\n\n".join([f"Source: {url}\n{content[:3000]}" for url, content in scraped_data])
            
            # Use LLM to analyze trends and suggest a topic
            selected_topic = self.trend_analysis_chain.run(trend_data=combined_trend_data).strip()
            
            logger.info(f"Selected trending topic: {selected_topic}")
            
            # Research the selected topic
            research_data = self.research_topic(selected_topic)
            
            return selected_topic, research_data
            
        except Exception as e:
            logger.error(f"Error finding trending topic: {str(e)}", exc_info=True)
            selected_topic = random.choice(self.config.FALLBACK_HR_TOPICS)
            return selected_topic, self.research_topic(selected_topic)
    
    def research_topic(self, topic: str, keywords: str = "") -> Dict[str, Any]:
        """
        Research a specific HR topic thoroughly.
        
        Args:
            topic: The HR topic to research
            keywords: Optional keywords to include in search
            
        Returns:
            Dictionary with research data
        """
        logger.info(f"Researching topic: {topic}")
        
        # Prepare search query
        search_query = topic
        if keywords:
            search_query = f"{topic} {keywords}"
        
        # Search the web for information
        search_results = search_web(search_query, num_results=self.config.MAX_RESEARCH_SOURCES)
        logger.info(f"Found {len(search_results)} search results for {topic}")
        
        # Scrape content from search results
        urls = [result['link'] for result in search_results]
        scraped_data = scrape_multiple_sources(urls)
        
        # Combine research data
        combined_research = ""
        source_metadata = []
        
        for url, content in scraped_data:
            if content:
                truncated_content = content[:5000]  # Limit content length
                combined_research += f"\n\nSOURCE: {url}\n{truncated_content}\n"
                
                # Extract keywords for SEO purposes
                extracted_keywords = extract_keywords_from_text(content, max_keywords=5)
                
                source_metadata.append({
                    "url": url,
                    "content_length": len(content),
                    "extracted_keywords": extracted_keywords
                })
        
        # If we have a large amount of research, we need to split it up for the LLM
        research_chunks = split_text_into_chunks(combined_research)
        synthesized_research = ""
        
        for i, chunk in enumerate(research_chunks):
            logger.info(f"Processing research chunk {i+1}/{len(research_chunks)}")
            chunk_synthesis = self.research_synthesis_chain.run(
                topic=topic,
                research_data=chunk,
                keywords=keywords
            )
            synthesized_research += chunk_synthesis + "\n\n"
            time.sleep(1)  # Avoid rate limiting
        
        # Compile research data
        research_data = {
            "topic": topic,
            "keywords": keywords,
            "synthesized_research": synthesized_research,
            "source_metadata": source_metadata,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"Completed research for topic: {topic}")
        return research_data
