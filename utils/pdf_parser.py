"""
PDF Parser - Extract text from PDF resumes
Supports both uploaded files and file paths
"""

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print("⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")


def extract_text_from_pdf(file_obj):
    """
    Extract text from PDF file
    
    Args:
        file_obj: File object (from Flask request.files or open())
    
    Returns:
        dict: Result with success status, text, and word count
    """
    if not PYPDF2_AVAILABLE:
        return {
            'success': False,
            'error': 'PyPDF2 not installed. Run: pip install PyPDF2'
        }
    
    print("📄 Extracting text from PDF...")
    
    try:
        # Create PDF reader
        pdf_reader = PyPDF2.PdfReader(file_obj)
        
        # Extract text from all pages
        text = ""
        num_pages = len(pdf_reader.pages)
        
        print(f"   Reading {num_pages} pages...")
        
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        
        # Clean up text
        text = text.strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        word_count = len(text.split())
        
        print(f"✓ Extracted {word_count} words from {num_pages} pages")
        
        if word_count < 50:
            return {
                'success': False,
                'error': 'Text too short - PDF might be scanned/image-based'
            }
        
        return {
            'success': True,
            'text': text,
            'word_count': word_count,
            'num_pages': num_pages
        }
        
    except Exception as e:
        print(f"✗ PDF extraction failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def validate_pdf(file_obj):
    """
    Check if file is a valid PDF
    
    Args:
        file_obj: File object
    
    Returns:
        bool: True if valid PDF
    """
    try:
        # Try to read first few bytes
        file_obj.seek(0)
        header = file_obj.read(5)
        file_obj.seek(0)  # Reset position
        
        # PDF files start with %PDF-
        return header == b'%PDF-'
    except:
        return False


# Test the parser
if __name__ == "__main__":
    print("PDF Parser Test")
    print("="*50)
    
    # This would need an actual PDF file to test
    print("To test:")
    print("1. Place a resume.pdf in the project folder")
    print("2. Run: python -c \"from utils.pdf_parser import *; result = extract_text_from_pdf(open('resume.pdf', 'rb')); print(result)\"")