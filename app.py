# app.py 
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash, get_flashed_messages
import os
import tempfile
import json
import sys
import base64
import pickle
import threading
import atexit
import signal
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import io

# Add root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
sys.path.append(PROJECT_ROOT)

# Import existing modules
try:
    from agentic_modules.document_loader import load_resume
    from agentic_modules.resume_understanding_agent import analyze_resume
    from agentic_modules.interview_planner_agent import generate_interview_plan
    from agentic_modules.audio_interview_agent import extract_questions_from_plan
    from agentic_modules.evaluation_agent import evaluate_answer_dynamically
    from agentic_modules.feedback_agent import generate_final_feedback
    from utils.speech_to_text_whisper import create_speech_to_text
    from config import Config
    print("✅ All AI modules loaded successfully!")
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("🔧 Make sure all your modules are in the correct directories")
    sys.exit(1)

# Flask app configuration
app = Flask(__name__)
app.secret_key = 'ai-interview-agent-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SESSION_FOLDER'] = 'session_data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global cleanup tracking
active_threads = []
cleanup_done = False

# Ensure required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SESSION_FOLDER'], exist_ok=True)
os.makedirs('whisper_temp', exist_ok=True)
os.makedirs('temp_reports', exist_ok=True)

# Initialize Speech-to-Text once with proper error handling
stt_instance = None
try:
    from utils.speech_to_text_whisper import create_speech_to_text
    stt_instance = create_speech_to_text(model_name=Config.WHISPER_MODEL, enhanced=True)
    print(f"✅ In-memory Whisper model '{Config.WHISPER_MODEL}' loaded successfully!")
except Exception as e:
    print(f"⚠️ In-memory Whisper model loading failed: {e}")
    print("🔧 Speech-to-text features will be disabled")
    stt_instance = None
# ===== CLEANUP FUNCTIONS =====

def cleanup_resources():
    """Clean up resources before shutdown"""
    global cleanup_done
    if cleanup_done:
        return
    
    print("🧹 Cleaning up resources...")
    
    # Clean up active threads
    for thread in active_threads:
        if thread.is_alive():
            try:
                thread.join(timeout=1.0)
            except:
                pass
    
    # Clean up temporary files
    temp_dirs = ['whisper_temp', 'temp_reports']
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                os.makedirs(temp_dir, exist_ok=True)
            except:
                pass
    
    cleanup_done = True
    print("✅ Cleanup completed")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"🛑 Received signal {signum}, shutting down gracefully...")
    cleanup_resources()
    sys.exit(0)

# Register cleanup handlers
atexit.register(cleanup_resources)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ===== TEMPLATE CONTEXT PROCESSOR =====

@app.context_processor
def inject_template_vars():
    """Make get_flashed_messages available in all templates"""
    return dict(
        get_flashed_messages=get_flashed_messages
    )

# ===== SESSION MANAGEMENT HELPERS =====

def save_session_data(session_id, data):
    """Save session data to file with proper error handling"""
    try:
        session_file = os.path.join(app.config['SESSION_FOLDER'], f"{session_id}.pkl")
        with open(session_file, 'wb') as f:
            pickle.dump(data, f)
        return True
    except Exception as e:
        print(f"❌ Error saving session data: {e}")
        return False

def load_session_data(session_id):
    """Load session data from file with proper error handling"""
    try:
        session_file = os.path.join(app.config['SESSION_FOLDER'], f"{session_id}.pkl")
        if os.path.exists(session_file):
            with open(session_file, 'rb') as f:
                return pickle.load(f)
        return None
    except Exception as e:
        print(f"❌ Error loading session data: {e}")
        return None

def delete_session_data(session_id):
    """Delete session data file with proper error handling"""
    try:
        session_file = os.path.join(app.config['SESSION_FOLDER'], f"{session_id}.pkl")
        if os.path.exists(session_file):
            os.remove(session_file)
        return True
    except Exception as e:
        print(f"❌ Error deleting session data: {e}")
        return False

