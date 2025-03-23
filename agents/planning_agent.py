import logging
import time
from typing import Dict, List, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json

from config import Config
from utils import extract_keywords_from_text

logger = logging.getLogger(__name__)

class PlanningAgent:
    """Agent responsible for creating a structured outline for the blog post."""
    
    def __init__(self):
        """Initialize the Planning Agent with necessary tools and LLM."""
        self.config = Config()
        
        # Initialize language model
        try:
            self.llm = ChatOpenAI(
                model_name=self.config.DEFAULT_MODEL,
                temperature=0.3,
                max_tokens=1000,
                api_key=self.config.OPENAI_API_KEY
            )
            logger.info("Planning Agent initialized with primary model")
        except Exception as e:
            logger.warning(f"Failed to initialize primary model: {str(e)}. Using fallback model.")
            self.llm = ChatOpenAI(
                model_name=self.config.FALLBACK_MODEL,
                temperature=0.3,
                max_tokens=1000,
                api_key=self.config.OPENAI_API_KEY
            )
        
        # Define prompt template for outline creation
        self.outline_prompt = PromptTemplate(
            template="""You are a professional content strategist for a popular HR blog. You need to create a detailed, 
            SEO-optimized outline for a blog post on the topic: "{topic}".
            
            Use the following research data to inform your outline:
            {research_data}
            
            Target keywords to incorporate: {keywords}
            
            Your outline should:
            1. Include a compelling, SEO-friendly title
            2. Have an introduction section
            3. Include 5-7 main sections with clear headings
            4. Each main section should have 2-3 subheadings
            5. Include a conclusion section
            6. Have a logical flow that builds understanding of the topic
            7. Target approximately 2000 words total
            
            The outline should be structured enough to guide a writer but allow for creativity.
            
            Return the outline as a JSON object with the following structure:
            {{
                "title": "The SEO-optimized title",
                "target_keywords": ["keyword1", "keyword2", ...],
                "estimated_word_count": 2000,
                "sections": [
                    {{
                        "heading": "Introduction",
                        "subheadings": [],
                        "key_points": ["point1", "point2", ...],
                        "target_word_count": 200
                    }},
                    {{
                        "heading": "Main Section 1",
                        "subheadings": [
                            {{
                                "title": "Subheading 1.1",
                                "key_points": ["point1", "point2", ...],
                                "target_word_count": 150
                            }},
                            ...
                        ],
                        "key_points": ["point1", "point2", ...],
                        "target_word_count": 300
                    }},
                    ...
                    {{
                        "heading": "Conclusion",
                        "subheadings": [],
                        "key_points": ["point1", "point2", ...],
                        "target_word_count": 200
                    }}
                ]
            }}
            """,
            input_variables=["topic", "research_data", "keywords"]
        )
        
        # Create outline creation chain
        self.outline_chain = LLMChain(
            llm=self.llm,
            prompt=self.outline_prompt
        )
        
        logger.info("Planning Agent initialized successfully")
    
    def create_outline(self, topic: str, research_data: Dict[str, Any], keywords: str = "") -> Dict[str, Any]:
        """
        Create a structured outline for a blog post based on research data.
        
        Args:
            topic: The blog topic
            research_data: Dictionary with research information
            keywords: Optional target keywords
            
        Returns:
            Dictionary with outline structure
        """
        logger.info(f"Creating outline for topic: {topic}")
        
        # Extract synthesized research from research data
        synthesized_research = research_data.get("synthesized_research", "")
        
        # If no keywords provided, extract some from the research
        if not keywords and "source_metadata" in research_data:
            # Gather keywords from all sources
            all_keywords = []
            for source in research_data["source_metadata"]:
                if "extracted_keywords" in source:
                    all_keywords.extend(source["extracted_keywords"])
            
            # Count frequency
            keyword_freq = {}
            for keyword in all_keywords:
                if keyword in keyword_freq:
                    keyword_freq[keyword] += 1
                else:
                    keyword_freq[keyword] = 1
            
            # Sort by frequency
            sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
            extracted_keywords = [keyword for keyword, _ in sorted_keywords[:5]]
            keywords = ", ".join(extracted_keywords)
            
            logger.info(f"Extracted keywords for SEO: {keywords}")
        
        try:
            # Generate the outline
            outline_json_str = self.outline_chain.run(
                topic=topic,
                research_data=synthesized_research,
                keywords=keywords
            )
            
            # Parse JSON response
            try:
                outline = json.loads(outline_json_str)
                logger.info(f"Successfully created outline with {len(outline.get('sections', []))} sections")
                return outline
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing outline JSON: {str(e)}")
                
                # Try to fix common JSON issues
                cleaned_json = outline_json_str.strip()
                # Remove any markdown code block syntax
                if cleaned_json.startswith("```json"):
                    cleaned_json = cleaned_json[7:]
                if cleaned_json.endswith("```"):
                    cleaned_json = cleaned_json[:-3]
                
                cleaned_json = cleaned_json.strip()
                
                try:
                    outline = json.loads(cleaned_json)
                    logger.info("Successfully parsed outline JSON after cleaning")
                    return outline
                except json.JSONDecodeError:
                    logger.error("Failed to parse outline JSON even after cleaning")
                    
                    # Create a basic fallback outline
                    fallback_outline = {
                        "title": f"{topic}: A Comprehensive Guide",
                        "target_keywords": keywords.split(", ") if keywords else [],
                        "estimated_word_count": 2000,
                        "sections": [
                            {
                                "heading": "Introduction",
                                "subheadings": [],
                                "key_points": ["Introduction to the topic", "Why it matters", "What will be covered"],
                                "target_word_count": 200
                            },
                            {
                                "heading": f"Understanding {topic}",
                                "subheadings": [
                                    {
                                        "title": "Key Concepts",
                                        "key_points": ["Important definitions", "Core principles"],
                                        "target_word_count": 250
                                    },
                                    {
                                        "title": "Current Trends",
                                        "key_points": ["Recent developments", "Industry shifts"],
                                        "target_word_count": 250
                                    }
                                ],
                                "key_points": [],
                                "target_word_count": 500
                            },
                            {
                                "heading": "Best Practices",
                                "subheadings": [
                                    {
                                        "title": "Strategies for Implementation",
                                        "key_points": ["Practical approaches", "Step-by-step guidance"],
                                        "target_word_count": 300
                                    },
                                    {
                                        "title": "Common Challenges",
                                        "key_points": ["Potential obstacles", "Solutions"],
                                        "target_word_count": 300
                                    }
                                ],
                                "key_points": [],
                                "target_word_count": 600
                            },
                            {
                                "heading": "Case Studies",
                                "subheadings": [
                                    {
                                        "title": "Success Stories",
                                        "key_points": ["Real-world examples", "Outcomes"],
                                        "target_word_count": 300
                                    }
                                ],
                                "key_points": [],
                                "target_word_count": 300
                            },
                            {
                                "heading": "Future Directions",
                                "subheadings": [],
                                "key_points": ["Emerging trends", "Predictions", "Preparation strategies"],
                                "target_word_count": 200
                            },
                            {
                                "heading": "Conclusion",
                                "subheadings": [],
                                "key_points": ["Summary of key points", "Final thoughts", "Call to action"],
                                "target_word_count": 200
                            }
                        ]
                    }
                    return fallback_outline
                
        except Exception as e:
            logger.error(f"Error creating outline: {str(e)}", exc_info=True)
            raise
