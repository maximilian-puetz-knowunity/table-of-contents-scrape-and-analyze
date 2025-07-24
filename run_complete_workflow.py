#!/usr/bin/env python3
"""
Complete Livebook TOC Extraction Workflow
=========================================

This script demonstrates the complete workflow for extracting table of contents from Livebooks:

1. 📸 Screenshot Capture: Capture all pages for specified ISBNs
2. 🤖 AI Filtering: Use GPT-4o mini to identify actual TOC pages  
3. 📁 Organization: Automatically organize files into TOC and non-TOC folders

Prerequisites:
- OpenAI API Key: Create a .env file with OPENAI_API_KEY=your-key-here
- Dependencies: Run pip install -r requirements.txt
- Chrome Browser: Installed on your system
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not found. Install with: pip install python-dotenv")
    print("💡 You can still set OPENAI_API_KEY as a regular environment variable")

# Import our tools
try:
    from livebook_screenshot_tool import LivebookScreenshotTool
    print("✅ Screenshot tool imported successfully")
except ImportError as e:
    print(f"❌ Failed to import screenshot tool: {e}")
    exit(1)

try:
    from filter_toc_screenshots import TOCScreenshotFilter, TOCFilterError
    print("✅ AI filter tool imported successfully")
except ImportError as e:
    print(f"❌ Failed to import AI filter tool: {e}")
    exit(1)

print("\n🚀 All imports completed!")

# Configuration Settings
# =====================

# ISBN List to Process
ISBN_LIST = [
    # Add more ISBNs here:
    "978-3-12-316302-9",
    "978-3-12-316303-6",
    "978-3-12-316304-3",
    "978-3-12-316305-0",
    "978-3-12-316306-7",
    "978-3-12-350550-8",
    "978-3-12-350552-2"
    # "978-3-12-789012-3",
]

# Workflow Settings
MAX_PAGES_PER_BOOK = 10        # Stop after 10 pages per book
CONFIDENCE_THRESHOLD = 0.7     # AI confidence threshold for TOC identification
HEADLESS_MODE = True           # Run browser in headless mode
AUTO_ORGANIZE = True           # Automatically organize files after filtering

def display_configuration():
    """Display current configuration."""
    print("⚙️ Workflow Configuration:")
    print(f"📚 ISBNs to process: {len(ISBN_LIST)}")
    for i, isbn in enumerate(ISBN_LIST, 1):
        print(f"   {i}. {isbn}")
    print(f"📄 Max pages per book: {MAX_PAGES_PER_BOOK}")
    print(f"🎯 AI confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"👻 Headless mode: {HEADLESS_MODE}")
    print(f"🗂️ Auto-organize files: {AUTO_ORGANIZE}")

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"🔑 OpenAI API key: {'*' * 20}{api_key[-4:]}")
    else:
        print("❌ OpenAI API key not found!")
        print("   Create .env file with: OPENAI_API_KEY=your-key-here")
        return False

    print("\n✅ Configuration ready!")
    return True

def capture_screenshots_step(isbn_list: List[str], max_pages: int = 10) -> Dict[str, Any]:
    """
    Step 1: Capture screenshots for all ISBNs.
    """
    print("\n📸 Step 1: Screenshot Capture")
    print("=" * 50)
    
    def progress_callback(book_index, total_books, isbn):
        """Update progress for current book."""
        percent = (book_index + 1) / total_books * 100
        print(f"📊 Progress: {percent:.1f}% - Processing {isbn}")
    
    try:
        with LivebookScreenshotTool(headless=HEADLESS_MODE) as tool:
            print("🚀 Starting screenshot capture...")
            
            # Capture screenshots for all ISBNs
            results = tool.screenshot_isbn_batch(
                isbn_list=isbn_list,
                max_pages=max_pages,
                progress_callback=progress_callback
            )
            
            # Calculate summary
            successful_books = sum(1 for r in results.values() if r['success'])
            total_pages = sum(r.get('total_pages', 0) for r in results.values() if r['success'])
            total_size = sum(r.get('total_size', 0) for r in results.values() if r['success'])
            
            print(f"\n📊 Screenshot Summary:")
            print(f"   ✅ Successful: {successful_books}/{len(isbn_list)} books")
            print(f"   📄 Total pages: {total_pages}")
            print(f"   💾 Total size: {total_size / (1024 * 1024):.1f} MB")
            
            for isbn, result in results.items():
                if result['success']:
                    pages = result['total_pages']
                    print(f"   📖 {isbn}: {pages} pages")
                else:
                    print(f"   ❌ {isbn}: Failed")
            
            return results
            
    except Exception as e:
        print(f"❌ Screenshot capture failed: {e}")
        return None

def filter_toc_step(screenshots_dir: str = "screenshots") -> Dict[str, Any]:
    """
    Step 2: Use AI to filter screenshots and identify TOC pages.
    """
    print("\n🤖 Step 2: AI-Powered TOC Filtering")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found!")
        print("   Create .env file with: OPENAI_API_KEY=your-key-here")
        return None
    
    # Find ISBN directories
    isbn_dirs = [d for d in os.listdir(screenshots_dir) 
                if os.path.isdir(os.path.join(screenshots_dir, d)) and any(c.isdigit() for c in d)]
    
    if not isbn_dirs:
        print("❌ No ISBN directories found")
        return None
    
    try:
        # Initialize filter
        print("🔧 Initializing AI filter...")
        filter_tool = TOCScreenshotFilter()
        
        # Track progress and results
        all_results = {}
        total_toc_pages = 0
        total_analyzed = 0
        total_cost = 0.0
        
        for i, isbn in enumerate(isbn_dirs):
            print(f"📖 Analyzing {isbn} ({i + 1}/{len(isbn_dirs)})...")
            
            try:
                # Analyze this ISBN directory
                isbn_results = filter_tool.filter_isbn_directory(
                    os.path.join(screenshots_dir, isbn),
                    confidence_threshold=CONFIDENCE_THRESHOLD
                )
                
                all_results[isbn] = isbn_results
                
                # Update counters
                book_toc_pages = len(isbn_results['toc_pages'])
                book_total_pages = isbn_results['total_screenshots']
                book_cost = book_total_pages * 0.00015
                
                total_toc_pages += book_toc_pages
                total_analyzed += book_total_pages
                total_cost += book_cost
                
                print(f"   ✅ {isbn}: {book_toc_pages}/{book_total_pages} pages are TOC (${book_cost:.4f})")
                
                if book_toc_pages > 0:
                    for page in isbn_results['toc_pages']:
                        conf = page['confidence']
                        print(f"      📄 {page['filename']} (confidence: {conf:.2f})")
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ {isbn}: Failed - {e}")
                all_results[isbn] = {'error': str(e)}
        
        # Create summary results
        summary_results = {
            'processed_isbns': all_results,
            'summary': {
                'total_books_processed': len(isbn_dirs),
                'total_screenshots_analyzed': total_analyzed,
                'total_toc_pages_found': total_toc_pages,
                'total_non_toc_pages': total_analyzed - total_toc_pages,
                'confidence_threshold': CONFIDENCE_THRESHOLD,
                'estimated_cost': total_cost
            }
        }
        
        print(f"\n📊 AI Analysis Summary:")
        print(f"   📚 Books analyzed: {len(isbn_dirs)}")
        print(f"   📄 Screenshots analyzed: {total_analyzed}")
        print(f"   ✅ TOC pages found: {total_toc_pages}")
        print(f"   ❌ Non-TOC pages: {total_analyzed - total_toc_pages}")
        print(f"   💰 Total cost: ${total_cost:.4f}")
        
        return summary_results
        
    except Exception as e:
        print(f"❌ AI filtering failed: {e}")
        return None

def organize_files_step(filter_results: Dict[str, Any]) -> None:
    """
    Step 3: Organize filtered files into TOC and non-TOC folders.
    """
    print("\n📁 Step 3: File Organization")
    print("=" * 50)
    
    if not filter_results:
        print("❌ No filter results available. Step 2 must complete successfully first.")
        return
    
    try:
        # Initialize filter tool for organization
        filter_tool = TOCScreenshotFilter()
        
        if AUTO_ORGANIZE:
            print("🗂️ Automatically organizing files...")
            
            # Organize files
            filter_tool.organize_filtered_results(filter_results, organize_files=True)
            
            print("✅ Files organized successfully!")
        else:
            print("📋 File organization preview (not moving files):")
            filter_tool.organize_filtered_results(filter_results, organize_files=False)
        
        # Save detailed report
        report_file = "toc_analysis_report.json"
        filter_tool.save_analysis_report(filter_results, report_file)
        print(f"💾 Detailed report saved: {report_file}")
        
        # Display organization summary
        print("\n📊 Final Organization Summary:")
        print("-" * 60)
        
        for isbn, results in filter_results['processed_isbns'].items():
            if 'error' in results:
                print(f"❌ {isbn}: {results['error']}")
                continue
            
            toc_count = len(results['toc_pages'])
            non_toc_count = len(results['non_toc_pages'])
            total_count = results['total_screenshots']
            
            print(f"📖 {isbn}:")
            print(f"   📄 Total pages: {total_count}")
            print(f"   ✅ TOC pages: {toc_count} → screenshots/{isbn}/toc_pages/")
            print(f"   ❌ Other pages: {non_toc_count} → screenshots/{isbn}/non_toc_pages/")
            
            if toc_count > 0:
                print("   📑 TOC files:")
                for page in results['toc_pages']:
                    conf = page['confidence']
                    print(f"      • {page['filename']} (confidence: {conf:.2f})")
            print()
        
        summary = filter_results['summary']
        print(f"🎯 Step 3 Complete!")
        print(f"   📚 Books processed: {summary['total_books_processed']}")
        print(f"   📄 Pages analyzed: {summary['total_screenshots_analyzed']}")
        print(f"   ✅ TOC pages found: {summary['total_toc_pages_found']}")
        print(f"   💰 AI analysis cost: ${summary['estimated_cost']:.4f}")
        
    except Exception as e:
        print(f"❌ File organization failed: {e}")

def display_final_summary(screenshot_results, filter_results):
    """
    Display final workflow summary and next steps.
    """
    print("\n🎉 Complete Livebook TOC Extraction Workflow - FINISHED!")
    print("=" * 70)
    
    if not screenshot_results:
        print("❌ Screenshot capture was not successful")
        return
    
    if not filter_results:
        print("❌ AI filtering was not successful")
        return
    
    # Success! Show complete summary
    summary = filter_results['summary']
    
    print(f"✅ Workflow completed successfully!")
    print(f"\n📊 Final Results:")
    print(f"   📚 Books processed: {summary['total_books_processed']}")
    print(f"   📄 Screenshots captured: {summary['total_screenshots_analyzed']}")
    print(f"   🎯 TOC pages identified: {summary['total_toc_pages_found']}")
    print(f"   💰 Total AI cost: ${summary['estimated_cost']:.4f}")
    
    print(f"\n📁 Your organized files are available in:")
    for isbn in ISBN_LIST:
        isbn_dir = Path(f"screenshots/{isbn}")
        if isbn_dir.exists():
            toc_dir = isbn_dir / "toc_pages"
            non_toc_dir = isbn_dir / "non_toc_pages"
            
            if toc_dir.exists():
                toc_files = list(toc_dir.glob("*.png"))
                print(f"   📖 {isbn}:")
                print(f"      ✅ TOC pages: {len(toc_files)} files in {toc_dir}")
                if non_toc_dir.exists():
                    non_toc_files = list(non_toc_dir.glob("*.png"))
                    print(f"      📄 Other pages: {len(non_toc_files)} files in {non_toc_dir}")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Review TOC pages in the toc_pages/ folders")
    print(f"   2. Check the detailed report: toc_analysis_report.json")
    print(f"   3. Use the TOC screenshots for your project")
    
    print(f"\n💡 To run this workflow again:")
    print(f"   1. Update the ISBN_LIST in this script")
    print(f"   2. Run: python run_complete_workflow.py")
    
    print(f"\n🎯 Perfect! You now have clean, AI-filtered TOC screenshots!")

def main():
    """
    Run the complete workflow: capture -> filter -> organize.
    """
    print("🚀 Complete Livebook TOC Extraction Workflow")
    print("=" * 60)
    print(f"📋 Processing {len(ISBN_LIST)} ISBNs")
    print(f"📄 Max {MAX_PAGES_PER_BOOK} pages per book")
    print(f"🎯 AI confidence threshold: {CONFIDENCE_THRESHOLD}")
    print()
    
    # Display and check configuration
    if not display_configuration():
        print("❌ Configuration invalid. Please fix and try again.")
        return
    
    print("\n" + "="*60)
    print("Starting 3-step workflow...")
    print("="*60)
    
    # Step 1: Capture screenshots
    screenshot_results = capture_screenshots_step(ISBN_LIST, MAX_PAGES_PER_BOOK)
    if not screenshot_results:
        print("❌ Workflow stopped - screenshot capture failed")
        return
    
    # Step 2: Filter TOC pages with AI
    filter_results = filter_toc_step()
    if not filter_results:
        print("❌ Workflow stopped - AI filtering failed")
        return
    
    # Step 3: Organize files
    organize_files_step(filter_results)
    
    # Final summary
    display_final_summary(screenshot_results, filter_results)

if __name__ == "__main__":
    main() 