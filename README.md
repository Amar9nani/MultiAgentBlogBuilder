# Multi-Agent SEO Blog Generator

A Python-based multi-agent system that generates high-quality, SEO-optimized blog posts for HR topics through research, planning, writing, optimization, and review stages.

## System Architecture

This project implements a multi-agent system with five specialized agents working together to generate comprehensive HR blog posts:

1. **Research Agent**: Finds trending HR topics and gathers relevant information from web searches and content scraping.
2. **Content Planning Agent**: Creates a structured outline with headings, subheadings, and key points based on research.
3. **Content Generation Agent**: Writes the blog content following the outline and research data.
4. **SEO Optimization Agent**: Ensures content follows SEO best practices including keyword usage and content structure.
5. **Review Agent**: Proofreads and improves content quality, ensuring it's ready for publication.

### Agent Workflow

1. The Research Agent searches for trending HR topics if none are specified, or researches a provided topic.
2. The Planning Agent creates a comprehensive outline based on the research.
3. The Content Agent generates the complete blog post following the outline.
4. The SEO Agent optimizes the content for search engines.
5. The Review Agent performs final editing and quality improvement.

## Tools and Frameworks Used

- **LangChain**: For building the agent architecture and chaining LLM operations
- **OpenAI GPT Models**: For content generation and analysis
- **Flask**: Web interface for interacting with the multi-agent system
- **Trafilatura**: For extracting clean text content from web pages
- **BeautifulSoup**: For web scraping and parsing HTML
- **Bootstrap**: For UI design
- **Markdown/Marked.js**: For rendering and formatting blog content

## Project Structure

- `main.py`: Flask application entry point
- `config.py`: Configuration settings
- `utils.py`: Utility functions for text processing
- `web_scraper.py`: Web scraping functionality
- `agents/`: Directory containing the five specialized agents
  - `research_agent.py`: Finds trending HR topics and researches content
  - `planning_agent.py`: Creates structured outlines
  - `content_agent.py`: Generates blog content
  - `seo_agent.py`: Optimizes content for SEO
  - `review_agent.py`: Proofreads and improves content quality

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/multi-agent-seo-blog-generator.git
   cd multi-agent-seo-blog-generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the project root with the following:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERPAPI_API_KEY=your_serpapi_key (optional)
   SESSION_SECRET=your_session_secret
   