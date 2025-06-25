import re
import json
from config import Config
from utils.llm_manager import llm_manager

def evaluate_answer_dynamically(question, answer, context=None):
    """Evaluate answer using the configured LLM provider"""
    
    # Handle skipped answers
    if "[skipped]" in answer.lower() or "[skip]" in answer.lower():
        return {
            "score": 0,
            "feedback": "Question skipped by candidate",
            "suggestions": ["Attempt all questions for better assessment"],
            "confidence": "High",
            "strengths": [],
            "weaknesses": ["Question avoidance"],
            "followup_questions": []
        }
    
    system_prompt = """You are an expert interview evaluator. Assess the candidate's answer 
    objectively and provide constructive feedback. Consider clarity, relevance, depth, 
    and completeness of the response. Always respond in valid JSON format."""
    
    # Prepare context information
    context_prompt = f"\n\nContext from previous answers: {context}" if context else ""
    
    user_prompt = f"""
    Please evaluate this interview answer:
    
    QUESTION: {question}
    CANDIDATE ANSWER: {answer}
    {context_prompt}

    Provide evaluation based on:
    - Relevance to the question (0-30 points)
    - Technical accuracy (0-30 points)
    - Depth of knowledge (0-20 points)
    - Clarity of explanation (0-20 points)

    Return your evaluation in this exact JSON format:
    {{
        "score": <integer 0-100>,
        "feedback": "<detailed feedback 2-3 sentences>",
        "suggestions": ["<suggestion1>", "<suggestion2>"],
        "confidence": "<High/Medium/Low>",
        "strengths": ["<strength1>", "<strength2>"],
        "weaknesses": ["<weakness1>", "<weakness2>"],
        "followup_questions": ["<question1>", "<question2>"]
    }}
    
    Ensure the response is valid JSON only, no additional text.
    """

    try:
        evaluation_text = llm_manager.generate_response(user_prompt, system_prompt)
        
        # Clean the response to extract JSON
        evaluation_text = evaluation_text.strip()
        
        # Remove markdown code blocks if present
        evaluation_text = re.sub(r'^```json\n?|\n?```$', '', evaluation_text, flags=re.MULTILINE)
        evaluation_text = re.sub(r'^```\n?|\n?```$', '', evaluation_text, flags=re.MULTILINE)
        
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', evaluation_text, re.DOTALL)
        if json_match:
            evaluation_text = json_match.group()
        
        # Parse JSON
        evaluation = json.loads(evaluation_text)
        
        # Validate required keys and provide defaults
        required_keys = {
            "score": 0,
            "feedback": "No feedback provided",
            "suggestions": [],
            "confidence": "Medium",
            "strengths": [],
            "weaknesses": [],
            "followup_questions": []
        }
        
        for key, default_value in required_keys.items():
            if key not in evaluation:
                evaluation[key] = default_value
        
        # Ensure score is within valid range
        evaluation["score"] = max(0, min(100, int(evaluation["score"])))
        
        print(f"✅ Answer evaluated successfully - Score: {evaluation['score']}%")
        return evaluation
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parsing failed: {e}")
        return parse_text_evaluation(evaluation_text)
    except Exception as e:
        print(f"❌ Answer evaluation failed: {e}")
        return {
            "score": 0,
            "feedback": f"Evaluation failed: {str(e)}",
            "suggestions": ["Technical issue occurred during evaluation"],
            "confidence": "Low",
            "strengths": [],
            "weaknesses": ["Evaluation error"],
            "followup_questions": []
        }

def parse_text_evaluation(text):
    """Fallback parser for non-JSON responses"""
    result = {
        "score": 50,  # Default middle score
        "feedback": "",
        "suggestions": [],
        "confidence": "Medium",
        "strengths": [],
        "weaknesses": [],
        "followup_questions": []
    }
    
    try:
        # Try to extract score
        score_patterns = [
            r"score.*?(\d{1,3})",
            r"(\d{1,3}).*?points?",
            r"(\d{1,3})\s*[/%]",
            r"rating.*?(\d{1,3})"
        ]
        
        for pattern in score_patterns:
            score_match = re.search(pattern, text, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
                if 0 <= score <= 100:
                    result["score"] = score
                    break
        
        # Extract confidence
        confidence_match = re.search(r"confidence.*?(low|medium|high)", text, re.IGNORECASE)
        if confidence_match:
            result["confidence"] = confidence_match.group(1).capitalize()
        
        # Extract suggestions
        suggestions_section = re.search(r"suggest.*?:(.*?)(?=\n\n|\n[A-Z]|$)", text, re.IGNORECASE | re.DOTALL)
        if suggestions_section:
            suggestions_text = suggestions_section.group(1)
            suggestions = [s.strip().lstrip('-•*') for s in suggestions_text.split('\n') if s.strip()]
            result["suggestions"] = suggestions[:3]  # Limit to 3 suggestions
        
        # Use the full text as feedback
        result["feedback"] = text[:500] + "..." if len(text) > 500 else text
        
        return result
    except Exception as e:
        print(f"⚠️ Text parsing failed: {e}")
        result["feedback"] = "Could not parse evaluation response"
        return result

def evaluate_answers_batch(qa_pairs):
    """Batch evaluation for efficiency"""
    if len(qa_pairs) <= 1:
        # For single questions, use individual evaluation
        return [evaluate_answer_dynamically(pair['question'], pair['answer']) for pair in qa_pairs]
    
    system_prompt = """You are an efficient batch evaluator. Evaluate multiple interview answers 
    and return results in JSON format."""
    
    combined_prompt = "Evaluate these interview answers:\n\n"
    for i, pair in enumerate(qa_pairs):
        combined_prompt += f"QUESTION {i+1}: {pair['question']}\n"
        combined_prompt += f"ANSWER: {pair['answer']}\n\n"
    
    combined_prompt += """
    Provide evaluations in JSON format as a list of objects with:
    - question_index (starting from 0)
    - score (0-100)
    - feedback (brief, 1-2 sentences)
    - suggestions (list of 1-2 items)
    - confidence (High/Medium/Low)
    
    Return only valid JSON array format.
    """
    
    try:
        response_text = llm_manager.generate_response(combined_prompt, system_prompt)
        
        # Clean and parse JSON
        response_text = re.sub(r'^```json\n?|\n?```$', '', response_text.strip(), flags=re.MULTILINE)
        evaluations = json.loads(response_text)
        
        # Validate and fill missing data
        for i, evaluation in enumerate(evaluations):
            if not isinstance(evaluation, dict):
                evaluations[i] = evaluate_answer_dynamically(qa_pairs[i]['question'], qa_pairs[i]['answer'])
        
        return evaluations
        
    except Exception as e:
        print(f"❌ Batch evaluation failed: {e}")
        # Fallback to individual evaluation
        return [evaluate_answer_dynamically(pair['question'], pair['answer']) for pair in qa_pairs]
