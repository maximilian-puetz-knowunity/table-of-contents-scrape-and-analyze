#!/usr/bin/env python3
"""
Test TOC Filter with Parallel Processing
========================================

Enhanced test script to demonstrate AI-powered TOC filtering
using parallel processing with the screenshots we've already captured.
"""

import os
import time
from filter_toc_screenshots import TOCScreenshotFilter, TOCFilterError

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional for testing

def test_toc_filter():
    """Test the TOC filtering functionality with parallel processing."""
    
    print("🤖 Testing AI-Powered TOC Screenshot Filter (Parallel Processing)")
    print("=" * 75)
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
        print("1. Analyzes all screenshots in screenshots/ directory using parallel workers")
        print("2. Uses GPT-4o mini to identify which pages contain table of contents")
        print("3. Provides confidence scores and reasoning for each analysis")
        print("4. Optionally organizes files into toc_pages/ and non_toc_pages/ folders")
        print("5. Generates a detailed JSON report")
        print("6. Shows performance improvements with parallel processing")
        return
    
    try:
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
        for isbn in isbn_dirs[:5]:  # Show first 5
            print(f"   📖 {isbn}")
        if len(isbn_dirs) > 5:
            print(f"   ... and {len(isbn_dirs) - 5} more")
        print()
        
        # Count total screenshots
        total_screenshots = 0
        for isbn in isbn_dirs:
            isbn_path = os.path.join(screenshots_dir, isbn)
            screenshots = [f for f in os.listdir(isbn_path) if f.endswith('.png')]
            total_screenshots += len(screenshots)
        
        print(f"📄 Total screenshots to analyze: {total_screenshots}")
        
        # Get user preferences for parallel processing
        print("\n🚀 Parallel Processing Options:")
        print("1. Conservative: Process books sequentially, pages in parallel (recommended)")
        print("2. Aggressive: Process books AND pages in parallel (faster, more API usage)")
        print("3. Single-threaded: Traditional sequential processing")
        
        mode = input("\nChoose processing mode (1/2/3, default=1): ").strip()
        
        if mode == "3":
            max_workers = 1
            parallel_books = False
            print("🐌 Using single-threaded processing...")
        elif mode == "2":
            max_workers = 6
            parallel_books = True
            print("🚀 Using aggressive parallel processing...")
        else:
            max_workers = 4
            parallel_books = False
            print("⚡ Using conservative parallel processing...")
        
        # Initialize the filter with parallel processing
        print(f"\n🔧 Initializing TOC filter with {max_workers} workers...")
        filter_tool = TOCScreenshotFilter(max_workers=max_workers, max_calls_per_minute=30)
        
        # Test with a single screenshot first
        test_isbn = isbn_dirs[0]
        test_dir = os.path.join(screenshots_dir, test_isbn)
        test_screenshots = [f for f in os.listdir(test_dir) if f.endswith('.png')]
        
        if test_screenshots:
            print(f"\n🧪 Testing with a single screenshot from {test_isbn}...")
            test_image = os.path.join(test_dir, test_screenshots[0])
            
            print(f"📸 Analyzing: {test_screenshots[0]}")
            start_time = time.time()
            result = filter_tool.analyze_screenshot(test_image)
            analysis_time = time.time() - start_time
            
            print("📊 Single Screenshot Analysis Result:")
            print(f"   Is TOC: {result.get('is_toc', 'Unknown')}")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Analysis time: {analysis_time:.2f}s")
            print(f"   Reasoning: {result.get('reasoning', 'No reasoning provided')}")
            
            if result.get('toc_elements_found'):
                print(f"   TOC Elements: {', '.join(result['toc_elements_found'])}")
            
            print()
        
        # Ask if user wants to continue with full analysis
        estimated_cost = total_screenshots * 0.0015  # Rough estimate
        proceed = input(f"🔍 Analyze ALL {total_screenshots} screenshots? (Est. cost: ${estimated_cost:.4f}) (y/N): ").strip().lower()
        
        if proceed != 'y':
            print("🛑 Analysis stopped. Single test completed successfully!")
            return
        
        # Run full batch analysis with timing
        print(f"\n🚀 Running full batch analysis with {max_workers} workers...")
        print(f"📊 Expected performance gain: ~{min(max_workers, 4)}x faster than sequential")
        
        start_time = time.time()
        results = filter_tool.filter_batch_directories(
            confidence_threshold=0.7,
            parallel_books=parallel_books
        )
        total_time = time.time() - start_time
        
        # Display results
        print(f"\n📊 Full Analysis Results (completed in {total_time:.1f}s):")
        print("-" * 65)
        
        summary = results['summary']
        screenshots_analyzed = summary['total_screenshots_analyzed']
        books_processed = summary['total_books_processed']
        toc_pages_found = summary['total_toc_pages_found']
        
        print(f"📚 Books processed: {books_processed}")
        print(f"📄 Screenshots analyzed: {screenshots_analyzed}")
        print(f"✅ TOC pages found: {toc_pages_found}")
        print(f"❌ Non-TOC pages: {summary['total_non_toc_pages']}")
        print(f"⚡ Total processing time: {total_time:.1f}s")
        print(f"🔧 Workers used: {summary['max_workers']}")
        print(f"📈 Avg. speed: {screenshots_analyzed / total_time:.1f} screenshots/second")
        
        actual_cost = screenshots_analyzed * 0.0015
        print(f"💰 Estimated API cost: ${actual_cost:.4f}")
        
        # Show top results
        print(f"\n📑 Books with Most TOC Pages:")
        print("-" * 50)
        
        # Sort books by TOC page count
        book_toc_counts = []
        for isbn, book_results in results['processed_isbns'].items():
            if 'error' not in book_results:
                toc_count = len(book_results.get('toc_pages', []))
                if toc_count > 0:
                    book_toc_counts.append((isbn, toc_count, book_results))
        
        book_toc_counts.sort(key=lambda x: x[1], reverse=True)
        
        for isbn, toc_count, book_results in book_toc_counts[:10]:  # Top 10
            print(f"📖 {isbn}: {toc_count} TOC pages")
            # Show a few example pages
            for page in book_results['toc_pages'][:2]:
                conf = page['confidence']
                print(f"   ✅ {page['filename']} (confidence: {conf:.2f})")
            if toc_count > 2:
                print(f"   ... and {toc_count - 2} more")
        
        if not book_toc_counts:
            print("❌ No TOC pages found in any books!")
        
        # Save report
        print("\n💾 Saving detailed analysis report...")
        report_filename = f"toc_analysis_report_{int(time.time())}.json"
        filter_tool.save_analysis_report(results, report_filename)
        print(f"✅ Report saved to: {report_filename}")
        
        # File organization with better error handling
        print("\n🗂️ File Organization Options:")
        print("1. Organize files into toc_pages/ and non_toc_pages/ folders")
        print("2. Just show what would be organized (dry run)")
        print("3. Skip organization")
        
        organize_choice = input("\nChoose option (1/2/3, default=3): ").strip()
        
        if organize_choice in ["1", "2"]:
            try:
                organize_files = organize_choice == "1"
                action = "Organizing" if organize_files else "Simulating organization of"
                print(f"📁 {action} files...")
                
                # Enhanced organization with better error handling
                organized_count = 0
                error_count = 0
                
                for isbn, book_results in results['processed_isbns'].items():
                    if 'error' in book_results:
                        print(f"⚠️ Skipping {isbn}: {book_results['error']}")
                        continue
                    
                    try:
                        # Check if we have valid results
                        if 'processed_isbns' not in results:
                            raise TOCFilterError("Invalid batch results format - missing processed_isbns")
                        
                        isbn_dir = os.path.join("screenshots", isbn)
                        if not os.path.exists(isbn_dir):
                            print(f"⚠️ ISBN directory not found: {isbn_dir}")
                            continue
                        
                        toc_pages = book_results.get('toc_pages', [])
                        non_toc_pages = book_results.get('non_toc_pages', [])
                        
                        if organize_files:
                            toc_dir = os.path.join(isbn_dir, "toc_pages")
                            non_toc_dir = os.path.join(isbn_dir, "non_toc_pages")
                            
                            # Create directories
                            os.makedirs(toc_dir, exist_ok=True)
                            os.makedirs(non_toc_dir, exist_ok=True)
                        
                        # Process TOC pages
                        for toc_page in toc_pages:
                            filename = toc_page['filename']
                            source = os.path.join(isbn_dir, filename)
                            target = os.path.join(isbn_dir, "toc_pages", filename)
                            
                            if organize_files and os.path.exists(source):
                                os.rename(source, target)
                                organized_count += 1
                            print(f"{'✅ Moved' if organize_files else '📋 Would move'} TOC: {filename}")
                        
                        # Process non-TOC pages
                        for non_toc_page in non_toc_pages:
                            filename = non_toc_page['filename']
                            source = os.path.join(isbn_dir, filename)
                            target = os.path.join(isbn_dir, "non_toc_pages", filename)
                            
                            if organize_files and os.path.exists(source):
                                os.rename(source, target)
                                organized_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        print(f"❌ Error organizing {isbn}: {e}")
                
                if organize_files:
                    print(f"✅ Organization complete! Moved {organized_count} files")
                    if error_count > 0:
                        print(f"⚠️ {error_count} errors occurred during organization")
                else:
                    print(f"📋 Dry run complete! Would organize {len(book_toc_counts)} books")
                
            except Exception as e:
                print(f"❌ File organization failed: {e}")
                print("💡 You can manually organize files or check the JSON report for details")
        else:
            print("📋 Files not organized. You can run organization later using the main script.")
        
        # Performance summary
        print(f"\n🎯 Performance Summary:")
        print("-" * 40)
        print(f"📊 Screenshots/second: {screenshots_analyzed / total_time:.1f}")
        print(f"⚡ Workers used: {max_workers}")
        print(f"🔧 Processing mode: {'Aggressive' if parallel_books else 'Conservative'}")
        estimated_sequential_time = screenshots_analyzed * 2.0  # Estimate 2s per screenshot
        speedup = estimated_sequential_time / total_time
        print(f"🚀 Estimated speedup: {speedup:.1f}x faster than sequential")
        
    except TOCFilterError as e:
        print(f"❌ TOC Filter Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


def show_usage_info():
    """Show information about using the TOC filter with parallel processing."""
    print("📚 TOC Screenshot Filter - Parallel Processing Usage")
    print("=" * 65)
    print()
    print("🎯 Purpose:")
    print("   Filter screenshots to identify table of contents pages using parallel processing")
    print("   Uses OpenAI GPT-4o mini with vision capabilities for enhanced speed")
    print()
    print("📋 Prerequisites:")
    print("   1. OpenAI API key (set OPENAI_API_KEY environment variable)")
    print("   2. Screenshots from ISBN batch processing")
    print("   3. Install dependencies: pip install openai Pillow")
    print()
    print("🚀 Quick Start:")
    print("   1. Set API key: export OPENAI_API_KEY='your-key'")
    print("   2. Run: python test_toc_filter.py")
    print("   3. Choose parallel processing mode (conservative/aggressive)")
    print("   4. Let the AI analyze all screenshots in parallel")
    print()
    print("💡 New Parallel Features:")
    print("   • Multiple workers analyze screenshots simultaneously")
    print("   • Rate limiting to respect OpenAI API limits")
    print("   • Conservative vs aggressive processing modes")
    print("   • Performance monitoring and speedup calculations")
    print("   • Enhanced error handling and recovery")
    print("   • Dry-run file organization option")
    print()
    print("⚡ Performance Benefits:")
    print("   • 3-6x faster than sequential processing")
    print("   • Configurable worker count (1-8 workers)")
    print("   • Intelligent rate limiting prevents API errors")
    print("   • Real-time progress monitoring")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_usage_info()
    else:
        test_toc_filter() 