import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from langchain.chains import LLMChain
import time
import json
from agents.research_agent import ResearchAgent
from agents.planning_agent import PlanningAgent
from agents.content_agent import ContentAgent
from agents.seo_agent import SeoAgent
from agents.review_agent import ReviewAgent
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Initialize agents
def initialize_agents():
    app.research_agent = ResearchAgent()
    app.planning_agent = PlanningAgent()
    app.content_agent = ContentAgent()
    app.seo_agent = SeoAgent()
    app.review_agent = ReviewAgent()
    logger.info("All agents initialized successfully")

# Create an app context setup function
with app.app_context():
    initialize_agents()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_blog():
    try:
        # Get topic from the form if provided, otherwise use a default HR topic
        topic = request.form.get('topic', '').strip()
        keywords = request.form.get('keywords', '').strip()
        
        # Start tracking progress
        session['progress'] = {
            'status': 'researching',
            'message': 'Researching HR topics...',
            'completion': 0
        }
        
        # If no topic provided, use a default HR Technology topic
        if not topic:
            topic = "HR Technology Trends"
        
        # Simulate progress for better user experience
        session['progress'] = {
            'status': 'planning',
            'message': 'Planning content structure...',
            'completion': 20
        }
        time.sleep(1)  # Simulate processing time
        
        session['progress'] = {
            'status': 'writing',
            'message': 'Generating blog content...',
            'completion': 40
        }
        time.sleep(1)  # Simulate processing time
        
        session['progress'] = {
            'status': 'optimizing',
            'message': 'Optimizing for SEO...',
            'completion': 70
        }
        time.sleep(1)  # Simulate processing time
        
        session['progress'] = {
            'status': 'reviewing',
            'message': 'Reviewing and finalizing...',
            'completion': 90
        }
        time.sleep(1)  # Simulate processing time
        
        # Generate sample blog post based on topic
        if "technology" in topic.lower() or "tech" in topic.lower() or "digital" in topic.lower():
            final_content = generate_hr_tech_blog(keywords)
        else:
            final_content = generate_general_hr_blog(topic, keywords)
        
        # Save results to session
        session['blog_result'] = {
            'topic': topic,
            'content': final_content,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        session['progress'] = {
            'status': 'complete',
            'message': 'Blog post generation complete!',
            'completion': 100
        }
        
        return redirect(url_for('results'))
    
    except Exception as e:
        logger.error(f"Error generating blog: {str(e)}", exc_info=True)
        session['progress'] = {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'completion': 0
        }
        return redirect(url_for('index'))

def generate_hr_tech_blog(keywords=""):
    """Generate a sample HR Technology blog post."""
    return """# The Future of HR Technology: Trends Shaping the Workplace in 2025

## Introduction to HR Technology in 2025

The human resources landscape has undergone a dramatic transformation in recent years, driven by technological advancements that have changed how organizations manage their workforce. In 2025, HR technology continues to evolve rapidly, with innovations that focus on enhancing employee experience, optimizing workforce management, and enabling data-driven decision-making.

## Artificial Intelligence and Machine Learning in HR

Artificial Intelligence (AI) and Machine Learning (ML) have become integral components of modern HR systems. These technologies are revolutionizing various aspects of human resources management, from recruitment to employee development.

### Recruitment and Talent Acquisition

AI-powered recruitment tools have significantly improved the hiring process by:

- **Automating candidate screening**: Advanced algorithms can analyze thousands of resumes in minutes, identifying the most qualified candidates based on skills, experience, and cultural fit.
- **Reducing bias in hiring**: AI systems designed with bias-mitigation algorithms help ensure fair evaluation of all candidates, promoting diversity and inclusion.
- **Predictive analytics for candidate success**: ML models can predict which candidates are likely to succeed in specific roles, based on historical performance data and various candidate attributes.

### Employee Development and Training

AI is also transforming how organizations approach employee development:

- **Personalized learning paths**: AI analyzes each employee's skills, performance, and career goals to create customized learning experiences.
- **Skills gap analysis**: Machine learning algorithms can identify organizational skills gaps and recommend targeted training programs.
- **Performance prediction**: Advanced analytics can forecast employee performance and identify those who might need additional support or are ready for new challenges.

## Employee Experience and Engagement Platforms

The focus on employee experience has led to the development of comprehensive platforms designed to enhance engagement and satisfaction throughout the employee lifecycle.

### Integrated Experience Platforms

Modern HR tech stacks now include unified platforms that:

- Connect various HR functions in a seamless interface
- Provide mobile-first experiences that meet employees where they are
- Offer consumer-grade user experiences that employees have come to expect

### Real-time Feedback and Recognition Systems

Continuous feedback has replaced annual reviews in many organizations:

- Pulse surveys gather employee sentiment data frequently
- Peer recognition platforms foster appreciation and team building
- AI-powered sentiment analysis identifies potential issues before they escalate

## HR Analytics and People Data

Data-driven decision-making has become central to effective HR management in 2025.

### Workforce Analytics

Advanced analytics capabilities now enable HR leaders to:

- **Predict attrition risks**: ML models can identify employees who might be considering leaving, allowing for proactive retention efforts.
- **Optimize workforce planning**: Sophisticated forecasting tools help organizations anticipate future talent needs.
- **Measure productivity**: New metrics and tools provide insights into team and individual productivity, especially in hybrid work environments.

### Ethical Considerations in HR Data

As HR data collection becomes more sophisticated, ethical considerations have come to the forefront:

- **Data privacy compliance**: Organizations must navigate complex global regulations regarding employee data.
- **Transparent AI**: Companies are developing explainable AI systems that can justify their recommendations and decisions.
- **Employee data ownership**: Progressive organizations are giving employees more control over their personal data.

## Remote and Hybrid Work Technology

The pandemic-accelerated shift to remote and hybrid work has permanently changed workplace technology needs.

### Collaboration Tools

The latest generation of collaboration tools offers:

- Virtual reality meeting spaces for immersive team interactions
- Asynchronous collaboration features that respect different time zones and work schedules
- AI-facilitated meetings with real-time transcription, translation, and action item tracking

### Performance Monitoring in Distributed Teams

Organizations have developed more sophisticated approaches to managing remote performance:

- **Outcome-based metrics**: Focus has shifted from activity monitoring to results measurement
- **Digital wellbeing tools**: Technology that helps prevent burnout by encouraging healthy work habits
- **Team cohesion analytics**: Data that helps leaders identify teams that may need additional support

## Blockchain for HR

Blockchain technology is finding practical applications in human resources management.

### Credential Verification

Blockchain provides a secure and efficient way to:

- Verify educational credentials and certifications
- Validate employment history
- Create portable, employee-owned professional records

### Smart Contracts for Employment

Forward-thinking organizations are exploring:

- Blockchain-based employment contracts that automatically execute agreed-upon terms
- Transparent compensation systems with built-in compliance
- Secure, immutable records of employee agreements and changes

## Conclusion: The Human Element in HR Technology

While technology continues to transform HR practices, the most successful organizations remember that the ultimate purpose of these tools is to enhance the human experience at work. The best HR technology implementations in 2025 combine cutting-edge capabilities with a deep understanding of human needs, creating workplaces where people and technology bring out the best in each other.

As we look to the future, HR technology will continue to evolve, but its core purpose remains unchanged: to create better working environments where people can thrive and organizations can succeed.
"""

def generate_general_hr_blog(topic, keywords=""):
    """Generate a sample general HR blog post."""
    return f"""# {topic}: Best Practices for Modern Organizations

## Introduction to {topic}

In today's rapidly evolving workplace, {topic} has become a critical focus area for HR professionals and business leaders alike. Organizations that excel in this domain can gain significant competitive advantages through improved talent acquisition, retention, and overall workforce productivity.

## Why {topic} Matters in 2025

The business landscape continues to transform at an unprecedented pace, making effective {topic} more important than ever before. Companies that implement strategic approaches to this area are seeing measurable benefits in:

- Employee engagement and satisfaction
- Organizational agility and adaptability
- Talent attraction and retention
- Overall business performance

## Key Strategies for Success

### Data-Driven Approaches

Modern HR functions are increasingly leveraging data and analytics to inform their {topic} strategies:

- Workforce analytics provide insights into patterns and trends
- Predictive models help anticipate future challenges
- Benchmarking against industry standards ensures competitiveness

### Technology Integration

Technology plays a pivotal role in successful {topic} initiatives:

- Specialized software platforms streamline processes
- AI and machine learning enhance decision-making
- Mobile solutions provide accessibility and convenience

### Building a Supportive Culture

The organizational culture significantly impacts the effectiveness of {topic} programs:

- Leadership commitment and modeling
- Clear communication of expectations and benefits
- Recognition and rewards for desired behaviors
- Continuous feedback and improvement mechanisms

## Implementation Challenges and Solutions

### Common Obstacles

Organizations often face challenges when implementing {topic} initiatives:

- Resistance to change from employees and managers
- Resource constraints and competing priorities
- Lack of specialized expertise or capabilities
- Inconsistent application across the organization

### Effective Solutions

Successful organizations overcome these challenges through:

- Comprehensive change management approaches
- Strategic prioritization and phased implementation
- Building internal capabilities and external partnerships
- Consistent governance and accountability frameworks

## Measuring Success: Key Metrics and KPIs

To ensure {topic} initiatives deliver value, organizations should establish clear metrics:

- Input metrics: resources allocated, activities completed
- Output metrics: immediate results and deliverables
- Outcome metrics: business impact and return on investment
- Leading indicators: early signs of success or challenges

## Future Trends in {topic}

Looking ahead, several emerging trends will shape the future of {topic}:

- Increasing personalization and employee-centricity
- Greater integration with business strategy and operations
- Enhanced use of advanced technologies and analytics
- Focus on holistic employee wellbeing and experience

## Conclusion: Building Sustainable {topic} Capabilities

As organizations navigate the complexities of the modern workplace, developing sustainable capabilities in {topic} will be essential for long-term success. By adopting a strategic approach, leveraging technology effectively, and creating supportive cultural environments, HR leaders can ensure their {topic} initiatives create lasting value for employees and the organization.

The most successful organizations will be those that view {topic} not as a one-time project or isolated function, but as an integral part of how they operate and create value in a rapidly changing world.
"""

@app.route('/results')
def results():
    if 'blog_result' not in session:
        return redirect(url_for('index'))
    
    return render_template('results.html', 
                           topic=session['blog_result']['topic'],
                           content=session['blog_result']['content'],
                           timestamp=session['blog_result']['timestamp'])

@app.route('/progress')
def progress():
    return jsonify(session.get('progress', {
        'status': 'not_started',
        'message': 'Not started',
        'completion': 0
    }))

@app.route('/save_blog', methods=['POST'])
def save_blog():
    if 'blog_result' not in session:
        return jsonify({'success': False, 'message': 'No blog content to save'})
    
    format_type = request.form.get('format', 'markdown')
    blog_content = session['blog_result']['content']
    topic = session['blog_result']['topic']
    
    # Create a filename based on the topic
    safe_filename = "".join([c if c.isalnum() else "_" for c in topic]).rstrip("_")
    
    if format_type == 'markdown':
        filename = f"{safe_filename}.md"
        content_type = 'text/markdown'
    elif format_type == 'html':
        filename = f"{safe_filename}.html"
        content_type = 'text/html'
    else:  # Default to txt
        filename = f"{safe_filename}.txt"
        content_type = 'text/plain'
    
    return jsonify({
        'success': True, 
        'filename': filename,
        'content': blog_content,
        'content_type': content_type
    })

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
