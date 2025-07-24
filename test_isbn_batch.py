#!/usr/bin/env python3
"""
Test ISBN Batch Processing
==========================

Test script to demonstrate capturing all pages for multiple ISBNs,
with each book's screenshots saved in separate directories.
"""

from livebook_screenshot_tool import LivebookScreenshotTool
import os

def test_isbn_batch():
    """Test ISBN batch processing with directory organization."""
    
    # Example ISBNs (replace with your actual list)
    isbn_list = [
        "978-3-12-316302-9",
        # Add more ISBNs here for testing:
        # "978-3-12-123456-7",
        # "978-3-12-789012-3",
    ]
    
    print("📚 Testing ISBN Batch Processing")
    print("=" * 50)
    print(f"📋 ISBNs to process: {len(isbn_list)}")
    print(f"📄 Max pages per book: 10")
    print()
    
    for i, isbn in enumerate(isbn_list, 1):
        print(f"  {i}. {isbn}")
    print()
    
    def progress_callback(current, total, isbn):
        """Progress callback for batch processing."""
        percent = (current + 1) / total * 100
        print(f"📊 Progress: {percent:.1f}% - Processing {isbn}")
    
    try:
        with LivebookScreenshotTool(headless=True) as tool:
            print("🚀 Starting batch processing...")
            results = tool.screenshot_isbn_batch(
                isbn_list=isbn_list,
                max_pages=10,  # Stop after 10 pages as requested
                progress_callback=progress_callback
            )
            
            print("\n🎉 Batch processing completed!")
            print("\n📊 Results Summary:")
            print("-" * 50)
            
            successful_books = 0
            total_pages = 0
            total_size = 0
            
            for isbn, result in results.items():
                if result['success']:
                    successful_books += 1
                    pages = result['total_pages']
                    size = result['total_size']
                    total_pages += pages
                    total_size += size
                    
                    print(f"✅ {isbn}:")
                    print(f"   📄 Pages: {pages}")
                    print(f"   💾 Size: {size / (1024 * 1024):.1f} MB")
                    print(f"   📁 Directory: screenshots/{isbn}/")
                    
                    # List captured files
                    isbn_dir = f"screenshots/{isbn}"
                    if os.path.exists(isbn_dir):
                        files = sorted([f for f in os.listdir(isbn_dir) if f.endswith('.png')])
                        for file in files[:3]:  # Show first 3 files
                            print(f"      📄 {file}")
                        if len(files) > 3:
                            print(f"      ... and {len(files) - 3} more files")
                else:
                    print(f"❌ {isbn}: {result.get('error', 'Failed')}")
                
                print()
            
            print(f"📋 Final Summary:")
            print(f"   📚 Books processed: {len(isbn_list)}")
            print(f"   ✅ Successful: {successful_books}")
            print(f"   ❌ Failed: {len(isbn_list) - successful_books}")
            print(f"   📄 Total pages: {total_pages}")
            print(f"   💾 Total size: {total_size / (1024 * 1024):.1f} MB")
            
            print(f"\n📁 Each book's screenshots are organized in:")
            for isbn in isbn_list:
                print(f"   screenshots/{isbn}/")
            
            return results
            
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
        return None

if __name__ == "__main__":
    test_isbn_batch() 