def get_current_session_data():
    """Get current session data"""
    interview_id = session.get('interview_id')
    if not interview_id:
        return None
    return load_session_data(interview_id)

def update_session_data(updates):
    """Update current session data"""
    interview_id = session.get('interview_id')
    if not interview_id:
        return False
    
    data = load_session_data(interview_id) or {}
    data.update(updates)
    return save_session_data(interview_id, data)

# ===== UTILITY FUNCTIONS =====

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_file_cleanup(file_path):
    """Safely clean up files"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"⚠️ Could not clean up file {file_path}: {e}")
    return False

# ===== ROUTES =====

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_interview():
    """Initialize interview session"""
    candidate_name = request.form.get('candidate_name', '').strip()
    if not candidate_name:
        flash('Please enter your name', 'error')
        return render_template('index.html')
    
    # Create new interview session
    interview_id = str(uuid.uuid4())
    
    # Store minimal data in Flask session
    session['candidate_name'] = candidate_name
    session['interview_id'] = interview_id
    session['stage'] = 'upload'
    
    # Store detailed data in file
    session_data = {
        'candidate_name': candidate_name,
        'stage': 'upload',
        'created_at': datetime.now().isoformat(),
        'questions': [],
        'answers': [],
        'evaluations': [],
        'current_question': 0,
        'resume_text': '',
        'resume_analysis': '',
        'interview_plan': '',
        'final_report': ''
    }
    
    save_session_data(interview_id, session_data)
    
    print(f"🚀 New interview session started for: {candidate_name} (ID: {interview_id[:8]})")
    return redirect(url_for('upload_resume'))

@app.route('/upload')
def upload_resume():
    """Resume upload page"""
    if 'candidate_name' not in session:
        flash('Please start a new interview session', 'error')
        return redirect(url_for('index'))
    return render_template('upload.html', 
                         candidate_name=session['candidate_name'])

@app.route('/analyze', methods=['POST'])
def analyze_resume_route():
    """Process uploaded resume and generate questions"""
    if 'candidate_name' not in session:
        flash('Please start a new interview session', 'error')
        return redirect(url_for('index'))
    
    if 'resume_file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('upload_resume'))
    
    file = request.files['resume_file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('upload_resume'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload PDF, DOC, or DOCX files only.', 'error')
        return redirect(url_for('upload_resume'))
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session['interview_id']}_{filename}")
    
    try:
        # Save uploaded file
        file.save(file_path)
        print(f"📄 Resume uploaded: {filename}")
        
        # Step 1: Load resume using  existing module
        print("📖 Loading resume content...")
        resume_text = load_resume(file_path)
        
        # Step 2: Analyze resume using  existing module
        print("🧠 Analyzing resume...")
        resume_analysis = analyze_resume(resume_text)
        
        # Step 3: Generate interview plan using  existing module
        print("📝 Generating interview plan...")
        interview_plan = generate_interview_plan(resume_analysis)
        
        # Step 4: Extract questions using  existing module
        print("❓ Extracting questions...")
        questions = extract_questions_from_plan(interview_plan)
        
        # Update session data in file
        session_data = {
            'resume_text': resume_text,
            'resume_analysis': resume_analysis,
            'interview_plan': interview_plan,
            'questions': questions,
            'answers': [],
            'evaluations': [],
            'current_question': 0,
            'stage': 'interview',
            'candidate_name': session['candidate_name'],
            'created_at': datetime.now().isoformat(),
            'final_report': ''
        }
        
        save_session_data(session['interview_id'], session_data)
        
        # Update Flask session stage
        session['stage'] = 'interview'
        
        # Clean up uploaded file
        safe_file_cleanup(file_path)
        
        print(f"✅ Resume processed successfully! Generated {len(questions)} questions.")
        flash(f'Resume analyzed successfully! Generated {len(questions)} personalized questions.', 'success')
        return redirect(url_for('interview'))
        
    except Exception as e:
        # Clean up on error
        safe_file_cleanup(file_path)
        
        error_msg = f"Error processing resume: {str(e)}"
        print(f"❌ {error_msg}")
        flash(error_msg, 'error')
        return redirect(url_for('upload_resume'))

@app.route('/interview')
def interview():
    """Interview page"""
    data = get_current_session_data()
    if not data or 'questions' not in data:
        flash('No active interview session found', 'error')
        return redirect(url_for('index'))
    
    questions = data.get('questions', [])
    answers = data.get('answers', [])
    evaluations = data.get('evaluations', [])
    current_question = data.get('current_question', 0)
    
    # Check if interview is complete
    if current_question >= len(questions):
        return redirect(url_for('generate_results'))
    
    # Calculate metrics
    progress = ((current_question + 1) / len(questions)) * 100 if questions else 0
    answered_count = len([a for a in answers if a != "[Skipped]"])
    
    # Calculate average score from evaluations
    scores = []
    for eval_data in evaluations:
        if isinstance(eval_data, dict) and 'score' in eval_data:
            scores.append(eval_data['score'])
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return render_template('interview.html',
                         candidate_name=session['candidate_name'],
                         questions=questions,
                         answers=answers,
                         evaluations=evaluations,
                         current_question=current_question,
                         current_question_text=questions[current_question] if current_question < len(questions) else "",
                         progress=progress,
                         answered_count=answered_count,
                         avg_score=avg_score,
                         total_questions=len(questions))

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Process submitted answer"""
    data = get_current_session_data()
    if not data or 'questions' not in data:
        flash('No active interview session found', 'error')
        return redirect(url_for('index'))
    
    answer = request.form.get('answer', '').strip()
    action = request.form.get('action', 'submit')
    
    questions = data['questions']
    answers = data.get('answers', [])
    evaluations = data.get('evaluations', [])
    current_question = data.get('current_question', 0)
    
    # Handle skip action
    if action == 'skip':
        answer = "[Skipped]"
    
    # Validate answer
    if not answer and action != 'skip':
        flash('Please provide an answer or skip the question', 'error')
        return redirect(url_for('interview'))
    
    print(f"📝 Processing answer for question {current_question + 1}: {answer[:50]}{'...' if len(answer) > 50 else ''}")
    
    # Store answer
    answers.append(answer)
    
    # Evaluate answer using existing module
    if answer != "[Skipped]":
        try:
            question = questions[current_question]
            print(f"🤖 Evaluating answer...")
            evaluation = evaluate_answer_dynamically(question, answer)
            evaluations.append(evaluation)
            print(f"✅ Answer evaluated. Score: {evaluation.get('score', 'N/A')}%")
        except Exception as e:
            error_msg = f"Evaluation failed: {str(e)}"
            print(f"❌ {error_msg}")
            evaluations.append({
                'score': 0, 
                'feedback': error_msg,
                'suggestions': ['Technical issue occurred during evaluation'],
                'confidence': 'Low'
            })
    else:
        evaluations.append({
            'score': 0, 
            'feedback': 'Question skipped by candidate',
            'suggestions': ['Try to answer all questions for better assessment'],
            'confidence': 'High'
        })
    
    # Update session data
    data.update({
        'answers': answers,
        'evaluations': evaluations,
        'current_question': current_question + 1
    })
    
    save_session_data(session['interview_id'], data)
    
    return redirect(url_for('interview'))

