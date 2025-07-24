#!/usr/bin/env python3
"""
Configuration Example for Livebook Screenshot Tool
=================================================

This file shows how to configure and use the complete workflow:
1. ISBN batch processing to capture all pages
2. AI-powered filtering to identify TOC pages
"""

import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not found. Install with: pip install python-dotenv")

# =============================================================================
# CONFIGURATION SETTINGS
# =============================================================================

# OpenAI API Configuration (for TOC filtering)
# Option 1: Set in .env file (recommended)
#   Create a .env file with: OPENAI_API_KEY=your-api-key-here
# Option 2: Set directly here (not recommended for production)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', "your-api-key-here")

# ISBN List to Process
ISBN_LIST = [
    "978-3-12-316302-9",
    # Add more ISBNs here:
    # "978-3-12-123456-7",
    # "978-3-12-789012-3",
]

# Screenshot Configuration
MAX_PAGES_PER_BOOK = 10  # Stop after 10 pages per book
CONFIDENCE_THRESHOLD = 0.7  # AI confidence threshold for TOC identification

# Directory Configuration
SCREENSHOTS_DIR = "screenshots"
OUTPUT_REPORT = "toc_analysis_report.json"

# =============================================================================
# WORKFLOW FUNCTIONS
# =============================================================================

def setup_environment():
    """Setup the environment for the complete workflow."""
    print("🔧 Setting up environment...")
    
    # Set OpenAI API key
    if OPENAI_API_KEY and OPENAI_API_KEY != "your-api-key-here":
        os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
        print("✅ OpenAI API key configured")
    else:
        print("⚠️ OpenAI API key not configured")
        print("   Set OPENAI_API_KEY in this file or as environment variable")
    
    # Create screenshots directory
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    print(f"✅ Screenshots directory ready: {SCREENSHOTS_DIR}/")

def capture_all_screenshots():
    """Step 1: Capture all pages for all ISBNs."""
    print("\n📚 Step 1: Capturing Screenshots")
    print("=" * 50)
    
    try:
        from livebook_screenshot_tool import LivebookScreenshotTool
        
        def progress_callback(current, total, isbn):
            percent = (current + 1) / total * 100
            print(f"📊 Progress: {percent:.1f}% - Processing {isbn}")
        
        with LivebookScreenshotTool(headless=True) as tool:
            results = tool.screenshot_isbn_batch(
                isbn_list=ISBN_LIST,
                max_pages=MAX_PAGES_PER_BOOK,
                progress_callback=progress_callback
            )
            
            successful_books = sum(1 for r in results.values() if r['success'])
            total_pages = sum(r.get('total_pages', 0) for r in results.values() if r['success'])
            
            print(f"\n✅ Screenshot capture completed!")
            print(f"📚 Books processed: {successful_books}/{len(ISBN_LIST)}")
            print(f"📄 Total pages captured: {total_pages}")
            
            return results
            
    except Exception as e:
        print(f"❌ Screenshot capture failed: {e}")
        return None

def filter_toc_pages():
    """Step 2: Use AI to filter and identify TOC pages."""
    print("\n🤖 Step 2: AI-Powered TOC Filtering")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ OpenAI API key not configured - skipping AI filtering")
        print("💡 Set OPENAI_API_KEY to enable this feature")
        return None
    
    try:
        from filter_toc_screenshots import TOCScreenshotFilter
        
        filter_tool = TOCScreenshotFilter()
        
        results = filter_tool.filter_batch_directories(
            screenshots_dir=SCREENSHOTS_DIR,
            confidence_threshold=CONFIDENCE_THRESHOLD
        )
        
        # Display results
        summary = results['summary']
        print(f"📊 AI Analysis Results:")
        print(f"   📚 Books analyzed: {summary['total_books_processed']}")
        print(f"   📄 Screenshots analyzed: {summary['total_screenshots_analyzed']}")
        print(f"   ✅ TOC pages found: {summary['total_toc_pages_found']}")
        print(f"   ❌ Non-TOC pages: {summary['total_non_toc_pages']}")
        
        # Save report
        filter_tool.save_analysis_report(results, OUTPUT_REPORT)
        print(f"💾 Analysis report saved: {OUTPUT_REPORT}")
        
        # Optional: Organize files
        organize = input("\n🗂️ Organize files into toc_pages/ and non_toc_pages/ folders? (y/N): ").strip().lower()
        if organize == 'y':
            filter_tool.organize_filtered_results(results, organize_files=True)
            print("✅ Files organized!")
        
        return results
        
    except Exception as e:
        print(f"❌ TOC filtering failed: {e}")
        return None

