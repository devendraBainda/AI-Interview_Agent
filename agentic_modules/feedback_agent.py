from config import Config
from utils.llm_manager import llm_manager

def generate_final_feedback(full_qa_evaluations, answered_count, total_questions):
    """Generate final feedback using the configured LLM provider"""
    
    if not full_qa_evaluations:
        return "No answers were provided during the interview."
    
    answered_percent = int((answered_count / total_questions) * 100)
    
    # Handle mixed string/dict evaluations - Enhanced processing
    formatted_evaluations = []
    total_score = 0
    valid_scores = 0
    
    for i, eval_item in enumerate(full_qa_evaluations):
        if isinstance(eval_item, dict):
            # Convert dict to readable string
            eval_parts = [f"Question {i+1} Evaluation:"]
            
            if 'score' in eval_item and eval_item['score'] is not None:
                score = eval_item['score']
                eval_parts.append(f"Score: {score}%")
                total_score += score
                valid_scores += 1
            
            if 'feedback' in eval_item and eval_item['feedback']:
                eval_parts.append(f"Feedback: {eval_item['feedback']}")
            
            if 'suggestions' in eval_item and eval_item['suggestions']:
                eval_parts.append("Suggestions:")
                for suggestion in eval_item['suggestions'][:3]:  # Limit suggestions
                    eval_parts.append(f"- {suggestion}")
            
            if 'strengths' in eval_item and eval_item['strengths']:
                eval_parts.append("Strengths:")
                for strength in eval_item['strengths'][:3]:  # Limit strengths
                    eval_parts.append(f"- {strength}")
            
            if 'weaknesses' in eval_item and eval_item['weaknesses']:
                eval_parts.append("Areas to improve:")
                for weakness in eval_item['weaknesses'][:3]:  # Limit weaknesses
                    eval_parts.append(f"- {weakness}")
            
            formatted_evaluations.append("\n".join(eval_parts))
        else:
            # Handle string evaluations as before
            formatted_evaluations.append(f"Question {i+1} Evaluation: {str(eval_item)}")
    
    # Calculate average score
    avg_score = total_score / valid_scores if valid_scores > 0 else 0
    
    joined_evaluations = "\n\n".join(formatted_evaluations)
    
    # Add comprehensive context to prompt
    completion_status = "complete" if answered_count == total_questions else "partial"
    partial_notice = ""
    if answered_count < total_questions:
        partial_notice = f" NOTE: This is a partial report based on {answered_count}/{total_questions} answered questions ({answered_percent}% completion)."
    
    system_prompt = """You are an expert AI interview coach and career advisor. 
    Generate comprehensive, constructive feedback that helps candidates improve their interview skills. 
    Be encouraging while providing specific, actionable advice."""
    
    user_prompt = f"""
    Generate a complete final interview report.{partial_notice}
    
    INTERVIEW STATISTICS:
    - Questions Answered: {answered_count}/{total_questions} ({answered_percent}%)
    - Average Score: {avg_score:.1f}%
    - Interview Status: {completion_status}
    
    DETAILED EVALUATIONS:
    {joined_evaluations}

    Create a comprehensive report with these sections:

    # 📊 Interview Performance Summary
    - Overall performance assessment
    - Completion rate and engagement
    - Key performance metrics

    # 💪 Candidate Strengths
    - Technical competencies demonstrated
    - Communication skills observed
    - Problem-solving approach

    # 🎯 Areas for Improvement
    - Specific skills to develop
    - Knowledge gaps identified
    - Interview technique suggestions

    # 📚 Recommended Learning Resources
    - Study topics based on performance
    - Skill development recommendations
    - Practice areas to focus on

    # 🌟 Final Assessment and Encouragement
    - Overall readiness assessment
    - Motivational feedback
    - Next steps for improvement

    Write in a professional yet encouraging tone. Be specific with recommendations and provide actionable advice.
    """

    try:
        final_report = llm_manager.generate_response(user_prompt, system_prompt)
        print("✅ Final report generated successfully")
        return final_report
        
    except Exception as e:
        error_msg = f"Report generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Provide a basic fallback report
        fallback_report = f"""
# Interview Report

## Performance Summary
- Questions Answered: {answered_count}/{total_questions} ({answered_percent}%)
- Average Score: {avg_score:.1f}%

## Evaluation Details
{joined_evaluations}

## Technical Issue
{error_msg}

Please try generating the report again or contact support if the issue persists.
"""
        return fallback_report
