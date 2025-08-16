#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""

import os
import sys
import requests
import time
import subprocess
from pathlib import Path

def test_backend():
    """Test if backend server is working"""
    
    print("🔧 Testing IPO Readiness PDF Analyzer Backend...")
    print()
    
    # Test 1: Import check
    print("1. Testing imports...")
    try:
        from app.main import app
        from app.pdf_processor import PDFProcessor
        from app.ipo_analyzer import IPOAnalyzer
        print("   ✅ All imports successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Environment variables
    print("2. Checking environment variables...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        print("   ✅ GEMINI_API_KEY is set")
    else:
        print("   ⚠️  GEMINI_API_KEY not set or using default value")
        print("      Please set your actual Gemini API key in .env file")
    
    # Test 3: PDF Processor
    print("3. Testing PDF processor initialization...")
    try:
        pdf_processor = PDFProcessor()
        print("   ✅ PDF processor initialized successfully")
    except Exception as e:
        print(f"   ❌ PDF processor failed: {e}")
        return False
    
    # Test 4: IPO Analyzer (without API key for now)
    print("4. Testing IPO analyzer initialization...")
    try:
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            ipo_analyzer = IPOAnalyzer()
            print("   ✅ IPO analyzer initialized successfully")
        else:
            print("   ⚠️  Skipping IPO analyzer test (API key needed)")
    except Exception as e:
        print(f"   ❌ IPO analyzer failed: {e}")
        print("      This might be due to missing or invalid Gemini API key")
    
    print()
    print("🎉 Backend test completed!")
    print()
    print("Next steps:")
    print("1. Set your Gemini API key in backend/.env")
    print("2. Run: uv run python run.py")
    print("3. Test the frontend at http://localhost:3000")
    
    return True

if __name__ == "__main__":
    test_backend()