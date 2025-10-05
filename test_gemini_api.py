#!/usr/bin/env python3
"""
Test script to verify Gemini API key is working
"""

import google.generativeai as genai

# Hardcoded API key
GEMINI_API_KEY = "AIzaSyD3VYWq9sZIHR3LlcvaIloXILRvkp0S9pY"

def test_gemini_api():
    print("=" * 60)
    print("Testing Gemini API Key")
    print("=" * 60)
    print(f"\nAPI Key: {GEMINI_API_KEY[:20]}...")
    
    try:
        # Configure Gemini
        print("\n1. Configuring Gemini API...")
        genai.configure(api_key=GEMINI_API_KEY)
        print("✓ Configuration successful")
        
        # List available models
        print("\n2. Listing available models...")
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                print(f"   - {m.name}")
        
        if not available_models:
            print("✗ No models available for generateContent")
            return False
        
        # Use first available model
        model_name = available_models[0].replace('models/', '')
        print(f"\n3. Initializing model: {model_name}")
        model = genai.GenerativeModel(model_name)
        print("✓ Model initialized")
        
        # Test prompt
        test_prompt = """Create a simple Mermaid diagram for a Flask API with:
- routes.py (handles requests)
- models.py (database models)
- database (PostgreSQL)

Generate ONLY the Mermaid code, starting with 'graph TB'."""
        
        print("\n4. Testing API call with Mermaid generation prompt...")
        print(f"Prompt: {test_prompt[:80]}...")
        
        response = model.generate_content(test_prompt)
        
        print("\n✓ API call successful!")
        print("\n" + "=" * 60)
        print("RESPONSE FROM GEMINI:")
        print("=" * 60)
        print(response.text)
        print("=" * 60)
        
        # Check if it's valid Mermaid
        if 'graph' in response.text.lower():
            print("\n✓ Response contains Mermaid syntax!")
        else:
            print("\n⚠ Response might not be valid Mermaid syntax")
        
        print("\n" + "=" * 60)
        print("✓✓✓ GEMINI API KEY IS WORKING! ✓✓✓")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗✗✗ ERROR ✗✗✗")
        print("=" * 60)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nPossible issues:")
        print("- API key is invalid or expired")
        print("- API key doesn't have Gemini API enabled")
        print("- Network connectivity issues")
        print("- API quota exceeded")
        print("=" * 60)
        return False

if __name__ == '__main__':
    test_gemini_api()
