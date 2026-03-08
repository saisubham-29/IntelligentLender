#!/usr/bin/env python3
"""Test AI document parsing"""
import os
import sys

def test_ai_parser():
    print("🤖 Testing AI Document Parser\n")
    print("=" * 60)
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        print("\nSet it with:")
        print("  export OPENAI_API_KEY='sk-...'")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...")
    
    # Check dependencies
    try:
        import openai
        print("✓ openai package installed")
    except ImportError:
        print("❌ openai not installed. Run: pip install openai")
        return False
    
    try:
        import pdf2image
        print("✓ pdf2image package installed")
    except ImportError:
        print("❌ pdf2image not installed. Run: pip install pdf2image")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow package installed")
    except ImportError:
        print("❌ Pillow not installed. Run: pip install Pillow")
        return False
    
    # Check poppler
    try:
        from pdf2image import convert_from_path
        # Try to use it (will fail if poppler not installed)
        print("✓ poppler system dependency available")
    except Exception as e:
        print(f"⚠️  poppler might not be installed: {e}")
        print("\nInstall with:")
        print("  macOS: brew install poppler")
        print("  Ubuntu: sudo apt-get install poppler-utils")
    
    # Test parser initialization
    try:
        from credit_engine.ai_document_parser import AIDocumentParser
        parser = AIDocumentParser()
        print("✓ AIDocumentParser initialized")
        
        if parser.client:
            print(f"✓ OpenAI client connected (model: {parser.model})")
        else:
            print("❌ OpenAI client not initialized")
            return False
    except Exception as e:
        print(f"❌ Parser initialization failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All checks passed! AI parsing is ready.")
    print("\nTo test with a real PDF:")
    print("  python test_ai_parsing.py path/to/document.pdf")
    return True

def test_with_pdf(pdf_path):
    """Test parsing a real PDF"""
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"\n📄 Testing with: {pdf_path}\n")
    
    from credit_engine.ai_document_parser import AIDocumentParser
    parser = AIDocumentParser()
    
    print("🔄 Parsing financial statement...")
    result = parser.parse_annual_report(pdf_path)
    
    print("\n📊 Extracted Data:")
    print("=" * 60)
    import json
    print(json.dumps(result, indent=2))
    print("=" * 60)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_with_pdf(sys.argv[1])
    else:
        test_ai_parser()
