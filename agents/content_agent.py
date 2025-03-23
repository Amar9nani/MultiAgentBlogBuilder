import logging
import time
from typing import Dict, List, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json

from config import Config
from utils import create_markdown_blog, count_words

logger = logging.getLogger(__name__)

class ContentAgent:
    """Agent responsible for generating blog content based on the outline."""
    
    def __init__(self):
        """Initialize the Content Agent with necessary tools and LLM."""
        self.config = Config()
        
        # Initialize language model
        try:
            self.llm = ChatOpenAI(
                model_name=self.config.DEFAULT_MODEL,
                temperature=0.7,  # Higher temperature for more creative content
                max_tokens=self.config.CONTENT_MAX_TOKENS,
                api_key=self.config.OPENAI_API_KEY
            )
            logger.info("Content Agent initialized with primary model")
        except Exception as e:
            logger.warning(f"Failed to initialize primary model: {str(e)}. Using fallback model.")
            self.llm = ChatOpenAI(
                model_name=self.config.FALLBACK_MODEL,
                temperature=0.7,
                max_tokens=self.config.CONTENT_MAX_TOKENS,
                api_key=self.config.OPENAI_API_KEY
            )
        
        # Define prompt template for content generation
        self.section_content_prompt = PromptTemplate(
            template="""You are a professional HR content writer. Write high-quality, engaging content for the following section 
            of a blog post about "{topic}".
            
            Section Heading: {heading}
            Subheadings: {subheadings}
            Key Points to Cover: {key_points}
            Target Word Count: {target_word_count}
            
            Research Information:
            {research_information}
            
            Write in a professional but conversational style. Include relevant examples and actionable insights.
            Focus on providing value to HR professionals and managers.
            
            The content should be well-structured with proper paragraphs and transitions.
            Incorporate the headings and subheadings naturally.
            
            Ensure the content is factually accurate based on the provided research.
            Target approximately {target_word_count} words for this section.
            """,
            input_variables=["topic", "heading", "subheadings", "key_points", "target_word_count", "research_information"]
        )
        
        # Define prompt template for introduction
        self.introduction_prompt = PromptTemplate(
            template="""You are a professional HR content writer. Write an engaging introduction for a blog post titled 
            "{title}" about {topic}.
            
            This introduction should:
            1. Hook the reader with a compelling opening
            2. Establish the importance of the topic for HR professionals
            3. Briefly outline what the post will cover
            4. Be approximately {target_word_count} words
            
            Research Information:
            {research_information}
            
            Write in a professional but conversational style that draws the reader in.
            """,
            input_variables=["title", "topic", "target_word_count", "research_information"]
        )
        
        # Define prompt template for conclusion
        self.conclusion_prompt = PromptTemplate(
            template="""You are a professional HR content writer. Write a strong conclusion for a blog post titled 
            "{title}" about {topic}.
            
            This conclusion should:
            1. Summarize the key points covered in the blog
            2. Emphasize the importance of the topic
            3. Provide final thoughts or recommendations
            4. Include a call to action for HR professionals
            5. Be approximately {target_word_count} words
            
            Key points covered in the blog:
            {key_points}
            
            Write in a professional but conversational style that leaves the reader with clear takeaways.
            """,
            input_variables=["title", "topic", "target_word_count", "key_points"]
        )
        
        # Create chains
        self.section_content_chain = LLMChain(
            llm=self.llm,
            prompt=self.section_content_prompt
        )
        
        self.introduction_chain = LLMChain(
            llm=self.llm,
            prompt=self.introduction_prompt
        )
        
        self.conclusion_chain = LLMChain(
            llm=self.llm,
            prompt=self.conclusion_prompt
        )
        
        logger.info("Content Agent initialized successfully")
    
    def generate_content(self, topic: str, outline: Dict[str, Any], research_data: Dict[str, Any]) -> str:
        """
        Generate a complete blog post based on the outline and research data.
        
        Args:
            topic: Blog post topic
            outline: Structured outline with sections
            research_data: Dictionary with research information
            
        Returns:
            Complete blog post content as markdown
        """
        logger.info(f"Generating content for topic: {topic}")
        
        # Extract research information
        research_information = research_data.get("synthesized_research", "")
        
        # Extract blog title from outline
        blog_title = outline.get("title", f"{topic}: A Comprehensive Guide")
        
        # Initialize sections list
        sections = []
        
        # Process each section in the outline
        for section_outline in outline.get("sections", []):
            heading = section_outline.get("heading", "")
            key_points = section_outline.get("key_points", [])
            target_word_count = section_outline.get("target_word_count", 300)
            
            # Process section based on its type
            if heading.lower() == "introduction":
                # Generate introduction
                content = self.introduction_chain.run(
                    title=blog_title,
                    topic=topic,
                    target_word_count=target_word_count,
                    research_information=research_information
                )
                
                sections.append({
                    "heading": heading,
                    "content": content,
                    "subheadings": []
                })
                
            elif heading.lower() == "conclusion":
                # Collect all key points from other sections for the conclusion
                all_key_points = []
                for s in outline.get("sections", []):
                    if s.get("heading").lower() not in ["introduction", "conclusion"]:
                        all_key_points.extend(s.get("key_points", []))
                
                key_points_text = "\n".join([f"- {point}" for point in all_key_points])
                
                # Generate conclusion
                content = self.conclusion_chain.run(
                    title=blog_title,
                    topic=topic,
                    target_word_count=target_word_count,
                    key_points=key_points_text
                )
                
                sections.append({
                    "heading": heading,
                    "content": content,
                    "subheadings": []
                })
                
            else:
                # Generate content for main sections
                subheadings_info = []
                processed_subheadings = []
                
                # Process each subheading
                for subheading in section_outline.get("subheadings", []):
                    subheading_title = subheading.get("title", "")
                    subheading_key_points = subheading.get("key_points", [])
                    subheading_target_word_count = subheading.get("target_word_count", 200)
                    
                    subheadings_info.append(f"{subheading_title}")
                    
                    # Generate content for the subheading
                    subheading_content = self.section_content_chain.run(
                        topic=topic,
                        heading=subheading_title,
                        subheadings="",
                        key_points="\n".join([f"- {point}" for point in subheading_key_points]),
                        target_word_count=subheading_target_word_count,
                        research_information=research_information
                    )
                    
                    processed_subheadings.append({
                        "title": subheading_title,
                        "content": subheading_content
                    })
                    
                    # Small delay to avoid rate limiting
                    time.sleep(1)
                
                # Generate content for the main section
                section_content = self.section_content_chain.run(
                    topic=topic,
                    heading=heading,
                    subheadings="\n".join(subheadings_info),
                    key_points="\n".join([f"- {point}" for point in key_points]),
                    target_word_count=max(50, target_word_count - sum(subheading.get("target_word_count", 200) for subheading in section_outline.get("subheadings", []))),
                    research_information=research_information
                )
                
                sections.append({
                    "heading": heading,
                    "content": section_content,
                    "subheadings": processed_subheadings
                })
                
                # Small delay to avoid rate limiting
                time.sleep(2)
        
        # Create the complete blog post
        blog_content = create_markdown_blog(blog_title, sections)
        
        word_count = count_words(blog_content)
        logger.info(f"Generated blog content with {word_count} words")
        
        return blog_content
