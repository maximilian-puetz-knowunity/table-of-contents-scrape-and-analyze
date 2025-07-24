#!/usr/bin/env python3
"""
Livebook Screenshot Tool - Usage Examples
========================================

This file demonstrates various usage scenarios for the LivebookScreenshotTool.
Run each example function to see different features and configurations.

Examples included:
1. Basic screenshot capture
2. Multiple URL processing
3. Visible browser mode (for debugging)
4. Error handling and retry mechanisms
5. Page information gathering
6. Batch processing with progress tracking
7. Context manager usage
"""

import time
from typing import List, Tuple
from livebook_screenshot_tool import LivebookScreenshotTool, LivebookScreenshotError


def example_1_basic_usage():
    """
    Example 1: Basic screenshot capture with default settings.
    """
    print("🔸 Example 1: Basic Usage")
    print("-" * 50)
    
    url = "https://klettbib.livebook.de/978-3-12-756141-8/"
    
    try:
        # Create tool with default settings (headless=True)
        tool = LivebookScreenshotTool()
        
        # Capture screenshot
        success = tool.screenshot_livebook_toc(url, "basic_example")
        
        if success:
            print("✅ Screenshot captured successfully!")
            print("📁 Check the 'screenshots' folder for the output file")
        else:
            print("❌ Screenshot capture failed!")
            
    except LivebookScreenshotError as e:
        print(f"❌ Livebook Screenshot Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    finally:
        tool.close()
    
    print("\n")


def example_2_visible_browser():
    """
    Example 2: Run with visible browser for debugging and observation.
    """
    print("🔸 Example 2: Visible Browser Mode")
    print("-" * 50)
    
    url = "https://klettbib.livebook.de/978-3-12-756141-8/"
    
    try:
        # Create tool with visible browser
        tool = LivebookScreenshotTool(headless=False, window_size=(1280, 720))
        
        print("🔍 Browser will open visibly - you can observe the process")
        success = tool.screenshot_livebook_toc(url, "visible_browser_example")
        
        if success:
            print("✅ Screenshot captured successfully!")
        
        # Keep browser open for a moment to observe
        print("⏳ Keeping browser open for 3 seconds for observation...")
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        tool.close()
    
    print("\n")


def example_3_multiple_urls():
    """
    Example 3: Process multiple URLs with progress tracking.
    """
    print("🔸 Example 3: Multiple URLs Processing")
    print("-" * 50)
    
    # Example URLs (you can replace with actual Livebook URLs)
    urls_and_filenames = [
        ("https://klettbib.livebook.de/978-3-12-756141-8/", "book1_toc"),
        ("https://klettbib.livebook.de/978-3-12-756141-8/", "book2_toc"),  # Same URL for demo
        # Add more URLs as needed
    ]
    
    def progress_callback(current: int, total: int, url: str):
        """Progress callback function."""
        progress = (current + 1) / total * 100
        print(f"📊 Progress: {progress:.1f}% ({current + 1}/{total}) - Processing: {url}")
    
    try:
        tool = LivebookScreenshotTool(headless=True)
        
        print(f"🚀 Processing {len(urls_and_filenames)} URLs...")
        results = tool.screenshot_multiple_urls(urls_and_filenames, progress_callback)
        
        # Display results
        print("\n📋 Results Summary:")
        for url, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {status}: {url}")
        
        successful_count = sum(results.values())
        print(f"\n🎯 Summary: {successful_count}/{len(results)} screenshots captured successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        tool.close()
    
    print("\n")


def example_4_error_handling():
    """
    Example 4: Demonstrate error handling and retry mechanisms.
    """
    print("🔸 Example 4: Error Handling and Retry")
    print("-" * 50)
    
    # Test with a potentially problematic URL
    invalid_url = "https://example.com/nonexistent-page"
    valid_url = "https://klettbib.livebook.de/978-3-12-756141-8/"
    
    tool = LivebookScreenshotTool(headless=True)
    
    try:
        # Test 1: Invalid URL (should fail gracefully)
        print("🧪 Test 1: Invalid URL handling")
        try:
            success = tool.screenshot_livebook_toc(invalid_url, "invalid_test", retry_count=2)
            print(f"Result: {'Success' if success else 'Failed as expected'}")
        except LivebookScreenshotError as e:
            print(f"Handled error gracefully: {e}")
        
        print()
        
        # Test 2: Valid URL with retry mechanism
        print("🧪 Test 2: Valid URL with retry mechanism")
        success = tool.screenshot_livebook_toc(valid_url, "retry_test", retry_count=3)
        print(f"Result: {'✅ Success' if success else '❌ Failed'}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        tool.close()
    
    print("\n")


def example_5_page_information():
    """
    Example 5: Get page information for debugging.
    """
    print("🔸 Example 5: Page Information Gathering")
    print("-" * 50)
    
    url = "https://klettbib.livebook.de/978-3-12-756141-8/"
    
    try:
        tool = LivebookScreenshotTool(headless=True)
        
        print("🔍 Gathering page information for debugging...")
        info = tool.get_page_info(url)
        
        if 'error' in info:
            print(f"❌ Error gathering page info: {info['error']}")
        else:
            print(f"📄 Page Title: {info['title']}")
            print(f"🔗 Current URL: {info['url']}")
            print(f"📏 Page Source Length: {info['page_source_length']} characters")
            
            print("\n🎯 TOC Element Detection Results:")
            for selector, count in info['found_elements'].items():
                status = "✅" if count > 0 else "❌"
                print(f"  {status} {selector}: {count} elements found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        tool.close()
    
    print("\n")


def example_6_context_manager():
    """
    Example 6: Using the tool as a context manager for automatic cleanup.
    """
    print("🔸 Example 6: Context Manager Usage")
    print("-" * 50)
    
    url = "https://klettbib.livebook.de/978-3-12-756141-8/"
    
    try:
        # Using the tool as a context manager ensures automatic cleanup
        with LivebookScreenshotTool(headless=True) as tool:
            print("🔧 Tool initialized with automatic cleanup")
            
            success = tool.screenshot_livebook_toc(url, "context_manager_example")
            
            if success:
                print("✅ Screenshot captured successfully!")
            
            # Tool will be automatically closed when exiting the context
        
        print("🧹 Tool automatically cleaned up (browser closed)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")


def example_7_batch_processing():
    """
    Example 7: Advanced batch processing with custom configuration.
    """
    print("🔸 Example 7: Advanced Batch Processing")
    print("-" * 50)
    
    # Example batch configuration
    batch_config = {
        'headless': True,
        'window_size': (1920, 1080),
        'retry_count': 2
    }
    
    # Multiple book URLs (replace with actual URLs)
    book_urls = [
        ("https://klettbib.livebook.de/978-3-12-756141-8/", "math_book_toc"),
        # Add more books here
    ]
    
    try:
        with LivebookScreenshotTool(**batch_config) as tool:
            print(f"🚀 Starting batch processing of {len(book_urls)} books...")
            
            successful_captures = 0
            failed_captures = 0
            
            for i, (url, filename) in enumerate(book_urls, 1):
                print(f"\n📖 Processing book {i}/{len(book_urls)}: {url}")
                
                try:
                    success = tool.screenshot_livebook_toc(
                        url, 
                        f"batch_{i:02d}_{filename}",
                        retry_count=batch_config['retry_count']
                    )
                    
                    if success:
                        successful_captures += 1
                        print(f"✅ Book {i} completed successfully")
                    else:
                        failed_captures += 1
                        print(f"❌ Book {i} failed")
                        
                except Exception as e:
                    failed_captures += 1
                    print(f"❌ Book {i} error: {e}")
                
                # Brief pause between captures
                if i < len(book_urls):
                    time.sleep(2)
            
            # Final summary
            print(f"\n📊 Batch Processing Complete!")
            print(f"✅ Successful: {successful_captures}")
            print(f"❌ Failed: {failed_captures}")
            print(f"📁 Check 'screenshots' folder for captured images")
    
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
    
    print("\n")


def run_all_examples():
    """
    Run all examples in sequence.
    """
    print("🎯 Running All Livebook Screenshot Tool Examples")
    print("=" * 60)
    print()
    
    examples = [
        example_1_basic_usage,
        example_2_visible_browser,
        example_3_multiple_urls,
        example_4_error_handling,
        example_5_page_information,
        example_6_context_manager,
        example_7_batch_processing
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except KeyboardInterrupt:
            print("⏹️ Examples interrupted by user")
            break
        except Exception as e:
            print(f"❌ Example {i} failed with error: {e}")
            print()
        
        # Pause between examples
        if i < len(examples):
            print("⏳ Pausing 3 seconds between examples...")
            time.sleep(3)
    
    print("🏁 All examples completed!")


def main():
    """
    Main function to run specific examples or all examples.
    """
    print("Livebook Screenshot Tool - Usage Examples")
    print("=" * 50)
    print()
    print("Available examples:")
    print("1. Basic Usage")
    print("2. Visible Browser Mode")
    print("3. Multiple URLs Processing")
    print("4. Error Handling")
    print("5. Page Information")
    print("6. Context Manager")
    print("7. Batch Processing")
    print("8. Run All Examples")
    print()
    
    try:
        choice = input("Enter example number (1-8) or press Enter for example 1: ").strip()
        
        if not choice:
            choice = "1"
        
        examples_map = {
            "1": example_1_basic_usage,
            "2": example_2_visible_browser,
            "3": example_3_multiple_urls,
            "4": example_4_error_handling,
            "5": example_5_page_information,
            "6": example_6_context_manager,
            "7": example_7_batch_processing,
            "8": run_all_examples
        }
        
        if choice in examples_map:
            examples_map[choice]()
        else:
            print("❌ Invalid choice. Running basic example...")
            example_1_basic_usage()
    
    except KeyboardInterrupt:
        print("\n⏹️ Examples interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 