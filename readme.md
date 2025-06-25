# 🤖 AI Interview Agent

An intelligent, AI-powered interview system that analyzes resumes, generates personalized questions, conducts voice-enabled interviews, and provides detailed feedback with real-time evaluation.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com)
[![Google](https://img.shields.io/badge/Google-Gemini-blue.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
## 🌟 Features

### 🧠 AI-Powered Analysis
- **Resume Intelligence**: Automatically extracts and analyzes skills, experience, and qualifications
- **Personalized Questions**: Generates tailored interview questions based on candidate's background
- **Real-time Evaluation**: Provides instant scoring and feedback for each answer
- **Multi-LLM Support**: Compatible with OpenAI GPT, Google Gemini, and Ollama models

### 🎤 Voice-Enabled Interface
- **Speech-to-Text**: Uses OpenAI Whisper for accurate audio transcription
- **Text-to-Speech**: AI reads questions aloud for better accessibility
- **Real-time Recording**: Live audio visualization during recording
- **Cross-browser Support**: Works on Chrome, Firefox, Safari, and Edge

### 📊 Comprehensive Reporting
- **Detailed Analytics**: Question-by-question breakdown with scores and feedback
- **Performance Metrics**: Overall scoring, completion rates, and improvement suggestions
- **Downloadable Reports**: Export complete interview analysis as text files
- **Progress Tracking**: Real-time interview progress and statistics

### 🎨 Modern User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Intuitive Interface**: Step-by-step guided interview process
- **Drag & Drop Upload**: Easy resume upload with file validation
- **Real-time Feedback**: Instant visual feedback and progress indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Modern web browser with microphone access
- One of the following AI providers:
  - OpenAI API key
  - Google Gemini API key
  - Ollama running locally

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/devendraBainda/AI-Interview_Agent.git
   cd ai-interview-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your API keys
   # Windows: notepad .env
   # Linux/Mac: nano .env
   ```

5. **Configure your AI provider** (edit `config.py`)
   ```python
   # Choose your preferred LLM provider
   LLM_PROVIDER = LLMProvider.GEMINI  # or OPENAI, OLLAMA
   
   # Set your API keys
   GEMINI_API_KEY = "your-gemini-api-key"
   OPENAI_API_KEY = "your-openai-api-key"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:5000`

## ⚙️ Configuration

### LLM Providers

#### OpenAI (Recommended for accuracy)
```python
LLM_PROVIDER = LLMProvider.OPENAI
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-4o-mini"  # or "gpt-4o" for better quality
```

#### Google Gemini (Recommended for cost-effectiveness)
```python
LLM_PROVIDER = LLMProvider.GEMINI
GEMINI_API_KEY = "your-gemini-api-key"
GEMINI_MODEL = "gemini-1.5-flash"  # or "gemini-1.5-pro"
```

#### Ollama (Recommended for privacy)
```python
LLM_PROVIDER = LLMProvider.OLLAMA
OLLAMA_MODEL = "phi3:mini"  # or "llama2", "mistral", etc.
OLLAMA_BASE_URL = "http://localhost:11434"
```

### Speech Recognition
```python
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
```

### Interview Settings
```python
MAX_QUESTIONS = 10              # Maximum questions per interview
QUESTION_TIMEOUT = 120          # Seconds per question
MAX_RECORDING_TIME = 60.0       # Maximum recording duration
EVALUATION_TIMEOUT = 30         # AI evaluation timeout
```

## 📁 Project Structure

```
ai-interview-agent/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables template
├── templates/                  # HTML templates
│   ├── base.html               # Base template
│   ├── index.html              # Landing page
│   ├── upload.html             # Resume upload
│   ├── interview.html          # Interview interface
│   ├── results.html            # Results display
│   ├── 404.html                # Error pages
│   └── 500.html
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Custom styles
│   └── js/
│       └── app.js              # JavaScript functionality
├── agentic_modules/            # AI processing modules
│   ├── document_loader.py      # Resume parsing
│   ├── resume_understanding_agent.py
│   ├── interview_planner_agent.py
│   ├── audio_interview_agent.py
│   ├── evaluation_agent.py
│   └── feedback_agent.py
├── utils/                      # Utility modules
│   ├── speech_to_text_whisper.py
│   └── text_to_speech.py
├── uploads/                    # Temporary file storage
├── session_data/               # Interview session data
└── temp_reports/               # Generated reports
```

## 🎯 How It Works

### 1. **Resume Analysis** 📄
- Upload resume in PDF, DOC, or DOCX format
- AI extracts key information (skills, experience, education)
- System analyzes candidate's background and expertise level

### 2. **Question Generation** ❓
- AI generates personalized questions based on resume analysis
- Questions cover technical skills, experience, and behavioral aspects
- Difficulty and topics adjusted to candidate's background

### 3. **Interactive Interview** 🎤
- Candidates can type or speak their answers
- Real-time speech-to-text transcription
- AI reads questions aloud for accessibility
- Visual progress tracking throughout the interview

### 4. **Real-time Evaluation** ⚡
- Each answer is evaluated immediately by AI
- Scoring based on relevance, completeness, and quality
- Detailed feedback and improvement suggestions provided

### 5. **Comprehensive Report** 📊
- Overall performance score and analytics
- Question-by-question breakdown
- Personalized recommendations for improvement
- Downloadable detailed report

## 🎮 Usage Examples

### Basic Interview Flow
```bash
1. Enter your name → Upload resume → AI analyzes background
2. Answer generated questions → Real-time evaluation
3. View results → Download report → Improve skills
```

### Voice Commands
- **"Start recording"** - Begin voice input
- **"Stop"** - End recording
- **"Skip question"** - Move to next question
- **"Repeat question"** - Hear question again

## 🧪 API Endpoints

### Core Routes
- `GET /` - Landing page
- `POST /start` - Initialize interview session
- `GET /upload` - Resume upload page
- `POST /analyze` - Process uploaded resume
- `GET /interview` - Interview interface
- `POST /submit_answer` - Submit interview answer
- `GET /results` - Display results
- `GET /download_report` - Download report

### API Endpoints
- `POST /transcribe_audio` - Audio transcription
- `GET /api/progress` - Real-time progress updates
- `GET /api/health` - System health check

## 🎨 Customization

### Themes and Styling
The application uses Bootstrap 5 with custom CSS. You can customize:
- Colors and branding in `static/css/style.css`
- Layout and components in template files
- Progress indicators and animations

### Question Templates
Modify question generation in `agentic_modules/interview_planner_agent.py`:
```python
def generate_interview_plan(resume_analysis):
    # Customize question types and difficulty
    # Add industry-specific questions
    # Adjust evaluation criteria
```

### Evaluation Criteria
Customize scoring in `agentic_modules/evaluation_agent.py`:
```python
def evaluate_answer_dynamically(question, answer):
    # Modify scoring algorithms
    # Add custom evaluation metrics
    # Adjust feedback generation
```

## 🔒 Security & Privacy

- **Data Protection**: Uploaded resumes are automatically deleted after processing
- **Session Security**: Interview data is stored securely and cleaned up after completion
- **API Security**: Rate limiting and input validation on all endpoints
- **Privacy**: No personal data is permanently stored

## 🐛 Troubleshooting

### Common Issues

**Microphone not working:**
- Ensure browser has microphone permissions
- Check that you're using HTTPS or localhost
- Try refreshing the page and granting permissions again

**AI responses are slow:**
- Check your internet connection
- Verify API keys are correct
- Consider switching to a faster model (e.g., Gemini Flash)

**Resume upload fails:**
- Ensure file is PDF, DOC, or DOCX format
- Check file size is under 16MB
- Verify file is not corrupted

**Ollama connection issues:**
- Ensure Ollama is running: `ollama serve`
- Check the model is installed: `ollama pull phi3:mini`
- Verify the base URL in config.py

### Debug Mode
Enable debug logging by setting:
```python
app.run(debug=True)
```

## 📈 Performance Tips

1. **Choose the right model**: 
   - Gemini Flash for speed and cost
   - GPT-4 for quality
   - Ollama for privacy

2. **Optimize Whisper model**:
   - Use "tiny" or "base" for faster transcription
   - Use "medium" or "large" for better accuracy

3. **Audio settings**:
   - Use good quality microphone
   - Record in quiet environment
   - Speak clearly and at moderate pace


### Development Setup
```bash
# Clone your fork
git clone https://github.com/devendraBainda/AI-Interview_Agent.git

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 .
black .
```

## 📊 Roadmap

- [ ] **Video Interview Support** - Add video recording and analysis
- [ ] **Multi-language Support** - Support for non-English interviews
- [ ] **Advanced Analytics** - Detailed performance insights and trends
- [ ] **Integration APIs** - Connect with HR systems and ATS platforms
- [ ] **Mobile App** - Native mobile applications for iOS and Android
- [ ] **Team Interviews** - Support for panel and group interviews
- [ ] **Industry Templates** - Pre-built templates for specific industries
- [ ] **AI Interviewer Personas** - Different AI interviewer personalities

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for GPT models and Whisper
- [Google](https://ai.google.dev/) for Gemini AI
- [Ollama](https://ollama.ai/) for local LLM support
- [Bootstrap](https://getbootstrap.com/) for UI components
- [Font Awesome](https://fontawesome.com/) for icons
- [Flask](https://flask.palletsprojects.com/) for the web framework

## 📞 Support

For support and questions:

- 📧 Email: [devendrabainda192@gmail.com](mailto:devendrabainda192@gmail.com)
- 🐛 Issues: [GitHub Issues](https://github.com/devendraBainda/AI-Interview_Agent/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/devendraBainda/AI-Interview_Agent/discussions)
- 📖 Documentation: [Wiki](https://github.com/devendraBainda/AI-Interview_Agent/wiki)

**Built with ❤️ using Flask, AI, and modern web technologies**

*Transform your interview process with the power of artificial intelligence!*
