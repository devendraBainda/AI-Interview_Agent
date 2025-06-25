import os
import sys
import pytesseract
from pdf2image import convert_from_path
from config import Config

# Try to import langchain loaders, fallback to alternatives
try:
    from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain not available, using alternative PDF/DOCX loaders")

# Alternative loaders if langchain is not available
if not LANGCHAIN_AVAILABLE:
    try:
        import PyPDF2
        import docx2txt
        ALTERNATIVE_LOADERS = True
    except ImportError:
        ALTERNATIVE_LOADERS = False
        print("❌ No PDF/DOCX loaders available. Install: pip install PyPDF2 python-docx2txt")

def load_resume(file_path):
    """Load resume content from PDF or DOCX file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = os.path.splitext(file_path)[-1].lower()
    
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return load_docx(file_path)
    else:
        raise ValueError("Unsupported file format! Only PDF and DOCX are supported.")

def load_pdf(file_path):
    """Load PDF content with multiple fallback methods"""
    text = ""
    
    # Method 1: LangChain PyPDFLoader
    if LANGCHAIN_AVAILABLE:
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            text = "\n".join([doc.page_content for doc in documents])
            if text.strip():
                print("✅ PDF loaded successfully with LangChain")
                return text
        except Exception as e:
            print(f"⚠️ LangChain PDF loading failed: {e}")
    
    # Method 2: PyPDF2 fallback
    if ALTERNATIVE_LOADERS:
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            if text.strip():
                print("✅ PDF loaded successfully with PyPDF2")
                return text
        except Exception as e:
            print(f"⚠️ PyPDF2 loading failed: {e}")
    
    # Method 3: OCR fallback
    try:
        print("🔍 Attempting OCR extraction...")
        images = convert_from_path(file_path, dpi=300)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
        if text.strip():
            print("✅ PDF loaded successfully with OCR")
            return text
    except Exception as ocr_error:
        print(f"❌ OCR failed: {ocr_error}")
    
    raise ValueError("All PDF loading methods failed")

def load_docx(file_path):
    """Load DOCX content with multiple fallback methods"""
    text = ""
    
    # Method 1: LangChain Docx2txtLoader
    if LANGCHAIN_AVAILABLE:
        try:
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            text = "\n".join([doc.page_content for doc in documents])
            if text.strip():
                print("✅ DOCX loaded successfully with LangChain")
                return text
        except Exception as e:
            print(f"⚠️ LangChain DOCX loading failed: {e}")
    
    # Method 2: docx2txt fallback
    if ALTERNATIVE_LOADERS:
        try:
            import docx2txt
            text = docx2txt.process(file_path)
            if text.strip():
                print("✅ DOCX loaded successfully with docx2txt")
                return text
        except Exception as e:
            print(f"⚠️ docx2txt loading failed: {e}")
    
    # Method 3: python-docx fallback
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        if text.strip():
            print("✅ DOCX loaded successfully with python-docx")
            return text
    except Exception as e:
        print(f"⚠️ python-docx loading failed: {e}")
    
    raise ValueError("All DOCX loading methods failed")
