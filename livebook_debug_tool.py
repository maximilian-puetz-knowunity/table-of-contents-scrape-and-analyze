#!/usr/bin/env python3
"""
Livebook Debug Tool
==================

A specialized debugging tool to help identify the correct navigation 
and selectors for capturing TOC screenshots from specific Livebooks.

This tool provides interactive debugging and exploration capabilities.
"""

import time
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from livebook_screenshot_tool import LivebookScreenshotTool


class LivebookDebugTool(LivebookScreenshotTool):
    """Extended tool with debugging and exploration capabilities."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug_mode = True
    
    def explore_livebook(self, url: str) -> Dict[str, Any]:
        """
        Comprehensive exploration of a Livebook structure.
        
        Args:
            url: Livebook URL to explore
            
        Returns:
            Dict with exploration results
        """
        print("🔍 Starting comprehensive Livebook exploration...")
        print("=" * 60)
        
        try:
            self._setup_driver()
            self.driver.get(url)
            self._wait_for_page_load()
            
            exploration_results = {
                'basic_info': self._get_basic_page_info(),
                'navigation_elements': self._find_navigation_elements(),
                'potential_toc_elements': self._find_potential_toc_elements(),
                'clickable_elements': self._find_clickable_elements(),
                'page_structure': self._analyze_page_structure()
            }
            
            self._print_exploration_results(exploration_results)
            return exploration_results
            
        except Exception as e:
            print(f"❌ Exploration failed: {e}")
            return {'error': str(e)}
        finally:
            if hasattr(self, 'driver') and self.driver:
                self.close()
    
    def interactive_debug(self, url: str):
        """
        Interactive debugging session with manual control.
        
        Args:
            url: Livebook URL to debug
        """
        print("🎮 Starting interactive debugging session...")
        print("=" * 60)
        print("Browser will open in visible mode for manual exploration.")
        print("You can manually navigate while the tool analyzes the page.")
        
        # Force visible mode for debugging
        original_headless = self.headless
        self.headless = False
        
        try:
            self._setup_driver()
            self.driver.get(url)
            self._wait_for_page_load()
            
            print("\n📋 Interactive Commands:")
            print("  - Press Enter to analyze current page")
            print("  - Type 'screenshot' to attempt TOC capture")
            print("  - Type 'nav' to try automatic navigation")
            print("  - Type 'quit' to exit")
            
            while True:
                command = input("\n🎮 Enter command: ").strip().lower()
                
                if command == 'quit':
                    break
                elif command == 'screenshot':
                    self._try_interactive_screenshot()
                elif command == 'nav':
                    self._try_interactive_navigation()
                else:
                    self._analyze_current_page()
                    
        except KeyboardInterrupt:
            print("\n⏹️ Debugging session interrupted")
        except Exception as e:
            print(f"❌ Debug session failed: {e}")
        finally:
            self.headless = original_headless
            self.close()
    
    def test_navigation_strategies(self, url: str) -> Dict[str, bool]:
        """
        Test all navigation strategies and report results.
        
        Args:
            url: Livebook URL to test
            
        Returns:
            Dict with strategy results
        """
        print("🧪 Testing all navigation strategies...")
        print("=" * 60)
        
        self.headless = False  # Visible for testing
        results = {}
        
        try:
            self._setup_driver()
            self.driver.get(url)
            self._wait_for_page_load()
            
            strategies = [
                ('click_toc_button', self._click_toc_button),
                ('click_inhalt_button', self._click_inhalt_button),
                ('keyboard_navigation', self._try_keyboard_navigation),
                ('page_navigation', self._try_page_navigation)
            ]
            
            for name, strategy in strategies:
                print(f"\n🔧 Testing {name}...")
                try:
                    # Reset to initial page
                    self.driver.get(url)
                    self._wait_for_page_load()
                    
                    success = strategy()
                    results[name] = success
                    
                    if success:
                        print(f"  ✅ {name} - SUCCESS")
                        time.sleep(3)  # Give time to observe
                        
                        # Check if TOC is now visible
                        toc_element = self._find_toc_on_current_page()
                        if toc_element:
                            print(f"  🎯 TOC element found after {name}!")
                        else:
                            print(f"  ⚠️ Navigation successful but no TOC found")
                    else:
                        print(f"  ❌ {name} - FAILED")
                        
                except Exception as e:
                    print(f"  💥 {name} - ERROR: {e}")
                    results[name] = False
            
            return results
            
        except Exception as e:
            print(f"❌ Strategy testing failed: {e}")
            return {'error': str(e)}
        finally:
            input("Press Enter to close browser...")
            self.close()
    
    def _get_basic_page_info(self) -> Dict[str, Any]:
        """Get basic information about the current page."""
        return {
            'title': self.driver.title,
            'url': self.driver.current_url,
            'page_source_length': len(self.driver.page_source)
        }
    
    def _find_navigation_elements(self) -> List[Dict[str, Any]]:
        """Find potential navigation elements."""
        nav_selectors = [
            "//button",
            "//a[@href]",
            "//*[@role='button']",
            "//*[contains(@class, 'nav')]",
            "//*[contains(@class, 'toolbar')]",
            "//*[contains(@class, 'menu')]"
        ]
        
        nav_elements = []
        for selector in nav_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for elem in elements[:5]:  # Limit to first 5 of each type
                    if elem.is_displayed():
                        nav_elements.append({
                            'selector': selector,
                            'tag': elem.tag_name,
                            'text': elem.text[:50],
                            'class': elem.get_attribute('class'),
                            'title': elem.get_attribute('title'),
                            'href': elem.get_attribute('href')
                        })
            except Exception:
                continue
        
        return nav_elements
    
    def _find_potential_toc_elements(self) -> List[Dict[str, Any]]:
        """Find elements that might contain TOC content."""
        toc_patterns = [
            'inhalt', 'inhaltsverzeichnis', 'contents', 'toc', 'index',
            'kapitel', 'chapter', 'section', 'übersicht', 'overview'
        ]
        
        potential_elements = []
        
        for pattern in toc_patterns:
            # Text-based search
            text_elements = self.driver.find_elements(
                By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{pattern}')]"
            )
            
            # Class-based search
            class_elements = self.driver.find_elements(
                By.XPATH, f"//*[contains(@class, '{pattern}')]"
            )
            
            for elements, search_type in [(text_elements, 'text'), (class_elements, 'class')]:
                for elem in elements[:3]:  # Limit results
                    try:
                        potential_elements.append({
                            'pattern': pattern,
                            'search_type': search_type,
                            'tag': elem.tag_name,
                            'text': elem.text[:100],
                            'class': elem.get_attribute('class'),
                            'size': elem.size,
                            'displayed': elem.is_displayed(),
                            'location': elem.location
                        })
                    except Exception:
                        continue
        
        return potential_elements
    
    def _find_clickable_elements(self) -> List[Dict[str, Any]]:
        """Find clickable elements that might navigate to TOC."""
        clickable_selectors = [
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'inhalt')]",
            "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'inhalt')]",
            "//*[@title and contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'inhalt')]",
            "//button[contains(@class, 'toc') or contains(@class, 'inhalt')]"
        ]
        
        clickable_elements = []
        for selector in clickable_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        clickable_elements.append({
                            'selector': selector,
                            'tag': elem.tag_name,
                            'text': elem.text,
                            'class': elem.get_attribute('class'),
                            'title': elem.get_attribute('title'),
                            'onclick': elem.get_attribute('onclick')
                        })
            except Exception:
                continue
        
        return clickable_elements
    
    def _analyze_page_structure(self) -> Dict[str, Any]:
        """Analyze overall page structure."""
        structure = {
            'total_elements': len(self.driver.find_elements(By.XPATH, "//*")),
            'buttons': len(self.driver.find_elements(By.TAG_NAME, "button")),
            'links': len(self.driver.find_elements(By.TAG_NAME, "a")),
            'divs': len(self.driver.find_elements(By.TAG_NAME, "div")),
            'forms': len(self.driver.find_elements(By.TAG_NAME, "form")),
            'iframes': len(self.driver.find_elements(By.TAG_NAME, "iframe"))
        }
        
        return structure
    
    def _print_exploration_results(self, results: Dict[str, Any]):
        """Print formatted exploration results."""
        print("\n📊 EXPLORATION RESULTS")
        print("=" * 60)
        
        # Basic info
        basic = results.get('basic_info', {})
        print(f"📄 Title: {basic.get('title', 'N/A')}")
        print(f"🔗 URL: {basic.get('url', 'N/A')}")
        print(f"📏 Page Source: {basic.get('page_source_length', 0):,} characters")
        
        # Page structure
        structure = results.get('page_structure', {})
        print(f"\n🏗️ Page Structure:")
        for element_type, count in structure.items():
            print(f"  {element_type}: {count}")
        
        # Potential TOC elements
        toc_elements = results.get('potential_toc_elements', [])
        print(f"\n🎯 Potential TOC Elements ({len(toc_elements)}):")
        for elem in toc_elements[:10]:  # Show first 10
            print(f"  • {elem['pattern']} ({elem['search_type']}) - {elem['tag']} - {elem['text'][:50]}...")
        
        # Clickable elements
        clickable = results.get('clickable_elements', [])
        print(f"\n🖱️ Clickable TOC Elements ({len(clickable)}):")
        for elem in clickable[:5]:  # Show first 5
            print(f"  • {elem['tag']}: \"{elem['text']}\" (class: {elem['class']})")
        
        # Navigation elements
        nav = results.get('navigation_elements', [])
        print(f"\n🧭 Navigation Elements ({len(nav)}):")
        for elem in nav[:10]:  # Show first 10
            print(f"  • {elem['tag']}: \"{elem['text'][:30]}\" (class: {elem['class']})")
    
    def _try_interactive_screenshot(self):
        """Try to capture TOC screenshot interactively."""
        print("📸 Attempting TOC screenshot capture...")
        try:
            toc_element = self._find_toc_on_current_page()
            if toc_element:
                print("✅ TOC element found! Capturing screenshot...")
                # Create timestamp for unique filename
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"interactive_toc_{timestamp}"
                
                # Scroll element into view and capture
                self.driver.execute_script("arguments[0].scrollIntoView(true);", toc_element)
                time.sleep(1)
                
                success = toc_element.screenshot(f"screenshots/{filename}.png")
                if success:
                    print(f"🎉 Screenshot saved as: screenshots/{filename}.png")
                else:
                    print("❌ Screenshot capture failed")
            else:
                print("⚠️ No TOC element found on current page")
        except Exception as e:
            print(f"❌ Screenshot attempt failed: {e}")
    
    def _try_interactive_navigation(self):
        """Try automatic navigation interactively."""
        print("🧭 Attempting automatic navigation...")
        if self._navigate_to_toc_page():
            print("✅ Navigation successful! Analyzing new page...")
            time.sleep(2)
            self._analyze_current_page()
        else:
            print("❌ Navigation failed")
    
    def _analyze_current_page(self):
        """Analyze the current page state."""
        print("\n🔍 Current Page Analysis:")
        print(f"  URL: {self.driver.current_url}")
        print(f"  Title: {self.driver.title}")
        
        # Quick TOC check
        toc_element = self._find_toc_on_current_page()
        if toc_element:
            print("  ✅ TOC element found!")
            print(f"    Size: {toc_element.size}")
            print(f"    Location: {toc_element.location}")
            print(f"    Text preview: {toc_element.text[:100]}...")
        else:
            print("  ❌ No TOC element found")


def main():
    """Main function with different debugging modes."""
    print("Livebook Debug Tool")
    print("=" * 50)
    print()
    print("Available modes:")
    print("1. Explore - Comprehensive structure analysis")
    print("2. Interactive - Manual debugging session") 
    print("3. Test Navigation - Test all navigation strategies")
    print("4. Quick Test - Test basic functionality")
    print()
    
    try:
        choice = input("Select mode (1-4): ").strip()
        url = input("Enter Livebook URL: ").strip()
        
        if not url:
            url = "https://klettbib.livebook.de/978-3-12-316302-9/"
            print(f"Using default URL: {url}")
        
        debug_tool = LivebookDebugTool(headless=True)
        
        if choice == "1":
            debug_tool.explore_livebook(url)
        elif choice == "2":
            debug_tool.interactive_debug(url)
        elif choice == "3":
            debug_tool.test_navigation_strategies(url)
        elif choice == "4":
            with debug_tool:
                success = debug_tool.screenshot_livebook_toc(url, "debug_test")
                print("✅ Success!" if success else "❌ Failed!")
        else:
            print("Invalid choice. Running exploration mode...")
            debug_tool.explore_livebook(url)
            
    except KeyboardInterrupt:
        print("\n⏹️ Debugging interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 