@app.route('/results')
def generate_results():
    """Generate and display results"""
    data = get_current_session_data()
    if not data or 'questions' not in data:
        flash('No interview data found', 'error')
        return redirect(url_for('index'))
    
    questions = data.get('questions', [])
    answers = data.get('answers', [])
    evaluations = data.get('evaluations', [])
    
    print("📊 Generating final report...")
    
    # Generate final feedback using existing module
    answered_count = len([a for a in answers if a != "[Skipped]"])
    try:
        final_report = generate_final_feedback(evaluations, answered_count, len(questions))
        print("✅ Final report generated successfully!")
    except Exception as e:
        error_msg = f"Report generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        final_report = error_msg
    
    # Calculate comprehensive metrics
    scores = []
    for eval_data in evaluations:
        if isinstance(eval_data, dict) and 'score' in eval_data:
            scores.append(eval_data['score'])
    
    avg_score = sum(scores) / len(scores) if scores else 0
    completion_rate = (answered_count / len(questions)) * 100 if questions else 0
    
    # Update session data with results
    data.update({
        'final_report': final_report,
        'avg_score': avg_score,
        'completion_rate': completion_rate,
        'scores': scores,
        'stage': 'results'
    })
    
    save_session_data(session['interview_id'], data)
    session['stage'] = 'results'
    
    return render_template('results.html',
                         candidate_name=session['candidate_name'],
                         questions=questions,
                         answers=answers,
                         evaluations=evaluations,
                         final_report=final_report,
                         avg_score=avg_score,
                         completion_rate=completion_rate,
                         answered_count=answered_count,
                         total_questions=len(questions),
                         scores=scores,
                         interview_id=session.get('interview_id'))

