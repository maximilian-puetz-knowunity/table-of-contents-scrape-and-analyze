#!/usr/bin/env python3
"""
Test Multi-Page Screenshot Functionality
========================================

Simple script to test capturing all pages from a Livebook.
This ensures we capture the complete table of contents wherever it appears.
"""

from livebook_screenshot_tool import LivebookScreenshotTool

def confirm_before_analysis():
    """
    Ask user to check the Google Drive content before proceeding with analysis.
    Returns True if user confirms, False if they cancel.
    """
    print("\n" + "="*60)
    print("📋 IMPORTANT: Before Starting Test Capture")
    print("="*60)
    print()
    print("🔍 Please review the content and instructions at:")
    print("🔗 https://drive.google.com/drive/folders/17xeeabkqmq1hABvsymUSPOusC-Aqbmes?usp=drive_link")
    print()
    print("📖 This contains important information about:")
    print("   • Data collection guidelines")
    print("   • Usage requirements") 
    print("   • Best practices for analysis")
    print("   • Legal and ethical considerations")
    print()
    print("⚠️  Please read through the content in the Google Drive before proceeding.")
    print()
    
    while True:
        response = input("✅ Have you reviewed the content and want to proceed with test capture? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\n✅ Proceeding with test capture...")
            return True
        elif response in ['n', 'no', '']:
            print("\n❌ Test capture cancelled. Please review the content and run again when ready.")
            return False
        else:
            print("⚠️  Please enter 'y' for yes or 'n' for no.")

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
    # Ask user to confirm after reviewing Google Drive content
    if confirm_before_analysis():
        test_multi_page_capture() 