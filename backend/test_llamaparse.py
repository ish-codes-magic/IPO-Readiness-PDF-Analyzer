#!/usr/bin/env python3
"""
Simple test script to verify LlamaParse + Gemini integration
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from pdf_processor import PDFProcessor

def test_pdf_processor():
    """Test the PDF processor with a sample PDF"""
    
    # Check if required environment variables are set
    required_env_vars = ["GEMINI_API_KEY", "LLAMA_CLOUD_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these environment variables before running the test.")
        return False
    
    try:
        # Initialize the PDF processor
        print("🚀 Initializing PDF processor...")
        processor = PDFProcessor()
        print("✅ PDF processor initialized successfully!")
        
        # Look for a test PDF file
        test_pdf_path = Path("app/CHEELIZZA PIZZA INDIA LTD - INVESTMENT DECK.pdf")
        if not test_pdf_path.exists():
            print(f"❌ Test PDF file not found: {test_pdf_path}")
            print("Please ensure the test PDF file exists in the app directory.")
            return False
        
        print(f"📄 Found test PDF: {test_pdf_path}")
        
        # Test the extraction
        print("🔍 Starting PDF extraction...")
        result = processor.extract_content(str(test_pdf_path))
        
        # Display results
        print("\n" + "="*50)
        print("EXTRACTION RESULTS")
        print("="*50)
        
        metadata = result.get('metadata', {})
        print(f"📊 Pages: {metadata.get('page_count', 'N/A')}")
        print(f"📊 Word count: {metadata.get('word_count', 'N/A')}")
        print(f"📊 Quality score: {metadata.get('quality_score', 'N/A')}")
        print(f"📊 Confidence score: {metadata.get('confidence_score', 'N/A')}")
        print(f"📊 Tables found: {metadata.get('tables_count', 'N/A')}")
        print(f"📊 Images found: {metadata.get('images_count', 'N/A')}")
        
        # Show company info if available
        company_info = result.get('company_info', {})
        if company_info and company_info.get('company_name'):
            print(f"\n🏢 Company: {company_info.get('company_name')}")
            print(f"🏢 Industry: {company_info.get('industry', 'N/A')}")
            print(f"🏢 Stage: {company_info.get('stage', 'N/A')}")
        
        # Show key insights
        key_insights = result.get('key_insights', [])
        if key_insights:
            print(f"\n💡 Key Insights ({len(key_insights)}):")
            for i, insight in enumerate(key_insights[:3], 1):
                print(f"   {i}. {insight}")
            if len(key_insights) > 3:
                print(f"   ... and {len(key_insights) - 3} more")
        
        # Show a snippet of the full text
        full_text = result.get('full_text', '')
        if full_text:
            snippet = full_text[:300] + "..." if len(full_text) > 300 else full_text
            print(f"\n📝 Text snippet:\n{snippet}")
        
        print("\n✅ PDF extraction completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during PDF extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing LlamaParse + Gemini PDF Processor")
    print("=" * 50)
    
    success = test_pdf_processor()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)