@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    """Handle audio transcription using in-memory processing (Windows compatible)"""
    data = get_current_session_data()
    if not data:
        return jsonify({'error': 'No active interview session'})
    
    if not stt_instance:
        return jsonify({'error': 'Speech recognition not available'})
    
    try:
        # Get audio data from request
        request_data = request.get_json()
        audio_data = request_data.get('audio_data')
        
        if not audio_data:
            return jsonify({'error': 'No audio data provided'})
        
        print("🎤 Processing audio for transcription...")
        
        # Decode base64 audio
        try:
            import base64
            audio_bytes = base64.b64decode(audio_data)
            print(f"📦 Decoded audio: {len(audio_bytes)} bytes")
        except Exception as e:
            print(f"❌ Base64 decode error: {e}")
            return jsonify({'error': f'Invalid audio data format: {str(e)}'})
        
        # Validate audio size
        if len(audio_bytes) < 1000:  # Less than 1KB
            print("⚠️ Audio file too small")
            return jsonify({
                'transcription': '',
                'status': 'no_speech',
                'message': 'Audio file too small - no speech detected'
            })
        
        # ===== KEY CHANGE: Use in-memory processing instead of file operations =====
        try:
            print(f"🎯 Starting in-memory transcription...")
            
            # Use the new in-memory transcription method
            transcription = stt_instance.transcribe_audio_data(audio_bytes)
            
            print(f"📝 Raw transcription: '{transcription}'")
            
            if transcription and transcription.strip():
                # Additional cleaning for better results
                transcription = transcription.strip()
                
                # Filter out common noise patterns
                noise_patterns = [
                    'you', 'uh', 'um', 'ah', 'er', 'hmm', 'mm',
                    'thank you.', 'thanks.', 'bye.', 'hello.', 'hi.',
                    'okay.', 'ok.', '...', '. .', ', ,', '? ?'
                ]
                
                # Check if transcription is just noise
                words = transcription.lower().split()
                clean_words = [w.strip('.,!?') for w in words]
                
                if (len(transcription) < 5 or 
                    transcription.lower().strip('.,!? ') in noise_patterns or
                    all(word in noise_patterns for word in clean_words)):
                    
                    print("🔇 Detected only noise/artifacts")
                    return jsonify({
                        'transcription': '',
                        'status': 'no_speech',
                        'message': 'Only noise detected - please speak more clearly'
                    })
                
                print(f"✅ Audio transcribed successfully: {transcription}")
                return jsonify({
                    'transcription': transcription,
                    'status': 'success',
                    'message': 'Audio transcribed successfully',
                    'length': len(transcription),
                    'word_count': len(transcription.split()),
                    'method': 'in_memory'  # Indicates we used in-memory processing
                })
            else:
                print("🔇 No speech detected in transcription")
                return jsonify({
                    'transcription': '',
                    'status': 'no_speech',
                    'message': 'No speech detected in audio - please try speaking louder and clearer'
                })
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ In-memory transcription failed: {error_msg}")
            
            # Provide more specific error messages
            if "model" in error_msg.lower():
                error_msg = "Speech recognition model error - please refresh and try again"
            elif "audio" in error_msg.lower() or "format" in error_msg.lower():
                error_msg = "Audio format not supported - please try again"
            elif "decode" in error_msg.lower():
                error_msg = "Could not decode audio data - please try again"
            elif "too small" in error_msg.lower() or "short" in error_msg.lower():
                error_msg = "Recording too short - please speak for longer"
            else:
                error_msg = f"Transcription failed: {error_msg}"
            
            return jsonify({
                'error': error_msg,
                'status': 'error',
                'method': 'in_memory',
                'debug_info': {
                    'audio_size': len(audio_bytes),
                    'original_error': str(e)
                }
            })
    
    except Exception as e:
        error_msg = f"Request processing failed: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({'error': error_msg})
    
