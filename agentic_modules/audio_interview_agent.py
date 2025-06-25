import re
import sys
import os
import time
import json
# Automatically add root folder
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from config import Config

# Extract questions from interview plan with improved parsing
def extract_questions_from_plan(interview_plan):
    """Extract questions from interview plan with multiple parsing strategies"""
    questions = []
    
    # Strategy 1: Try multiple regex patterns for question extraction
    patterns = [
        r"\d+\.\s+(.+?)(?=\n\d+\.|\n\n|\n[A-Z][a-z]+:|\Z)",  # 1. Question text
        r"-\s+(.+?)(?=\n-|\n\n|\n[A-Z][a-z]+:|\Z)",           # - Question text
        r"\*\s+(.+?)(?=\n\*|\n\n|\n[A-Z][a-z]+:|\Z)",         # * Question text
        r"Q\d+:\s+(.+?)(?=\nQ\d+:|\n\n|\n[A-Z][a-z]+:|\Z)",   # Q1: Question text
        r"Question\s+\d+:\s+(.+?)(?=\nQuestion|\n\n|\n[A-Z][a-z]+:|\Z)"  # Question 1: Question text
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, interview_plan, re.DOTALL | re.IGNORECASE)
        if matches:
            # Clean up matches
            for match in matches:
                clean_question = match.strip().replace('\n', ' ')
                # Remove extra whitespace
                clean_question = re.sub(r'\s+', ' ', clean_question)
                if len(clean_question) > 10 and '?' in clean_question:
                    questions.append(clean_question)
            if questions:
                break
    
    # Strategy 2: Look for markdown-style questions
    if not questions:
        markdown_matches = re.findall(r"### (.+?)\n", interview_plan)
        for match in markdown_matches:
            if '?' in match and len(match) > 10:
                questions.append(match.strip())
    
    # Strategy 3: Look for questions ending with question marks
    if not questions:
        lines = interview_plan.split('\n')
        for line in lines:
            line = line.strip()
            if line.endswith('?') and len(line) > 15:
                # Remove numbering and bullet points
                clean_line = re.sub(r'^\d+\.?\s*', '', line)
                clean_line = re.sub(r'^[-*]\s*', '', clean_line)
                questions.append(clean_line)
    
    # Strategy 4: Fallback - extract any substantial lines that look like questions
    if not questions:
        lines = [line.strip() for line in interview_plan.split('\n') if line.strip()]
        for line in lines:
            # Skip headers and short lines
            if (len(line) > 20 and 
                not line.startswith(('##', '**', '===', '---')) and
                not line.endswith((':')) and
                ('?' in line or any(word in line.lower() for word in ['explain', 'describe', 'what', 'how', 'why', 'tell']))):
                questions.append(line)
    
    # Clean and validate questions
    cleaned_questions = []
    for q in questions:
        # Remove markdown formatting
        q = re.sub(r'\*\*(.+?)\*\*', r'\1', q)  # Remove bold
        q = re.sub(r'\*(.+?)\*', r'\1', q)      # Remove italic
        q = q.strip()
        
        # Ensure question ends with question mark if it's interrogative
        if any(word in q.lower() for word in ['what', 'how', 'why', 'when', 'where', 'which', 'who']) and not q.endswith('?'):
            q += '?'
        
        if len(q) > 10:
            cleaned_questions.append(q)
    
    # Remove duplicates while preserving order
    unique_questions = []
    seen = set()
    for q in cleaned_questions:
        if q.lower() not in seen:
            unique_questions.append(q)
            seen.add(q.lower())
    
    # Limit to max questions from config
    max_questions = getattr(Config, 'MAX_QUESTIONS', 10)
    final_questions = unique_questions[:max_questions]
    
    print(f"✅ Extracted {len(final_questions)} questions from interview plan")
    
    # If no questions found, provide fallback questions
    if not final_questions:
        print("⚠️ No questions extracted, using fallback questions")
        final_questions = [
            "Can you tell me about yourself and your professional background?",
            "What are your key technical skills and areas of expertise?",
            "Describe a challenging project you've worked on recently.",
            "How do you approach problem-solving in your work?",
            "What are your career goals and aspirations?"
        ]
    
    return final_questions

# Conduct full voice-based interview with skip functionality
def conduct_voice_interview(questions, skip_requested=False):
    """Conduct voice-based interview (placeholder for web implementation)"""
    qa_pairs = []
    
    print(f"\nStarting interview with {len(questions)} questions...")
    
    # Note: This function is primarily for standalone CLI usage
    # The web app handles interview flow differently through Flask routes
    
    for idx, question in enumerate(questions):
        print(f"\n{'='*50}")
        print(f"QUESTION {idx+1}/{len(questions)}")
        print(f"{'='*50}")
        print(f"Q: {question}")
        
        # Skip if requested
        if skip_requested:
            print("Interview skipped by user")
            qa_pairs.append({
                "question_number": idx+1,
                "question": question,
                "answer": "[Skipped]",
                "status": "skipped"
            })
            continue
        
        # For web app, this would be handled by the Flask routes
        # Here we just simulate the structure
        qa_pairs.append({
            "question_number": idx+1,
            "question": question,
            "answer": "[Web interface handles this]",
            "status": "pending"
        })
    
    return qa_pairs

# Test function for question extraction
def test_question_extraction():
    """Test the question extraction with sample interview plan"""
    sample_plan = """
    ### Interview Overview
    This interview focuses on technical skills and problem-solving.
    
    ### Question List
    1. Can you tell me about your background in software development?
    2. How do you approach debugging complex issues?
    3. What is your experience with database design?
    4. Describe a time when you had to learn a new technology quickly.
    5. How do you ensure code quality in your projects?
    
    ### Additional Questions
    - What are your thoughts on agile development?
    - How do you handle tight deadlines?
    """
    
    questions = extract_questions_from_plan(sample_plan)
    print("Extracted questions:")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
    
    return questions

if __name__ == "__main__":
    # Test question extraction
    test_questions = test_question_extraction()
