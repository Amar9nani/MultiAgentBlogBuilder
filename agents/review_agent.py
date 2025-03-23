import logging
import re
from typing import Dict, List, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json

from config import Config
from utils import count_words

logger = logging.getLogger(__name__)

class ReviewAgent:
    """Agent responsible for reviewing and improving content quality."""
    
    def __init__(self):
        """Initialize the Review Agent with necessary tools and LLM."""
        self.config = Config()
        
        # Initialize language model
        try:
            self.llm = ChatOpenAI(
                model_name=self.config.DEFAULT_MODEL,
                temperature=0.3,
                max_tokens=1000,
                api_key=self.config.OPENAI_API_KEY
            )
            logger.info("Review Agent initialized with primary model")
        except Exception as e:
            logger.warning(f"Failed to initialize primary model: {str(e)}. Using fallback model.")
            self.llm = ChatOpenAI(
                model_name=self.config.FALLBACK_MODEL,
                temperature=0.3,
                max_tokens=1000,
                api_key=self.config.OPENAI_API_KEY
            )
        
        # Define prompt template for content review
        self.content_review_prompt = PromptTemplate(
            template="""You are a professional editor for an HR industry blog. Review and improve the following blog content 
            for quality, clarity, and professionalism.
            
            Blog Content:
            {content}
            
            Your review should focus on:
            1. Grammar, spelling, and punctuation errors
            2. Clarity and readability improvements
            3. Tone consistency (professional but conversational)
            4. Logical flow and transitions between sections
            5. Accuracy of information and claims
            6. Completeness of thought and explanations
            7. Removal of any redundancies or unnecessary text
            
            Make direct improvements to the content rather than just providing feedback.
            Maintain all markdown formatting, headings, and structure, including any SEO elements.
            Ensure the content remains informative and valuable to HR professionals.
            Keep any [INTERNAL LINK SUGGESTION] tags intact.
            
            Return the improved content in markdown format.
            """,
            input_variables=["content"]
        )
        
        # Define prompt template for final check
        self.final_check_prompt = PromptTemplate(
            template="""You are a professional editor for an HR industry blog. Perform a final check on the following blog content 
            to ensure it is ready for publication.
            
            Blog Content:
            {content}
            
            Your final check should ensure:
            1. The content is free of any grammar, spelling, or punctuation errors
            2. The tone is professional yet conversational throughout
            3. There are no formatting issues or markdown errors
            4. The content flows logically and has smooth transitions
            5. Any obvious inaccuracies or outdated information is addressed
            6. The blog post is comprehensive and covers the topic well
            
            Make any final necessary improvements to the content.
            If any information appears outdated, add a note suggesting regular updates.
            
            Return the final, publication-ready content in markdown format.
            """,
            input_variables=["content"]
        )
        
        # Create chains
        self.content_review_chain = LLMChain(
            llm=self.llm,
            prompt=self.content_review_prompt
        )
        
        self.final_check_chain = LLMChain(
            llm=self.llm,
            prompt=self.final_check_prompt
        )
        
        logger.info("Review Agent initialized successfully")
    
    def review_content(self, content: str) -> str:
        """
        Review and improve blog content.
        
        Args:
            content: The blog content to review
            
        Returns:
            Improved content
        """
        logger.info("Starting content review and improvement")
        initial_word_count = count_words(content)
        
        try:
            # First pass: Content review and improvement
            reviewed_content = self.content_review_chain.run(content=content)
            logger.info("Completed first pass of content review")
            
            # Second pass: Final check
            final_content = self.final_check_chain.run(content=reviewed_content)
            logger.info("Completed final check of content")
            
            final_word_count = count_words(final_content)
            logger.info(f"Review complete. Word count: {initial_word_count} → {final_word_count}")
            
            # Verify content length hasn't decreased significantly
            if final_word_count < initial_word_count * 0.9:
                logger.warning("Significant content reduction detected during review")
                
                # If content length decreased too much, revert to original but fix obvious issues
                fixed_content = self._fix_basic_issues(content)
                logger.info("Reverted to original content with basic fixes")
                return fixed_content
            
            return final_content
            
        except Exception as e:
            logger.error(f"Error during content review: {str(e)}", exc_info=True)
            
            # If review fails, return original content with basic fixes
            fixed_content = self._fix_basic_issues(content)
            logger.info("Returning original content with basic fixes due to error")
            return fixed_content
    
    def _fix_basic_issues(self, content: str) -> str:
        """
        Fix basic issues in content when full review fails.
        
        Args:
            content: The blog content
            
        Returns:
            Content with basic issues fixed
        """
        # Fix common typos
        typos = {
            "teh ": "the ",
            "adn ": "and ",
            "waht ": "what ",
            "taht ": "that ",
            "thier ": "their ",
            "recieve": "receive",
            "alot ": "a lot ",
            "its ": "it's ",  # Common confusion (possessive vs. contraction)
            "occurr": "occur",
            "managment": "management",
            "accomodat": "accommodat",
            "enviroment": "environment"
        }
        
        fixed_content = content
        
        # Fix basic typos
        for typo, correction in typos.items():
            fixed_content = re.sub(r'\b' + re.escape(typo) + r'\b', correction, fixed_content, flags=re.IGNORECASE)
        
        # Fix multiple spaces
        fixed_content = re.sub(r' {2,}', ' ', fixed_content)
        
        # Fix extra line breaks
        fixed_content = re.sub(r'\n{3,}', '\n\n', fixed_content)
        
        # Ensure periods have spaces after them
        fixed_content = re.sub(r'\.(?=[A-Za-z])', '. ', fixed_content)
        
        return fixed_content