@app.route('/speak_text', methods=['POST'])
def speak_text_route():
    """Generate speech audio for AI questions and feedback"""
    try:
        request_data = request.get_json()
        text = request_data.get('text', '').strip()
        voice = request_data.get('voice', 'en-US-JennyNeural')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 1000:  # Limit text length
            return jsonify({'error': 'Text too long (max 1000 characters)'}), 400
        
        print(f"🔊 Generating speech for: {text[:50]}...")
        
        # Import TTS engine
        from utils.text_to_speech import tts_engine
        
        # Generate speech
        audio_data = tts_engine.generate_speech(text, voice)
        
        if not audio_data:
            return jsonify({'error': 'No audio generated'}), 500
        
        # Convert to base64 for transmission
        import base64
        audio_base64 = base64.b64encode(audio_data).decode()
        
        return jsonify({
            'audio_data': audio_base64,
            'status': 'success',
            'message': 'Speech generated successfully',
            'text_length': len(text)
        })
        
    except Exception as e:
        error_msg = f"TTS failed: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({'error': error_msg}), 500

@app.route('/download_report')
def download_report():
    """Download comprehensive interview report"""
    data = get_current_session_data()
    if not data or 'final_report' not in data:
        flash('No report data available', 'error')
        return redirect(url_for('index'))
    
    # Generate comprehensive report content
    report_content = f"""
AI INTERVIEW REPORT
{'='*50}
Candidate: {session.get('candidate_name', 'Unknown')}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Interview ID: {session.get('interview_id', 'N/A')}
LLM Provider: {Config.LLM_PROVIDER.value.upper()}
Speech Model: {Config.WHISPER_MODEL}

PERFORMANCE SUMMARY:
{'='*30}
- Total Questions: {len(data.get('questions', []))}
- Questions Answered: {len([a for a in data.get('answers', []) if a != "[Skipped]"])}
- Questions Skipped: {len([a for a in data.get('answers', []) if a == "[Skipped]"])}
- Completion Rate: {data.get('completion_rate', 0):.1f}%
- Average Score: {data.get('avg_score', 0):.1f}%

DETAILED ASSESSMENT:
{'='*30}
{data.get('final_report', 'No report available')}

QUESTION-BY-QUESTION BREAKDOWN:
{'='*40}
"""
    
    questions = data.get('questions', [])
    answers = data.get('answers', [])
    evaluations = data.get('evaluations', [])
    
    for i, (question, answer) in enumerate(zip(questions, answers)):
        report_content += f"\n{'-'*20} Question {i+1} {'-'*20}\n"
        report_content += f"QUESTION: {question}\n\n"
        report_content += f"ANSWER: {answer}\n\n"
        
        if i < len(evaluations) and isinstance(evaluations[i], dict):
            eval_data = evaluations[i]
            report_content += f"EVALUATION:\n"
            report_content += f"- Score: {eval_data.get('score', 0)}%\n"
            report_content += f"- Feedback: {eval_data.get('feedback', 'No feedback')}\n"
            
            if eval_data.get('suggestions'):
                report_content += f"- Suggestions: {', '.join(eval_data['suggestions'])}\n"
            
            if eval_data.get('strengths'):
                report_content += f"- Strengths: {', '.join(eval_data['strengths'])}\n"
            
            report_content += f"- Confidence: {eval_data.get('confidence', 'N/A')}\n"
        
        report_content += f"\n{'='*50}\n"
    
    # Add technical details
    report_content += f"""
TECHNICAL DETAILS:
{'='*20}
- LLM Provider: {Config.LLM_PROVIDER.value.upper()}
- Speech Recognition: {Config.WHISPER_MODEL}
- Question Generation: Automated based on resume analysis
- Evaluation Method: Dynamic AI assessment
- Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

End of Report
"""
    
    # Create file-like object
    report_file = io.BytesIO()
    report_file.write(report_content.encode('utf-8'))
    report_file.seek(0)
    
    filename = f"interview_report_{session.get('candidate_name', 'candidate')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    print(f"📥 Generating download for: {filename}")
    
    return send_file(report_file, 
                     as_attachment=True, 
                     download_name=filename,
                     mimetype='text/plain')

