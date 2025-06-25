import sys
import os
# Automatically add root folder
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
from config import Config
from utils.llm_manager import llm_manager

def generate_interview_plan(resume_briefing, difficulty="medium"):
    """Generate interview plan using the configured LLM provider"""
    
    system_prompt = """You are an expert interview designer. Based on the resume analysis provided, 
    create a comprehensive interview plan with diverse question types that assess both technical 
    and behavioral competencies. The questions should be tailored to the candidate's background 
    and experience level."""
    
    max_questions = getattr(Config, 'MAX_QUESTIONS', 10)
    
    user_prompt = f"""
    You are an expert AI interview designer.

    Based on the following candidate profile briefing:

    {resume_briefing}

    Design a complete technical interview plan with these specifications:
    - Difficulty Level: {difficulty}
    - Maximum Questions: {max_questions}
    - Question Types: Mix of technical, behavioral, and situational questions
    
    Create an interview plan with:
    1. Interview Overview: Brief description of interview focus areas
    2. Topics Covered: List of technical domains and skills to assess
    3. Question List: Exactly {max_questions} numbered interview questions
    4. Difficulty Progression: How questions increase in complexity
    
    Format your output with clear section headings:
    
    ### Interview Overview
    [Brief overview of what this interview will assess]
    
    ### Topics Covered
    [List of key areas to be evaluated]
    
    ### Question List
    1. [First question - usually introductory]
    2. [Second question - technical/role-specific]
    3. [Third question - behavioral/situational]
    [Continue with remaining questions...]
    
    ### Difficulty Progression
    [Explanation of how questions build in complexity]
    
    Make sure each question is:
    - Clear and specific
    - Relevant to the candidate's background
    - Appropriate for the difficulty level
    - Designed to assess different competencies
    
    Focus on creating questions that will generate meaningful responses for evaluation.
    """

    try:
        interview_plan = llm_manager.generate_response(user_prompt, system_prompt)
        print("✅ Interview plan generated successfully")
        return interview_plan
        
    except Exception as e:
        error_msg = f"Interview planning failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Provide fallback interview plan
        fallback_plan = f"""
### Interview Overview
Technical interview focusing on general software development skills and problem-solving abilities.

### Topics Covered
- Programming fundamentals
- Problem-solving approach
- Technical experience
- Communication skills
- Career development

### Question List
1. Can you tell me about yourself and your technical background?
2. What programming languages and technologies are you most comfortable with?
3. Describe a challenging technical problem you've solved recently.
4. How do you approach debugging when something isn't working as expected?
5. Tell me about a time when you had to learn a new technology or framework quickly.
6. How do you ensure your code is maintainable and follows best practices?
7. Describe your experience working in a team environment.
8. What interests you most about this role and our company?
9. How do you stay updated with new technologies and industry trends?
10. Where do you see yourself in your career in the next few years?

### Difficulty Progression
Questions start with general background, move to technical problem-solving, then behavioral scenarios, and conclude with career-focused questions.

Note: This is a fallback plan due to: {error_msg}
"""
        return fallback_plan

# Protected usage example
if __name__ == "__main__":
    from agentic_modules.document_loader import load_resume
    from agentic_modules.resume_understanding_agent import analyze_resume
    
    file_path = "uploads/resume.pdf"
    if os.path.exists(file_path):
        resume_text = load_resume(file_path)
        briefing = analyze_resume(resume_text)
        plan = generate_interview_plan(briefing)
        print(plan)
    else:
        print(f"File not found: {file_path}")
