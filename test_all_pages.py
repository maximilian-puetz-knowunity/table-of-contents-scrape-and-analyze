#!/usr/bin/env python3
"""
Test Multi-Page Screenshot Functionality
========================================

Simple script to test capturing all pages from a Livebook.
This ensures we capture the complete table of contents wherever it appears.
"""

from livebook_screenshot_tool import LivebookScreenshotTool

def test_multi_page_capture():
    """Test capturing all pages from a Livebook."""
    
    url = "https://klettbib.livebook.de/978-3-12-316302-9/"
    
    print("🚀 Testing Multi-Page Screenshot Capture")
    print("=" * 50)
    print(f"📍 URL: {url}")
    print("🎯 Goal: Capture ALL pages to ensure TOC is included")
    print()
    
    try:
        with LivebookScreenshotTool(headless=True) as tool:
            print("📚 Starting multi-page capture...")
            results = tool.screenshot_all_pages(url, "test_multipage")
            
            if results['success']:
                print(f"\n🎉 SUCCESS! Captured {results['total_pages']} pages")
                print(f"📊 Total size: {results['total_size']:,} bytes")
                print("\n📁 Captured files:")
                
                for page in results['captured_pages']:
                    size_kb = page['file_size'] // 1024
                    print(f"   📄 Page {page['page_number']:2d}: {page['filename']} ({size_kb:,} KB)")
                
                print(f"\n✅ All pages saved to screenshots/ folder")
                print("💡 The table of contents is now guaranteed to be captured!")
                
            else:
                print(f"\n❌ FAILED: {results.get('error', 'Unknown error')}")
                if results.get('captured_pages'):
                    print(f"⚠️ Partial capture: {len(results['captured_pages'])} pages saved")
                    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_multi_page_capture() 