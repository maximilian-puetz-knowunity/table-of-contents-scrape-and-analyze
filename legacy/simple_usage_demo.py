#!/usr/bin/env python3
"""
Simple Livebook Screenshot Demo
==============================

Demonstrates the simplified approach to capturing Livebook screenshots
with both full page (recommended) and element-specific modes.
"""

from livebook_screenshot_tool import LivebookScreenshotTool

def demo_full_page_screenshots():
    """Demonstrate full page screenshot capture (recommended approach)."""
    print("🔸 Demo 1: Full Page Screenshots (Recommended)")
    print("-" * 60)
    
    urls_to_capture = [
        "https://klettbib.livebook.de/978-3-12-316302-9/",
        # Add more URLs here as needed
    ]
    
    with LivebookScreenshotTool(headless=True) as tool:
        for i, url in enumerate(urls_to_capture, 1):
            print(f"📸 Capturing screenshot {i}/{len(urls_to_capture)}: {url}")
            
            success = tool.screenshot_livebook_toc(
                url, 
                f"demo_fullpage_{i:02d}",
                full_page=True  # This is the default
            )
            
            if success:
                print(f"  ✅ Success! Screenshot {i} captured")
            else:
                print(f"  ❌ Failed to capture screenshot {i}")
    
    print("\n🎉 Full page screenshot demo completed!")
    print("📁 Check the 'screenshots' folder for captured images")

def demo_element_specific_screenshots():
    """Demonstrate element-specific screenshot capture (advanced)."""
    print("\n🔸 Demo 2: Element-Specific Screenshots (Advanced)")
    print("-" * 60)
    print("⚠️  This mode tries to find specific TOC elements")
    print("   Falls back to full page if TOC not found")
    
    url = "https://klettbib.livebook.de/978-3-12-316302-9/"
    
    with LivebookScreenshotTool(headless=True) as tool:
        print(f"🔍 Attempting element-specific capture: {url}")
        
        success = tool.screenshot_livebook_toc(
            url, 
            "demo_element_specific",
            full_page=False  # Try to find specific TOC element
        )
        
        if success:
            print("  ✅ Success! Element-specific screenshot captured")
        else:
            print("  ❌ Failed to capture element-specific screenshot")

def demo_batch_processing():
    """Demonstrate batch processing with progress tracking."""
    print("\n🔸 Demo 3: Batch Processing with Progress")
    print("-" * 60)
    
    # Example batch - replace with actual URLs
    batch_urls = [
        ("https://klettbib.livebook.de/978-3-12-316302-9/", "batch_book_1"),
        # Add more (url, filename) pairs here
    ]
    
    def progress_callback(current, total, url):
        percent = (current + 1) / total * 100
        print(f"  📊 Progress: {percent:.1f}% ({current + 1}/{total})")
    
    with LivebookScreenshotTool(headless=True) as tool:
        print(f"🚀 Processing {len(batch_urls)} URLs in batch...")
        
        results = tool.screenshot_multiple_urls(
            batch_urls, 
            progress_callback=progress_callback,
            full_page=True
        )
        
        # Summary
        successful = sum(results.values())
        print(f"\n📊 Batch Results: {successful}/{len(results)} successful")
        
        for url, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {url}")

def demo_different_browser_modes():
    """Demonstrate different browser configurations."""
    print("\n🔸 Demo 4: Different Browser Configurations")
    print("-" * 60)
    
    url = "https://klettbib.livebook.de/978-3-12-316302-9/"
    
    configurations = [
        {"name": "Headless (default)", "headless": True, "window_size": (1920, 1080)},
        {"name": "Large headless", "headless": True, "window_size": (2560, 1440)},
        {"name": "Mobile size", "headless": True, "window_size": (375, 667)},
    ]
    
    for config in configurations:
        print(f"🔧 Testing {config['name']}...")
        
        try:
            with LivebookScreenshotTool(
                headless=config['headless'], 
                window_size=config['window_size']
            ) as tool:
                
                filename = f"demo_{config['name'].lower().replace(' ', '_')}"
                success = tool.screenshot_livebook_toc(url, filename, full_page=True)
                
                if success:
                    print(f"  ✅ {config['name']} - Success!")
                else:
                    print(f"  ❌ {config['name']} - Failed!")
                    
        except Exception as e:
            print(f"  💥 {config['name']} - Error: {e}")

def main():
    """Run all demonstrations."""
    print("Livebook Screenshot Tool - Simple Usage Demo")
    print("=" * 70)
    print("🎯 Demonstrating the simplified approach with full page screenshots")
    print()
    
    try:
        # Run the demonstrations
        demo_full_page_screenshots()
        demo_element_specific_screenshots()
        demo_batch_processing()
        demo_different_browser_modes()
        
        print("\n" + "=" * 70)
        print("🏁 All demonstrations completed!")
        print("📋 Summary:")
        print("  • Full page screenshots: ✅ Simple and reliable")
        print("  • Element detection: ⚠️  Complex, use when needed")
        print("  • Batch processing: ✅ Efficient for multiple URLs")
        print("  • Different configs: ✅ Flexible browser settings")
        print()
        print("💡 Recommendation: Use full_page=True (default) for best results")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main() 