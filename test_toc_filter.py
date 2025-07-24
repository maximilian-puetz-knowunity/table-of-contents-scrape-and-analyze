#!/usr/bin/env python3
"""
Test TOC Filter
===============

Simple test script to demonstrate AI-powered TOC filtering
using the screenshots we've already captured.
"""

import os
from filter_toc_screenshots import TOCScreenshotFilter, TOCFilterError

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional for testing

def test_toc_filter():
    """Test the TOC filtering functionality."""
    
    print("🤖 Testing AI-Powered TOC Screenshot Filter")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️ OpenAI API key not found!")
        print("🔑 Option 1 (Recommended): Create .env file")
        print("   Create a .env file in this directory with:")
        print("   OPENAI_API_KEY=your-api-key-here")
        print()
        print("🔑 Option 2: Set environment variable")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print()
        print("💡 Get an API key from: https://platform.openai.com/api-keys")
        print()
        print("📋 What this script does when API key is available:")
        print("1. Analyzes all screenshots in screenshots/ directory")
        print("2. Uses GPT-4o mini to identify which pages contain table of contents")
        print("3. Provides confidence scores and reasoning for each analysis")
        print("4. Optionally organizes files into toc_pages/ and non_toc_pages/ folders")
        print("5. Generates a detailed JSON report")
        return
    
    try:
        # Initialize the filter
        print("🔧 Initializing TOC filter with GPT-4o mini...")
        filter_tool = TOCScreenshotFilter()
        
        # Check if we have screenshots to analyze
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            print(f"❌ Screenshots directory not found: {screenshots_dir}")
            print("💡 Run the screenshot capture first to generate screenshots")
            return
        
        # Find ISBN directories
        isbn_dirs = [d for d in os.listdir(screenshots_dir) 
                    if os.path.isdir(os.path.join(screenshots_dir, d)) and any(c.isdigit() for c in d)]
        
        if not isbn_dirs:
            print("❌ No ISBN directories found in screenshots/")
            print("💡 Run the ISBN batch processing first to generate screenshots")
            return
        
        print(f"📚 Found {len(isbn_dirs)} ISBN directories to analyze:")
        for isbn in isbn_dirs:
            print(f"   📖 {isbn}")
        print()
        
        # Test with a single screenshot first
        test_isbn = isbn_dirs[0]
        test_dir = os.path.join(screenshots_dir, test_isbn)
        test_screenshots = [f for f in os.listdir(test_dir) if f.endswith('.png')]
        
        if test_screenshots:
            print(f"🧪 Testing with a single screenshot from {test_isbn}...")
            test_image = os.path.join(test_dir, test_screenshots[0])
            
            print(f"📸 Analyzing: {test_screenshots[0]}")
            result = filter_tool.analyze_screenshot(test_image)
            
            print("📊 Analysis Result:")
            print(f"   Is TOC: {result.get('is_toc', 'Unknown')}")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Reasoning: {result.get('reasoning', 'No reasoning provided')}")
            
            if result.get('toc_elements_found'):
                print(f"   TOC Elements: {', '.join(result['toc_elements_found'])}")
            
            print()
        
        # Ask if user wants to continue with full analysis
        proceed = input("🔍 Do you want to analyze ALL screenshots? This will use OpenAI API credits (y/N): ").strip().lower()
        
        if proceed != 'y':
            print("🛑 Analysis stopped. Single test completed successfully!")
            return
        
        # Run full batch analysis
        print("🚀 Running full batch analysis...")
        results = filter_tool.filter_batch_directories(confidence_threshold=0.7)
        
        # Display results
        print("\n📊 Full Analysis Results:")
        print("-" * 50)
        
        summary = results['summary']
        print(f"📚 Books processed: {summary['total_books_processed']}")
        print(f"📄 Screenshots analyzed: {summary['total_screenshots_analyzed']}")
        print(f"✅ TOC pages found: {summary['total_toc_pages_found']}")
        print(f"❌ Non-TOC pages: {summary['total_non_toc_pages']}")
        
        # Show TOC pages found
        print(f"\n📑 TOC Pages Identified:")
        print("-" * 50)
        
        for isbn, book_results in results['processed_isbns'].items():
            if 'error' in book_results:
                print(f"❌ {isbn}: {book_results['error']}")
                continue
            
            toc_pages = book_results.get('toc_pages', [])
            if toc_pages:
                print(f"📖 {isbn} ({len(toc_pages)} TOC pages):")
                for page in toc_pages:
                    conf = page['confidence']
                    print(f"   ✅ {page['filename']} (confidence: {conf:.2f})")
            else:
                print(f"📖 {isbn}: No TOC pages found")
        
        # Save report
        print("\n💾 Saving analysis report...")
        filter_tool.save_analysis_report(results, "toc_analysis_report.json")
        print("✅ Report saved to: toc_analysis_report.json")
        
        # Optional file organization
        organize = input("\n🗂️ Organize files into toc_pages/ and non_toc_pages/ folders? (y/N): ").strip().lower()
        if organize == 'y':
            filter_tool.organize_filtered_results(results, organize_files=True)
            print("✅ Files organized!")
        
    except TOCFilterError as e:
        print(f"❌ TOC Filter Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def show_usage_info():
    """Show information about using the TOC filter."""
    print("📚 TOC Screenshot Filter - Usage Information")
    print("=" * 60)
    print()
    print("🎯 Purpose:")
    print("   Filter screenshots to identify only table of contents pages")
    print("   Uses OpenAI GPT-4o mini with vision capabilities")
    print()
    print("📋 Prerequisites:")
    print("   1. OpenAI API key (set OPENAI_API_KEY environment variable)")
    print("   2. Screenshots from ISBN batch processing")
    print("   3. Install dependencies: pip install openai Pillow")
    print()
    print("🚀 Quick Start:")
    print("   1. Set API key: export OPENAI_API_KEY='your-key'")
    print("   2. Run: python test_toc_filter.py")
    print("   3. Or use directly: python filter_toc_screenshots.py")
    print()
    print("💡 Features:")
    print("   • AI analysis of each screenshot")
    print("   • Confidence scores for TOC identification")
    print("   • Detailed reasoning for each decision")
    print("   • Automatic file organization")
    print("   • JSON reports for further analysis")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_usage_info()
    else:
        test_toc_filter() 