def run_complete_workflow():
    """Run the complete workflow: capture + filter."""
    print("🚀 Complete Livebook TOC Extraction Workflow")
    print("=" * 60)
    print(f"📋 Processing {len(ISBN_LIST)} ISBNs")
    print(f"📄 Max {MAX_PAGES_PER_BOOK} pages per book")
    print(f"🎯 AI confidence threshold: {CONFIDENCE_THRESHOLD}")
    print()
    
    # Setup
    setup_environment()
    
    # Step 1: Capture screenshots
    screenshot_results = capture_all_screenshots()
    if not screenshot_results:
        print("❌ Workflow stopped - screenshot capture failed")
        return
    
    # Step 2: Filter TOC pages
    filter_results = filter_toc_pages()
    
    # Summary
    print(f"\n🎉 Workflow Complete!")
    print("=" * 60)
    
    if screenshot_results:
        successful_books = sum(1 for r in screenshot_results.values() if r['success'])
        print(f"📚 Books processed: {successful_books}/{len(ISBN_LIST)}")
    
    if filter_results:
        toc_pages = filter_results['summary']['total_toc_pages_found']
        print(f"🎯 TOC pages identified: {toc_pages}")
        print(f"📊 Detailed report: {OUTPUT_REPORT}")
    
    print(f"\n📁 Results available in: {SCREENSHOTS_DIR}/")

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def example_single_isbn():
    """Example: Process a single ISBN."""
    print("📖 Single ISBN Example")
    print("-" * 30)
    
    from livebook_screenshot_tool import LivebookScreenshotTool
    
    isbn = "978-3-12-316302-9"
    
    with LivebookScreenshotTool() as tool:
        results = tool.screenshot_all_pages(
            url=f"https://klettbib.livebook.de/{isbn}/",
            base_filename=isbn,
            max_pages=10,
            output_dir=f"screenshots/{isbn}"
        )
        
        if results['success']:
            print(f"✅ Captured {results['total_pages']} pages for {isbn}")
        else:
            print(f"❌ Failed to capture {isbn}")

def example_with_custom_settings():
    """Example: Custom configuration."""
    print("⚙️ Custom Settings Example")
    print("-" * 30)
    
    # Custom ISBN list
    custom_isbns = ["978-3-12-316302-9"]
    
    # Custom settings
    custom_max_pages = 5
    custom_confidence = 0.8
    
    from livebook_screenshot_tool import LivebookScreenshotTool
    
    with LivebookScreenshotTool(headless=False, window_size=(1600, 900)) as tool:
        results = tool.screenshot_isbn_batch(
            isbn_list=custom_isbns,
            max_pages=custom_max_pages
        )
        
        print(f"Captured with custom settings: {custom_max_pages} pages max")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "workflow":
            run_complete_workflow()
        elif command == "capture":
            setup_environment()
            capture_all_screenshots()
        elif command == "filter":
            setup_environment()
            filter_toc_pages()
        elif command == "single":
            example_single_isbn()
        elif command == "custom":
            example_with_custom_settings()
        else:
            print(f"Unknown command: {command}")
    else:
        print("📚 Livebook Screenshot Tool - Configuration Example")
        print("=" * 60)
        print()
        print("📋 Available commands:")
        print("  python config_example.py workflow   # Complete workflow")
        print("  python config_example.py capture    # Capture screenshots only")
        print("  python config_example.py filter     # AI filtering only")
        print("  python config_example.py single     # Single ISBN example")
        print("  python config_example.py custom     # Custom settings example")
        print()
        print("⚙️ Configuration:")
        print(f"  ISBNs to process: {len(ISBN_LIST)}")
        print(f"  Max pages per book: {MAX_PAGES_PER_BOOK}")
        print(f"  AI confidence threshold: {CONFIDENCE_THRESHOLD}")
        print(f"  OpenAI API key configured: {'Yes' if OPENAI_API_KEY != 'your-api-key-here' else 'No'}")
        print()
        print("💡 Edit this file to configure your settings!") 