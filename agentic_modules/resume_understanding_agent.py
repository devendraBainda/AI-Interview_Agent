import sys
import os
import json
# Automatically add root folder
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)  
from agentic_modules.document_loader import load_resume
from config import Config
from utils.llm_manager import llm_manager

def analyze_resume(resume_text, output_format="text"):
    """Analyze resume using the configured LLM provider"""
    
    system_prompt = """You are a professional technical recruiter and resume analyst. 
    Analyze the provided resume and extract key information including:
    - Professional summary
    - Key skills and technologies
    - Work experience highlights
    - Education background
    - Notable achievements
    - Areas of expertise
    
    Provide a comprehensive analysis that will be used to generate personalized interview questions."""
    
    user_prompt = f"""
    Carefully read the candidate's resume text below:

    {resume_text}

    Extract and summarize:
    - Key technical skills
    - Relevant domains / fields
    - Notable projects or achievements
    - Strengths and potential weak areas
    - Topics suitable for technical interview
    
    Output a complete INTERVIEW PREPARATION BRIEFING.
    Be detailed and specific.
    {f"Output as JSON with keys: skills, domains, projects, strengths, weaknesses, interview_topics" if output_format == "json" else ""}
    
    Please provide:
    1. Professional Summary (2-3 sentences)
    2. Key Technical Skills (list)
    3. Key Soft Skills (list)
    4. Work Experience Summary
    5. Education Background
    6. Notable Achievements
    7. Recommended Interview Focus Areas
    8. Potential Challenge Areas
    
    Format your response clearly with headers for each section.
    """

    try:
        briefing = llm_manager.generate_response(user_prompt, system_prompt)
        
        # Validate and return JSON if requested
        if output_format == "json":
            try:
                # Try to extract JSON from response if it's embedded in text
                import re
                json_match = re.search(r'\{.*\}', briefing, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    # If no JSON found, create structured JSON from text
                    return {
                        "skills": "See detailed analysis",
                        "domains": "See detailed analysis", 
                        "projects": "See detailed analysis",
                        "strengths": "See detailed analysis",
                        "weaknesses": "See detailed analysis",
                        "interview_topics": "See detailed analysis",
                        "full_analysis": briefing
                    }
            except json.JSONDecodeError:
                print("Invalid JSON format, returning text instead")
                return briefing
        
        print("✅ Resume analysis completed successfully")
        return briefing
        
    except Exception as e:
        error_msg = f"Resume analysis failed: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

# Protected usage example
if __name__ == "__main__":
    file_path = "uploads/resume.pdf"
    if os.path.exists(file_path):
        resume_text = load_resume(file_path)
        briefing = analyze_resume(resume_text, output_format="json")
        print(json.dumps(briefing, indent=2))
    else:
        print(f"Resume file {file_path} does not exist.")
