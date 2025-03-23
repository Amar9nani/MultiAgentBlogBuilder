import logging
import re
from typing import Dict, List, Any, Tuple
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json

from config import Config
from utils import calculate_keyword_density, count_words

logger = logging.getLogger(__name__)

class SeoAgent:
    """Agent responsible for optimizing content for search engines."""
    
    def __init__(self):
        """Initialize the SEO Agent with necessary tools and LLM."""
        self.config = Config()
        
        # Initialize language model
        try:
            self.llm = ChatOpenAI(
                model_name=self.config.DEFAULT_MODEL,
                temperature=0.3,
                max_tokens=1000,
                api_key=self.config.OPENAI_API_KEY
            )
            logger.info("SEO Agent initialized with primary model")
        except Exception as e:
            logger.warning(f"Failed to initialize primary model: {str(e)}. Using fallback model.")
            self.llm = ChatOpenAI(
                model_name=self.config.FALLBACK_MODEL,
                temperature=0.3,
                max_tokens=1000,
                api_key=self.config.OPENAI_API_KEY
            )
        
        # Define prompt template for SEO optimization
        self.seo_optimization_prompt = PromptTemplate(
            template="""You are a professional SEO expert specializing in HR content. Optimize the following blog content 
            for search engines while maintaining readability and natural flow.
            
            Blog Topic: {topic}
            Target Keywords: {keywords}
            
            Original Content:
            {content}
            
            SEO Optimization Guidelines:
            1. Ensure appropriate keyword density (around 1-2% for primary keywords)
            2. Add appropriate internal linking suggestions (indicated with [INTERNAL LINK SUGGESTION: anchor text | topic])
            3. Optimize headings with keywords (H1, H2, H3 tags)
            4. Improve meta description and title if provided
            5. Add suitable alt text suggestions for any image placeholders
            6. Ensure paragraphs are an appropriate length for readability
            7. Use bullet points, numbered lists, or tables where appropriate
            8. Add schema markup suggestions if relevant
            
            Based on the SEO analysis, enhance the content to improve its search engine ranking while maintaining high quality.
            Return the fully optimized content in markdown format.
            """,
            input_variables=["topic", "keywords", "content"]
        )
        
        # Define prompt template for SEO analysis
        self.seo_analysis_prompt = PromptTemplate(
            template="""You are a professional SEO expert specializing in HR content. Analyze the following blog content 
            and provide an SEO assessment and recommendations.
            
            Blog Topic: {topic}
            Target Keywords: {keywords}
            
            Content to Analyze:
            {content}
            
            Provide an analysis including:
            1. Current keyword density and distribution
            2. Heading structure assessment
            3. Content length evaluation
            4. Readability assessment
            5. Specific recommendations for improvement
            
            Format your response as a JSON object with the following structure:
            {{
                "keyword_analysis": {{
                    "primary_keyword_density": 0.0,
                    "keyword_distribution": "description",
                    "suggestions": ["suggestion1", "suggestion2"]
                }},
                "structure_analysis": {{
                    "heading_quality": "description",
                    "content_organization": "description",
                    "suggestions": ["suggestion1", "suggestion2"]
                }},
                "content_quality": {{
                    "readability_score": "description",
                    "content_depth": "description",
                    "suggestions": ["suggestion1", "suggestion2"]
                }},
                "overall_score": 0-100,
                "priority_improvements": ["improvement1", "improvement2"]
            }}
            """,
            input_variables=["topic", "keywords", "content"]
        )
        
        # Create chains
        self.seo_optimization_chain = LLMChain(
            llm=self.llm,
            prompt=self.seo_optimization_prompt
        )
        
        self.seo_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.seo_analysis_prompt
        )
        
        logger.info("SEO Agent initialized successfully")
    
    def analyze_seo(self, content: str, topic: str, keywords: str = "") -> Dict[str, Any]:
        """
        Analyze content for SEO performance.
        
        Args:
            content: The blog content to analyze
            topic: The blog topic
            keywords: Target keywords
            
        Returns:
            Dictionary with SEO analysis
        """
        logger.info(f"Analyzing SEO for content about {topic}")
        
        try:
            # Run basic keyword analysis
            keyword_list = [kw.strip() for kw in keywords.split(",")] if keywords else []
            keyword_density = calculate_keyword_density(content, keyword_list) if keyword_list else 0
            
            # Run LLM analysis
            analysis_json_str = self.seo_analysis_chain.run(
                topic=topic,
                keywords=keywords,
                content=content
            )
            
            # Parse JSON response
            try:
                analysis = json.loads(analysis_json_str)
                logger.info(f"Successfully completed SEO analysis with score {analysis.get('overall_score', 'N/A')}")
                
                # Add calculated keyword density
                if "keyword_analysis" in analysis:
                    analysis["keyword_analysis"]["calculated_keyword_density"] = keyword_density
                
                return analysis
            
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing SEO analysis JSON: {str(e)}")
                
                # Try to fix common JSON issues
                cleaned_json = analysis_json_str.strip()
                # Remove any markdown code block syntax
                if cleaned_json.startswith("```json"):
                    cleaned_json = cleaned_json[7:]
                if cleaned_json.endswith("```"):
                    cleaned_json = cleaned_json[:-3]
                
                cleaned_json = cleaned_json.strip()
                
                try:
                    analysis = json.loads(cleaned_json)
                    logger.info("Successfully parsed SEO analysis JSON after cleaning")
                    
                    # Add calculated keyword density
                    if "keyword_analysis" in analysis:
                        analysis["keyword_analysis"]["calculated_keyword_density"] = keyword_density
                    
                    return analysis
                    
                except json.JSONDecodeError:
                    logger.error("Failed to parse SEO analysis JSON even after cleaning")
                    
                    # Return a basic fallback analysis
                    return {
                        "keyword_analysis": {
                            "primary_keyword_density": keyword_density,
                            "keyword_distribution": "Unable to assess",
                            "suggestions": ["Ensure keywords are distributed throughout the content"]
                        },
                        "structure_analysis": {
                            "heading_quality": "Unable to assess",
                            "content_organization": "Unable to assess",
                            "suggestions": ["Review heading structure", "Ensure logical content flow"]
                        },
                        "content_quality": {
                            "readability_score": "Unable to assess",
                            "content_depth": f"Content contains {count_words(content)} words",
                            "suggestions": ["Ensure content is comprehensive", "Check for readability"]
                        },
                        "overall_score": 50,
                        "priority_improvements": ["Optimize keyword usage", "Review content structure"]
                    }
        
        except Exception as e:
            logger.error(f"Error analyzing SEO: {str(e)}", exc_info=True)
            
            # Return a fallback analysis
            return {
                "keyword_analysis": {
                    "primary_keyword_density": keyword_density if keyword_list else 0,
                    "keyword_distribution": "Error in analysis",
                    "suggestions": ["Review keyword usage manually"]
                },
                "structure_analysis": {
                    "heading_quality": "Error in analysis",
                    "content_organization": "Error in analysis",
                    "suggestions": ["Review heading structure manually"]
                },
                "content_quality": {
                    "readability_score": "Error in analysis",
                    "content_depth": f"Content contains {count_words(content)} words",
                    "suggestions": ["Review content manually"]
                },
                "overall_score": 0,
                "priority_improvements": ["Retry SEO analysis"]
            }
    
    def optimize_content(self, content: str, topic: str, keywords: str = "") -> str:
        """
        Optimize content for SEO.
        
        Args:
            content: The blog content to optimize
            topic: The blog topic
            keywords: Target keywords
            
        Returns:
            Optimized content
        """
        logger.info(f"Optimizing content for SEO about {topic}")
        
        try:
            # First analyze current SEO performance
            seo_analysis = self.analyze_seo(content, topic, keywords)
            
            # If content already scores well, make minimal changes
            if seo_analysis.get("overall_score", 0) > 85:
                logger.info("Content already scores well for SEO. Making minimal optimization.")
                
                # Add internal linking suggestions
                optimized_content = self._add_internal_linking_suggestions(content, topic)
                
                # Ensure keyword presence in headings
                optimized_content = self._optimize_headings(optimized_content, topic, keywords)
                
                return optimized_content
            
            # Otherwise perform full optimization
            optimized_content = self.seo_optimization_chain.run(
                topic=topic,
                keywords=keywords,
                content=content
            )
            
            logger.info("Successfully optimized content for SEO")
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error optimizing content for SEO: {str(e)}", exc_info=True)
            # Return original content if optimization fails
            return content
    
    def _add_internal_linking_suggestions(self, content: str, topic: str) -> str:
        """
        Add internal linking suggestions to content.
        
        Args:
            content: The blog content
            topic: The blog topic
            
        Returns:
            Content with linking suggestions
        """
        # Define related HR topics for linking
        related_topics = {
            "Employee Retention": "employee retention strategies",
            "Remote Work": "remote work best practices",
            "Diversity and Inclusion": "diversity and inclusion in the workplace",
            "Performance Management": "effective performance management",
            "Employee Wellness": "employee wellness programs",
            "HR Technology": "hr technology trends",
            "Recruitment": "recruitment best practices",
            "Employee Engagement": "employee engagement strategies",
            "Workplace Culture": "building positive workplace culture",
            "Leadership Development": "leadership development programs"
        }
        
        modified_content = content
        
        # Add linking suggestions for related topics
        for link_text, link_topic in related_topics.items():
            if link_text.lower() in topic.lower():
                # Skip if the link topic is the same as the current topic
                continue
                
            # Look for mentions of the topic that could be linked
            pattern = r'\b' + re.escape(link_text) + r'\b'
            match = re.search(pattern, modified_content, re.IGNORECASE)
            
            if match and "[INTERNAL LINK SUGGESTION" not in modified_content:
                # Add link suggestion (only one per topic)
                start, end = match.span()
                link_suggestion = f"{modified_content[start:end]} [INTERNAL LINK SUGGESTION: {link_text} | {link_topic}]"
                modified_content = modified_content[:start] + link_suggestion + modified_content[end:]
        
        return modified_content
    
    def _optimize_headings(self, content: str, topic: str, keywords: str) -> str:
        """
        Ensure headings contain keywords for better SEO.
        
        Args:
            content: The blog content
            topic: The blog topic
            keywords: Target keywords
            
        Returns:
            Content with optimized headings
        """
        # Extract keywords
        keyword_list = [kw.strip() for kw in keywords.split(",")] if keywords else []
        if not keyword_list and topic:
            keyword_list = [topic]
        
        # If no keywords available, return original content
        if not keyword_list:
            return content
        
        modified_content = content
        heading_pattern = r'(#+)\s+(.*?)$'
        
        # Find all headings
        for match in re.finditer(heading_pattern, content, re.MULTILINE):
            heading_markers, heading_text = match.groups()
            original_heading = f"{heading_markers} {heading_text}"
            
            # Check if any keyword is already in the heading
            keyword_present = any(keyword.lower() in heading_text.lower() for keyword in keyword_list)
            
            # If no keyword present and it's a major heading (## or #), consider adding one
            if not keyword_present and heading_markers in ['#', '##', '###'] and len(heading_text) > 3:
                # Find most relevant keyword
                most_relevant = keyword_list[0]  # Default to first keyword
                
                # Try to find a better match
                for keyword in keyword_list:
                    if keyword.lower() in heading_text.lower():
                        most_relevant = keyword
                        break
                
                # Add the keyword if it makes sense
                if len(heading_text) < 50:  # Don't modify very long headings
                    new_heading = f"{heading_markers} {heading_text}: {most_relevant.capitalize()}"
                    modified_content = modified_content.replace(original_heading, new_heading)
        
        return modified_content
