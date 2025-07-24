#!/usr/bin/env python3
"""
Livebook Screenshot Tool
======================

A robust Python tool for automatically capturing table of contents screenshots 
from Livebook educational platforms with comprehensive error handling and 
multiple operation modes.

Author: Senior Python Developer
Version: 1.0.0
"""

import os
import time
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import (
        TimeoutException, 
        NoSuchElementException, 
        WebDriverException,
        ElementNotInteractableException
    )
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError as e:
    raise ImportError(
        f"Required dependencies not installed: {e}\n"
        "Please install with: pip install selenium webdriver-manager"
    )


class LivebookScreenshotError(Exception):
    """Custom exception for Livebook screenshot operations."""
    pass


class LivebookScreenshotTool:
    """
    A comprehensive tool for capturing table of contents screenshots from Livebook platforms.
    
    Features:
    - Automatic ChromeDriver management
    - German language TOC detection
    - Element-specific screenshots
    - Headless and visible browser modes
    - Comprehensive error handling
    - Logging support
    """
    
    def __init__(self, headless: bool = True, window_size: Tuple[int, int] = (1920, 1080)):
        """
        Initialize the LivebookScreenshotTool.
        
        Args:
            headless (bool): Whether to run browser in headless mode
            window_size (Tuple[int, int]): Browser window size (width, height)
        """
        self.headless = headless
        self.window_size = window_size
        self.driver = None
        self.wait = None
        
        # Configure logging
        self._setup_logging()
        
        # TOC selectors for German Livebook platforms
        self.toc_selectors = [
            # Primary "Inhalt" selectors (most common in Livebooks)
            "//h1[contains(text(), 'Inhalt')]/..",
            "//h2[contains(text(), 'Inhalt')]/..",
            "//h3[contains(text(), 'Inhalt')]/..",
            "//div[contains(text(), 'Inhalt')]/..",
            "//span[contains(text(), 'Inhalt')]/../..",
            # Traditional "Inhaltsverzeichnis" selectors
            "//h1[contains(text(), 'Inhaltsverzeichnis')]/..",
            "//h2[contains(text(), 'Inhaltsverzeichnis')]/..",
            "//h3[contains(text(), 'Inhaltsverzeichnis')]/..",
            "//div[contains(text(), 'Inhaltsverzeichnis')]/..",
            "//span[contains(text(), 'Inhaltsverzeichnis')]/../..",
            # Class-based selectors
            "//div[contains(@class, 'toc')]",
            "//div[contains(@class, 'table-of-contents')]",
            "//div[contains(@class, 'inhaltsverzeichnis')]",
            "//div[contains(@class, 'inhalt')]",
            "//nav[contains(@class, 'toc')]",
            "//section[contains(@class, 'toc')]"
        ]
        
        self.logger.info(f"Initialized LivebookScreenshotTool - Headless: {headless}, Window: {window_size}")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _setup_driver(self) -> None:
        """Setup Chrome WebDriver with optimized options."""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Performance and stability options
            chrome_options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Faster loading
            # chrome_options.add_argument("--disable-javascript")  # Keep JS enabled for Livebook
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Install and setup ChromeDriver automatically
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            
            self.logger.info("Chrome WebDriver setup successful")
            
        except Exception as e:
            error_msg = f"Failed to setup Chrome WebDriver: {str(e)}"
            self.logger.error(error_msg)
            raise LivebookScreenshotError(error_msg)
    
    def _find_toc_element(self) -> Optional[Any]:
        """
        Find the table of contents element using multiple selectors and navigation.
        
        Returns:
            WebElement or None: The TOC element if found
        """
        # First try to find TOC on current page
        toc_element = self._find_toc_on_current_page()
        if toc_element:
            return toc_element
        
        # If not found, try to navigate to TOC page
        self.logger.info("TOC not found on current page, attempting navigation...")
        if self._navigate_to_toc_page():
            time.sleep(3)  # Wait for page to load after navigation
            toc_element = self._find_toc_on_current_page()
            if toc_element:
                self.logger.info("Found TOC after navigation")
                return toc_element
        
        self.logger.warning("No TOC element found even after navigation attempts")
        return None
    
    def _find_toc_on_current_page(self) -> Optional[Any]:
        """Find TOC element on the current page."""
        for selector in self.toc_selectors:
            try:
                self.logger.debug(f"Trying selector: {selector}")
                elements = self.driver.find_elements(By.XPATH, selector)
                
                if elements:
                    # Filter elements by size and visibility
                    for element in elements:
                        if element.is_displayed() and element.size['height'] > 50:
                            self.logger.info(f"Found TOC element with selector: {selector}")
                            return element
                            
            except Exception as e:
                self.logger.debug(f"Selector {selector} failed: {str(e)}")
                continue
        
        return None
    
    def _navigate_to_toc_page(self) -> bool:
        """Attempt to navigate to the TOC page using various methods."""
        navigation_strategies = [
            self._click_toc_button,
            self._click_inhalt_button,
            self._try_keyboard_navigation,
            self._try_page_navigation
        ]
        
        for strategy in navigation_strategies:
            try:
                if strategy():
                    self.logger.info(f"Navigation successful with {strategy.__name__}")
                    return True
            except Exception as e:
                self.logger.debug(f"Navigation strategy {strategy.__name__} failed: {e}")
                continue
        
        return False
    
    def _click_toc_button(self) -> bool:
        """Try to click TOC/Inhaltsverzeichnis buttons."""
        button_selectors = [
            "//button[contains(text(), 'Inhalt')]",
            "//button[contains(text(), 'Inhaltsverzeichnis')]",
            "//a[contains(text(), 'Inhalt')]",
            "//a[contains(text(), 'Inhaltsverzeichnis')]",
            "//div[contains(@class, 'inhaltsverzeichnis') and @role='button']",
            "//div[contains(@class, 'toc') and @role='button']",
            "*[title*='Inhalt']",
            "*[title*='Inhaltsverzeichnis']"
        ]
        
        for selector in button_selectors:
            try:
                buttons = self.driver.find_elements(By.XPATH, selector)
                for button in buttons:
                    if button.is_enabled():
                        self.logger.info(f"Clicking TOC button: {selector}")
                        self.driver.execute_script("arguments[0].click();", button)
                        return True
            except Exception:
                continue
        return False
    
    def _click_inhalt_button(self) -> bool:
        """Try to click any clickable element containing 'Inhalt'."""
        try:
            clickable_elements = self.driver.find_elements(
                By.XPATH, 
                "//*[contains(text(), 'Inhalt') and (self::button or self::a or @onclick or @role='button')]"
            )
            
            for element in clickable_elements:
                if element.is_displayed() and element.is_enabled():
                    self.logger.info("Clicking Inhalt element")
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
        except Exception:
            pass
        return False
    
    def _try_keyboard_navigation(self) -> bool:
        """Try keyboard shortcuts that might navigate to TOC."""
        try:
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.action_chains import ActionChains
            
            # Try common TOC keyboard shortcuts
            actions = ActionChains(self.driver)
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # Try 'i' for index/inhalt
            actions.click(body).send_keys('i').perform()
            time.sleep(1)
            
            # Try 't' for table of contents
            actions.send_keys('t').perform()
            time.sleep(1)
            
            return True
        except Exception:
            return False
    
    def _try_page_navigation(self) -> bool:
        """Try navigating through pages to find TOC."""
        try:
            # Look for common navigation elements
            nav_selectors = [
                "//button[contains(@aria-label, 'first') or contains(@title, 'first')]",
                "//button[contains(@aria-label, 'beginning') or contains(@title, 'beginning')]",
                "//a[contains(@href, 'page=1') or contains(@href, 'p=1')]",
                "//button[contains(text(), '1')]",
                "//button[@aria-label='Go to first page']"
            ]
            
            for selector in nav_selectors:
                try:
                    nav_buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in nav_buttons:
                        if button.is_displayed() and button.is_enabled():
                            self.logger.info(f"Clicking navigation button: {selector}")
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(2)
                            return True
                except Exception:
                    continue
                    
            return False
        except Exception:
            return False
    
    def _wait_for_page_load(self, timeout: int = 30) -> bool:
        """
        Wait for page to fully load.
        
        Args:
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if page loaded successfully
        """
        try:
            # Wait for document ready state
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            self.logger.info("Page loaded successfully")
            return True
            
        except TimeoutException:
            self.logger.warning(f"Page load timeout after {timeout} seconds")
            return False
    
    def _create_output_directory(self, filename: str, custom_dir: str = None) -> str:
        """
        Create output directory if it doesn't exist and return full path.
        
        Args:
            filename (str): Output filename
            custom_dir (str): Custom directory path (optional)
            
        Returns:
            str: Full path to output file
        """
        if custom_dir:
            output_dir = Path(custom_dir)
        else:
            output_dir = Path("screenshots")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Add timestamp if filename doesn't have extension
        if not Path(filename).suffix:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}.png"
        elif not filename.endswith('.png'):
            filename = f"{filename}.png"
        
        return str(output_dir / filename)
    
    def screenshot_livebook_toc(self, url: str, filename: str, retry_count: int = 3, full_page: bool = True) -> bool:
        """
        Capture a screenshot from a Livebook URL.
        
        Args:
            url (str): The Livebook URL to capture
            filename (str): Output filename for the screenshot
            retry_count (int): Number of retry attempts
            full_page (bool): If True, capture full page; if False, try to find TOC element
            
        Returns:
            bool: True if screenshot was captured successfully
            
        Raises:
            LivebookScreenshotError: If screenshot capture fails
        """
        if not url or not filename:
            raise LivebookScreenshotError("URL and filename are required")
        
        full_path = self._create_output_directory(filename)
        
        for attempt in range(retry_count):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{retry_count}: Capturing screenshot of {url}")
                
                # Setup driver if not already done
                if not self.driver:
                    self._setup_driver()
                
                # Navigate to URL
                self.logger.info(f"Navigating to: {url}")
                self.driver.get(url)
                
                # Wait for page to load
                if not self._wait_for_page_load():
                    self.logger.warning("Page may not have loaded completely")
                
                if full_page:
                    # Simple full page screenshot
                    self.logger.info(f"Capturing full page screenshot to: {full_path}")
                    success = self.driver.save_screenshot(full_path)
                else:
                    # Try to find specific TOC element
                    toc_element = self._find_toc_element()
                    
                    if not toc_element:
                        # Fallback: try to find any content that might be TOC
                        self.logger.info("Trying fallback TOC detection methods")
                        
                        # Try finding elements with specific text patterns
                        fallback_selectors = [
                            "//div[contains(., 'Inhalt')]",
                            "//div[contains(., 'Kapitel')]",
                            "//ul[contains(@class, 'list')]",
                            "//div[contains(@class, 'content')]"
                        ]
                        
                        for selector in fallback_selectors:
                            try:
                                elements = self.driver.find_elements(By.XPATH, selector)
                                for element in elements:
                                    if element.is_displayed() and element.size['height'] > 100:
                                        toc_element = element
                                        self.logger.info(f"Found TOC with fallback selector: {selector}")
                                        break
                                if toc_element:
                                    break
                            except Exception:
                                continue
                    
                    if not toc_element:
                        if attempt < retry_count - 1:
                            self.logger.warning(f"TOC element not found, retrying in 5 seconds...")
                            time.sleep(5)
                            continue
                        else:
                            self.logger.warning("TOC element not found, falling back to full page screenshot")
                            success = self.driver.save_screenshot(full_path)
                    else:
                        # Scroll element into view and capture element screenshot
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", toc_element)
                        time.sleep(2)
                        self.logger.info(f"Capturing TOC element screenshot to: {full_path}")
                        success = toc_element.screenshot(full_path)
                
                if success and os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    self.logger.info(f"Screenshot captured successfully: {full_path} ({file_size} bytes)")
                    return True
                else:
                    raise LivebookScreenshotError("Screenshot capture failed - file not created")
                    
            except LivebookScreenshotError:
                raise
            except Exception as e:
                error_msg = f"Unexpected error during screenshot capture: {str(e)}"
                self.logger.error(error_msg)
                
                if attempt < retry_count - 1:
                    self.logger.info(f"Retrying in 5 seconds...")
                    time.sleep(5)
                    # Reset driver on error
                    self.close()
                else:
                    raise LivebookScreenshotError(error_msg)
        
        return False
    
    def screenshot_multiple_urls(self, url_filename_pairs: list, progress_callback=None, full_page: bool = True) -> Dict[str, bool]:
        """
        Capture screenshots from multiple URLs.
        
        Args:
            url_filename_pairs (list): List of (url, filename) tuples
            progress_callback (callable): Optional callback for progress updates
            full_page (bool): If True, capture full pages; if False, try to find TOC elements
            
        Returns:
            Dict[str, bool]: Results for each URL
        """
        results = {}
        
        for i, (url, filename) in enumerate(url_filename_pairs):
            try:
                if progress_callback:
                    progress_callback(i, len(url_filename_pairs), url)
                
                result = self.screenshot_livebook_toc(url, filename, full_page=full_page)
                results[url] = result
                
            except Exception as e:
                self.logger.error(f"Failed to capture {url}: {str(e)}")
                results[url] = False
        
        return results
    
    def screenshot_isbn_batch(self, isbn_list: list, base_url_template: str = "https://klettbib.livebook.de/{}/", 
                             max_pages: int = 10, progress_callback=None) -> Dict[str, Any]:
        """
        Capture screenshots for a batch of ISBNs, each in its own directory.
        
        Args:
            isbn_list (list): List of ISBN strings
            base_url_template (str): URL template with {} placeholder for ISBN
            max_pages (int): Maximum pages per book (default: 10)
            progress_callback (callable): Optional progress callback function
            
        Returns:
            Dict[str, Any]: Results for each ISBN
        """
        batch_results = {}
        
        for i, isbn in enumerate(isbn_list):
            try:
                if progress_callback:
                    progress_callback(i, len(isbn_list), isbn)
                
                # Create URL from template
                url = base_url_template.format(isbn)
                
                # Create directory for this ISBN
                isbn_dir = f"screenshots/{isbn}"
                
                self.logger.info(f"Processing ISBN {isbn} ({i+1}/{len(isbn_list)})")
                
                # Capture all pages for this book
                results = self.screenshot_all_pages(
                    url=url,
                    base_filename=f"{isbn}",
                    max_pages=max_pages,
                    output_dir=isbn_dir
                )
                
                batch_results[isbn] = results
                
                if results['success']:
                    self.logger.info(f"✅ ISBN {isbn}: {results['total_pages']} pages captured")
                else:
                    self.logger.warning(f"❌ ISBN {isbn}: Failed - {results.get('error', 'Unknown error')}")
                
            except Exception as e:
                error_msg = f"Failed to process ISBN {isbn}: {str(e)}"
                self.logger.error(error_msg)
                batch_results[isbn] = {
                    'success': False,
                    'error': error_msg,
                    'captured_pages': []
                }
        
        return batch_results
    
    def screenshot_all_pages(self, url: str, base_filename: str, max_pages: int = 10, output_dir: str = None) -> Dict[str, Any]:
        """
        Capture screenshots of all pages in a Livebook.
        
        Args:
            url (str): The Livebook URL to capture
            base_filename (str): Base filename for screenshots (will be numbered)
            max_pages (int): Maximum number of pages to capture (default: 10)
            output_dir (str): Custom output directory (default: screenshots/)
            
        Returns:
            Dict[str, Any]: Results with page count and file paths
        """
        if not url or not base_filename:
            raise LivebookScreenshotError("URL and base filename are required")
        
        self.logger.info(f"Starting multi-page screenshot capture for: {url}")
        
        try:
            # Setup driver if not already done
            if not self.driver:
                self._setup_driver()
            
            # Navigate to URL
            self.logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            if not self._wait_for_page_load():
                self.logger.warning("Page may not have loaded completely")
            
            # Try to navigate to first page
            self._navigate_to_first_page()
            
            captured_pages = []
            current_page = 1
            
            while current_page <= max_pages:
                self.logger.info(f"Capturing page {current_page}...")
                
                # Wait a moment for page to stabilize
                time.sleep(2)
                
                # Create filename for this page
                page_filename = f"{base_filename}_page_{current_page:02d}"
                full_path = self._create_output_directory(page_filename, custom_dir=output_dir)
                
                # Capture screenshot of current page
                success = self.driver.save_screenshot(full_path)
                
                if success and os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    self.logger.info(f"Page {current_page} captured: {full_path} ({file_size} bytes)")
                    captured_pages.append({
                        'page_number': current_page,
                        'filename': full_path,
                        'file_size': file_size
                    })
                else:
                    self.logger.warning(f"Failed to capture page {current_page}")
                
                # Try to navigate to next page
                if not self._navigate_to_next_page():
                    self.logger.info(f"No more pages found after page {current_page}")
                    break
                
                current_page += 1
            
            total_pages = len(captured_pages)
            total_size = sum(page['file_size'] for page in captured_pages)
            
            self.logger.info(f"Multi-page capture completed: {total_pages} pages, {total_size:,} bytes total")
            
            return {
                'success': True,
                'total_pages': total_pages,
                'captured_pages': captured_pages,
                'total_size': total_size,
                'base_url': url
            }
            
        except Exception as e:
            error_msg = f"Multi-page screenshot capture failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'captured_pages': captured_pages if 'captured_pages' in locals() else []
            }
    
    def _navigate_to_first_page(self) -> bool:
        """Try to navigate to the first page of the Livebook."""
        first_page_selectors = [
            "//button[contains(@aria-label, 'first') or contains(@title, 'first')]",
            "//button[contains(@aria-label, 'beginning') or contains(@title, 'beginning')]", 
            "//button[contains(@class, 'first')]",
            "//a[contains(@href, 'page=1') or contains(@href, 'p=1')]",
            "//button[text()='1']",
            "//button[@aria-label='Go to first page']",
            "//button[contains(@class, 'pagination') and contains(text(), '1')]"
        ]
        
        for selector in first_page_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        self.logger.info(f"Navigating to first page with: {selector}")
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(2)
                        return True
            except Exception as e:
                self.logger.debug(f"First page navigation failed with {selector}: {e}")
                continue
        
        self.logger.info("No first page navigation found, assuming already on first page")
        return True
    
    def _navigate_to_next_page(self) -> bool:
        """Try to navigate to the next page of the Livebook."""
        next_page_selectors = [
            "//button[contains(@aria-label, 'next') or contains(@title, 'next')]",
            "//button[contains(@aria-label, 'forward') or contains(@title, 'forward')]",
            "//button[contains(@class, 'next')]",
            "//a[contains(@aria-label, 'next')]",
            "//button[@aria-label='Go to next page']",
            "//button[contains(@class, 'pagination-next')]",
            "//button[contains(text(), '►')]",
            "//button[contains(text(), '→')]",
            "//button[contains(text(), 'Next')]",
            # Look for pagination numbers and click the next one
            "//button[contains(@class, 'pagination')][following-sibling::button]",
        ]
        
        # First try standard next buttons
        for selector in next_page_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # Check if button is not disabled
                        disabled = element.get_attribute('disabled')
                        aria_disabled = element.get_attribute('aria-disabled')
                        
                        if not disabled and aria_disabled != 'true':
                            self.logger.info(f"Navigating to next page with: {selector}")
                            self.driver.execute_script("arguments[0].click();", element)
                            time.sleep(3)  # Wait for page to load
                            return True
            except Exception as e:
                self.logger.debug(f"Next page navigation failed with {selector}: {e}")
                continue
        
        # Alternative: try keyboard navigation
        try:
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.action_chains import ActionChains
            
            actions = ActionChains(self.driver)
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # Try right arrow key
            actions.click(body).send_keys(Keys.ARROW_RIGHT).perform()
            time.sleep(2)
            
            # Try page down
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(2)
            
            return True
        except Exception:
            pass
        
        self.logger.info("No next page navigation found")
        return False
    
    def get_page_info(self, url: str) -> Dict[str, Any]:
        """
        Get information about the page structure for debugging.
        
        Args:
            url (str): URL to analyze
            
        Returns:
            Dict[str, Any]: Page information
        """
        if not self.driver:
            self._setup_driver()
        
        try:
            self.driver.get(url)
            self._wait_for_page_load()
            
            info = {
                'title': self.driver.title,
                'url': self.driver.current_url,
                'page_source_length': len(self.driver.page_source),
                'found_elements': {}
            }
            
            # Check each selector
            for selector in self.toc_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    info['found_elements'][selector] = len(elements)
                except Exception:
                    info['found_elements'][selector] = 0
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def close(self) -> None:
        """Close the WebDriver and cleanup resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None
                self.wait = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()


def main():
    """Example usage of the LivebookScreenshotTool."""
    
    # Example URL
    url = "https://klettbib.livebook.de/978-3-12-316302-9/"
    
    try:
        # Create tool instance  
        tool = LivebookScreenshotTool(headless=True)
        
        print("🎯 Choose capture mode:")
        print("1. Single page screenshot")
        print("2. All pages screenshot (recommended for TOC)")
        
        choice = input("Enter choice (1 or 2, default=2): ").strip()
        
        if choice == "1":
            # Single page screenshot
            print("📸 Capturing single page screenshot...")
            success = tool.screenshot_livebook_toc(url, "livebook_single_page", full_page=True)
            
            if success:
                print("✅ Single page screenshot captured successfully!")
                print("📁 Check the 'screenshots' folder for the output file")
            else:
                print("❌ Screenshot capture failed!")
        else:
            # Multi-page screenshot (default and recommended)
            print("📚 Capturing all pages (recommended for TOC)...")
            results = tool.screenshot_all_pages(url, "livebook_all_pages")
            
            if results['success']:
                total_pages = results['total_pages']
                total_size = results['total_size']
                print(f"✅ All pages captured successfully!")
                print(f"📊 Total: {total_pages} pages, {total_size:,} bytes")
                print("📁 Check the 'screenshots' folder for all page files")
                
                # Show captured pages
                for page in results['captured_pages']:
                    print(f"   Page {page['page_number']:2d}: {page['filename']}")
            else:
                print("❌ Multi-page capture failed!")
                if 'error' in results:
                    print(f"Error: {results['error']}")
            
    except LivebookScreenshotError as e:
        print(f"❌ Livebook Screenshot Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    finally:
        tool.close()


if __name__ == "__main__":
    main() 