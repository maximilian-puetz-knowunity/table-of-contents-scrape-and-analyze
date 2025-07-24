# Livebook Screenshot Tool - Error Handling Guide

This guide provides comprehensive information about error handling, troubleshooting, and common issues when using the Livebook Screenshot Tool.

## Table of Contents

1. [Error Types](#error-types)
2. [Common Errors](#common-errors)
3. [Troubleshooting Steps](#troubleshooting-steps)
4. [Browser Issues](#browser-issues)
5. [Network Problems](#network-problems)
6. [Element Detection Issues](#element-detection-issues)
7. [Performance Optimization](#performance-optimization)
8. [Logging and Debugging](#logging-and-debugging)

## Error Types

### 1. LivebookScreenshotError

**Custom exception for tool-specific errors**

```python
class LivebookScreenshotError(Exception):
    """Custom exception for Livebook screenshot operations."""
    pass
```

**Common causes:**
- URL validation failures
- TOC element not found
- Screenshot capture failures
- File system errors

**Example handling:**
```python
try:
    tool.screenshot_livebook_toc(url, filename)
except LivebookScreenshotError as e:
    print(f"Livebook Error: {e}")
    # Handle specific error cases
```

### 2. WebDriver Errors

**Selenium WebDriver related errors**

- `WebDriverException`: General WebDriver issues
- `TimeoutException`: Page load or element wait timeouts
- `NoSuchElementException`: Element not found
- `ElementNotInteractableException`: Element cannot be interacted with

### 3. Network Errors

**Connection and HTTP related errors**

- Connection timeouts
- DNS resolution failures
- HTTP status errors (404, 500, etc.)
- SSL certificate issues

## Common Errors

### Error 1: ChromeDriver Installation Failed

**Error Message:**
```
Failed to setup Chrome WebDriver: [Errno 2] No such file or directory: 'chromedriver'
```

**Cause:** ChromeDriver not found or webdriver-manager failed to download it.

**Solutions:**
1. **Check internet connection** - webdriver-manager needs to download ChromeDriver
2. **Clear webdriver cache:**
   ```bash
   rm -rf ~/.wdm/drivers/chromedriver/
   ```
3. **Manual ChromeDriver installation:**
   ```bash
   # Download from https://chromedriver.chromium.org/
   # Place in PATH or use explicit path
   ```
4. **Install specific Chrome version:**
   ```python
   from webdriver_manager.chrome import ChromeDriverManager
   service = Service(ChromeDriverManager(version="114.0.5735.90").install())
   ```

### Error 2: TOC Element Not Found

**Error Message:**
```
Table of contents element not found after all attempts. The page structure might be different than expected.
```

**Cause:** The page doesn't contain recognizable TOC elements.

**Solutions:**
1. **Analyze page structure:**
   ```python
   tool = LivebookScreenshotTool()
   info = tool.get_page_info(url)
   print(info['found_elements'])
   ```
2. **Try visible browser mode for manual inspection:**
   ```python
   tool = LivebookScreenshotTool(headless=False)
   ```
3. **Custom selector implementation:**
   ```python
   # Add custom selectors to tool.toc_selectors
   tool.toc_selectors.append("//your-custom-xpath")
   ```

### Error 3: Page Load Timeout

**Error Message:**
```
Page load timeout after 30 seconds
```

**Cause:** Slow network, heavy page, or server issues.

**Solutions:**
1. **Increase timeout:**
   ```python
   # Modify _wait_for_page_load timeout parameter
   tool._wait_for_page_load(timeout=60)
   ```
2. **Check network connection**
3. **Try different times** - server might be busy
4. **Use lighter browser options:**
   ```python
   # Already included in default setup:
   # --disable-images
   # --disable-javascript
   ```

### Error 4: Screenshot File Not Created

**Error Message:**
```
Screenshot capture failed - file not created
```

**Cause:** Element found but screenshot capture failed.

**Solutions:**
1. **Check element visibility:**
   ```python
   # Element might be hidden or have zero size
   print(f"Element size: {element.size}")
   print(f"Element displayed: {element.is_displayed()}")
   ```
2. **Try scrolling element into view:**
   ```python
   driver.execute_script("arguments[0].scrollIntoView(true);", element)
   ```
3. **Check disk space and permissions**
4. **Use full page screenshot as fallback:**
   ```python
   driver.save_screenshot("fallback.png")
   ```

### Error 5: Permission Denied

**Error Message:**
```
PermissionError: [Errno 13] Permission denied: 'screenshots/filename.png'
```

**Cause:** Insufficient permissions to write to screenshots directory.

**Solutions:**
1. **Check directory permissions:**
   ```bash
   ls -la screenshots/
   chmod 755 screenshots/
   ```
2. **Use different output directory:**
   ```python
   # Modify _create_output_directory method
   output_dir = Path.home() / "Downloads" / "screenshots"
   ```
3. **Run with appropriate permissions**

## Troubleshooting Steps

### Step 1: Basic Diagnostics

```python
def diagnose_environment():
    """Run basic environment diagnostics."""
    import selenium
    import webdriver_manager
    
    print(f"Python version: {sys.version}")
    print(f"Selenium version: {selenium.__version__}")
    print(f"Webdriver-manager version: {webdriver_manager.__version__}")
    
    # Test basic WebDriver setup
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        print(f"ChromeDriver path: {driver_path}")
    except Exception as e:
        print(f"ChromeDriver setup failed: {e}")

# Run diagnostics
diagnose_environment()
```

### Step 2: URL Validation

```python
def validate_livebook_url(url: str) -> bool:
    """Validate if URL is accessible."""
    import requests
    
    try:
        response = requests.head(url, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        return response.status_code == 200
    except Exception as e:
        print(f"URL validation failed: {e}")
        return False

# Test URL
url = "https://klettbib.livebook.de/978-3-12-756141-8/"
is_valid = validate_livebook_url(url)
```

### Step 3: Progressive Testing

```python
def progressive_test(url: str):
    """Test tool functionality progressively."""
    
    # Test 1: Basic WebDriver setup
    print("🧪 Test 1: WebDriver Setup")
    try:
        tool = LivebookScreenshotTool(headless=True)
        print("✅ WebDriver setup successful")
    except Exception as e:
        print(f"❌ WebDriver setup failed: {e}")
        return
    
    # Test 2: Page navigation
    print("\n🧪 Test 2: Page Navigation")
    try:
        tool._setup_driver()
        tool.driver.get(url)
        print(f"✅ Page loaded: {tool.driver.title}")
    except Exception as e:
        print(f"❌ Page navigation failed: {e}")
        tool.close()
        return
    
    # Test 3: Element detection
    print("\n🧪 Test 3: Element Detection")
    try:
        toc_element = tool._find_toc_element()
        if toc_element:
            print(f"✅ TOC element found: {toc_element.tag_name}")
        else:
            print("⚠️ No TOC element found")
    except Exception as e:
        print(f"❌ Element detection failed: {e}")
    
    # Cleanup
    tool.close()

# Run progressive test
progressive_test("https://klettbib.livebook.de/978-3-12-756141-8/")
```

## Browser Issues

### Chrome Version Compatibility

**Problem:** ChromeDriver version doesn't match Chrome browser version.

**Solution:**
```python
# Check Chrome version
import subprocess
result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
print(f"Chrome version: {result.stdout}")

# Use specific ChromeDriver version
from webdriver_manager.chrome import ChromeDriverManager
driver_manager = ChromeDriverManager(version="your_version_here")
```

### Headless Mode Issues

**Problem:** Screenshots work in visible mode but fail in headless mode.

**Solution:**
```python
# Use larger window size for headless mode
tool = LivebookScreenshotTool(
    headless=True,
    window_size=(1920, 1080)  # Ensure sufficient size
)

# Alternative: Force specific viewport
chrome_options.add_argument("--force-device-scale-factor=1")
chrome_options.add_argument("--high-dpi-support=1")
```

### Memory Issues

**Problem:** Browser crashes with large pages or multiple operations.

**Solution:**
```python
# Add memory-related options
chrome_options.add_argument("--memory-pressure-off")
chrome_options.add_argument("--max_old_space_size=4096")
chrome_options.add_argument("--disable-background-timer-throttling")
chrome_options.add_argument("--disable-renderer-backgrounding")
```

## Network Problems

### Slow Connections

```python
# Increase timeouts for slow connections
class LivebookScreenshotTool:
    def __init__(self, headless=True, window_size=(1920, 1080), timeout=60):
        self.timeout = timeout
    
    def _setup_driver(self):
        # ... existing setup ...
        self.wait = WebDriverWait(self.driver, self.timeout)
        
        # Set page load timeout
        self.driver.set_page_load_timeout(self.timeout)
```

### Proxy Configuration

```python
# Configure proxy if needed
chrome_options.add_argument(f"--proxy-server=http://proxy.example.com:8080")
chrome_options.add_argument("--proxy-bypass-list=localhost,127.0.0.1")
```

### SSL Issues

```python
# Handle SSL certificate issues
chrome_options.add_argument("--ignore-ssl-errors-on-localhost")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
```

## Element Detection Issues

### Custom Selector Development

```python
def create_custom_selectors(page_analysis: dict) -> list:
    """Create custom selectors based on page analysis."""
    
    custom_selectors = []
    
    # Analyze page structure
    if "mathematics" in page_analysis.get('title', '').lower():
        custom_selectors.extend([
            "//div[@class='math-toc']",
            "//section[contains(@id, 'contents')]"
        ])
    
    # Add language-specific selectors
    custom_selectors.extend([
        "//h1[contains(text(), 'Inhalt')]/..",
        "//h2[contains(text(), 'Übersicht')]/..",
        "//div[contains(@class, 'kapitel')]"
    ])
    
    return custom_selectors
```

### Fallback Strategies

```python
def find_toc_with_fallbacks(self) -> Optional[Any]:
    """Find TOC with multiple fallback strategies."""
    
    # Strategy 1: Standard selectors
    element = self._find_toc_element()
    if element:
        return element
    
    # Strategy 2: Text-based search
    try:
        elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Kapitel')]")
        for elem in elements:
            parent = elem.find_element(By.XPATH, "..")
            if parent.size['height'] > 100:
                return parent
    except:
        pass
    
    # Strategy 3: Class-based fallback
    try:
        potential_elements = self.driver.find_elements(By.CSS_SELECTOR, "div, section, nav")
        for elem in potential_elements:
            if elem.size['height'] > 200 and "content" in elem.get_attribute('class', ''):
                return elem
    except:
        pass
    
    return None
```

## Performance Optimization

### Memory Management

```python
def optimize_for_batch_processing():
    """Optimize settings for batch processing."""
    
    chrome_options = Options()
    
    # Memory optimization
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--aggressive-cache-discard")
    chrome_options.add_argument("--disable-background-timer-throttling")
    
    # CPU optimization
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-sync")
    
    return chrome_options
```

### Connection Pooling

```python
class BatchScreenshotTool:
    """Optimized tool for batch processing."""
    
    def __init__(self):
        self.driver = None
        self.session_count = 0
        self.max_session_reuse = 10
    
    def screenshot_with_reuse(self, url: str, filename: str) -> bool:
        """Reuse driver for multiple screenshots."""
        
        if not self.driver or self.session_count >= self.max_session_reuse:
            self._reset_driver()
        
        try:
            # Use existing driver
            result = self._capture_screenshot(url, filename)
            self.session_count += 1
            return result
        except Exception:
            # Reset driver on error
            self._reset_driver()
            return self._capture_screenshot(url, filename)
```

## Logging and Debugging

### Advanced Logging Setup

```python
import logging
from datetime import datetime

def setup_advanced_logging():
    """Setup comprehensive logging."""
    
    # Create logger
    logger = logging.getLogger('livebook_screenshot')
    logger.setLevel(logging.DEBUG)
    
    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        'livebook_screenshot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    file_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(simple_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Use advanced logging
logger = setup_advanced_logging()
```

### Debug Mode Implementation

```python
class DebugLivebookScreenshotTool(LivebookScreenshotTool):
    """Extended version with debug capabilities."""
    
    def __init__(self, *args, debug_mode=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug_mode = debug_mode
        
        if debug_mode:
            self.logger.setLevel(logging.DEBUG)
            self.save_debug_info = True
            self.debug_dir = Path("debug_output")
            self.debug_dir.mkdir(exist_ok=True)
    
    def screenshot_livebook_toc(self, url: str, filename: str, **kwargs) -> bool:
        """Enhanced version with debug output."""
        
        if self.debug_mode:
            self._save_debug_page_info(url, filename)
        
        return super().screenshot_livebook_toc(url, filename, **kwargs)
    
    def _save_debug_page_info(self, url: str, filename: str):
        """Save debug information to files."""
        
        debug_file = self.debug_dir / f"{filename}_debug.txt"
        
        with open(debug_file, 'w') as f:
            f.write(f"Debug Info for {filename}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write("-" * 50 + "\n")
            
            # Save page info
            info = self.get_page_info(url)
            for key, value in info.items():
                f.write(f"{key}: {value}\n")
```

## Recovery Strategies

### Automatic Retry with Backoff

```python
import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1, max_delay=60):
    """Retry function with exponential backoff."""
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            print(f"Attempt {attempt + 1} failed, retrying in {delay:.1f} seconds...")
            time.sleep(delay)

# Usage example
def capture_with_retry(tool, url, filename):
    return retry_with_backoff(
        lambda: tool.screenshot_livebook_toc(url, filename),
        max_retries=3
    )
```

### Graceful Degradation

```python
def capture_with_degradation(tool, url, filename):
    """Try multiple approaches with graceful degradation."""
    
    strategies = [
        lambda: tool.screenshot_livebook_toc(url, filename),  # Normal
        lambda: tool.screenshot_livebook_toc(url, filename, retry_count=5),  # More retries
        lambda: capture_with_visible_browser(url, filename),  # Visible mode
        lambda: capture_full_page_fallback(url, filename)  # Full page
    ]
    
    for i, strategy in enumerate(strategies):
        try:
            print(f"Trying strategy {i + 1}/{len(strategies)}")
            result = strategy()
            if result:
                return result
        except Exception as e:
            print(f"Strategy {i + 1} failed: {e}")
    
    print("All strategies failed")
    return False
```

## Getting Help

### Support Information

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the README.md for latest updates
- **Debug Output**: Always include debug logs when reporting issues
- **System Information**: Include OS, Python version, and browser version

### Creating Bug Reports

Include the following information:

1. **Environment Details:**
   ```python
   import sys, platform
   print(f"Python: {sys.version}")
   print(f"Platform: {platform.platform()}")
   print(f"Architecture: {platform.architecture()}")
   ```

2. **Error Details:**
   - Full error traceback
   - URL being processed
   - Tool configuration used
   - Expected vs. actual behavior

3. **Debug Output:**
   - Enable debug logging
   - Include relevant log entries
   - Attach debug files if available

4. **Reproduction Steps:**
   - Minimal code to reproduce the issue
   - Any specific conditions or timing
   - Whether the issue is consistent or intermittent 