@app.route('/reset')
def reset_interview():
    """Reset interview session"""
    candidate_name = session.get('candidate_name', 'Unknown')
    interview_id = session.get('interview_id')
    
    # Clean up session data file
    if interview_id:
        delete_session_data(interview_id)
    
    session.clear()
    print(f"🔄 Interview session reset for: {candidate_name}")
    flash('Interview session reset successfully', 'info')
    return redirect(url_for('index'))

# ===== API ENDPOINTS =====

@app.route('/api/progress')
def get_progress():
    """API endpoint for real-time progress updates"""
    data = get_current_session_data()
    if not data or 'questions' not in data:
        return jsonify({'error': 'No active interview'})
    
    questions = data.get('questions', [])
    answers = data.get('answers', [])
    current_question = data.get('current_question', 0)
    evaluations = data.get('evaluations', [])
    
    # Calculate metrics
    progress = ((current_question + 1) / len(questions)) * 100 if questions else 0
    answered_count = len([a for a in answers if a != "[Skipped]"])
    
    # Calculate average score
    scores = [eval_data.get('score', 0) for eval_data in evaluations if isinstance(eval_data, dict)]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return jsonify({
        'progress': progress,
        'current_question': current_question + 1,
        'total_questions': len(questions),
        'answered_count': answered_count,
        'avg_score': avg_score,
        'completion_rate': (answered_count / len(questions)) * 100 if questions else 0
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Interview Agent is running',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'llm_provider': Config.LLM_PROVIDER.value,
            'whisper_model': Config.WHISPER_MODEL,
            'max_questions': getattr(Config, 'MAX_QUESTIONS', 10)
        },
        'modules_loaded': {
            'speech_to_text': stt_instance is not None,
            'ai_modules': True
        }
    })

# ===== ERROR HANDLERS =====

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload_resume'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ===== MAIN =====

if __name__ == '__main__':
    print("🤖 AI Interview Agent - Flask Edition")
    print("=" * 60)
    print(f"📊 LLM Provider: {Config.LLM_PROVIDER.value.upper()}")
    print(f"🎤 Speech Model: {Config.WHISPER_MODEL}")
    print(f"📁 Upload Directory: {app.config['UPLOAD_FOLDER']}")
    print(f"💾 Session Directory: {app.config['SESSION_FOLDER']}")
    print(f"🔧 Debug Mode: {'ON' if app.debug else 'OFF'}")
    print("=" * 60)
    print("🚀 Starting server...")
    print("🌐 Access the app at: http://localhost:5000")
    if Config.LLM_PROVIDER.value == 'ollama':
        print("📖 Make sure Ollama is running: ollama serve")
    print("=" * 60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        cleanup_resources()
    except Exception as e:
        print(f"❌ Server error: {e}")
        cleanup_resources()
