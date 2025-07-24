# Livebook Screenshot Tool

A robust, production-ready Python tool for automatically capturing table of contents screenshots from Livebook educational platforms. This tool specializes in German-language content detection and provides comprehensive error handling for reliable automation.

## 🎯 Features

- **Automatic ChromeDriver Management**: No manual driver installation required
- **German Language TOC Detection**: Specialized selectors for "Inhaltsverzeichnis"
- **Smart Screenshot Modes**: Full page (recommended) or element-specific capture
- **Multi-Page Capture**: Automatically capture all pages from Livebooks
- **ISBN Batch Processing**: Process multiple books with organized directory structure
- **AI-Powered TOC Filtering**: Uses OpenAI GPT-4o mini to identify actual TOC pages
- **Multiple Operation Modes**: Both headless and visible browser options
- **Comprehensive Error Handling**: Robust retry mechanisms and graceful degradation
- **Jupyter Integration**: Ready-to-use notebook examples with progress tracking
- **Context Manager Support**: Automatic resource cleanup
- **Extensive Logging**: Detailed logging for debugging and monitoring
- **Cost-Effective**: AI filtering costs ~$0.0015 per book (10 pages)

## 📋 Requirements

- **Python**: 3.8 or higher
- **Chrome Browser**: Latest stable version recommended
- **Internet Connection**: Required for ChromeDriver auto-download
- **OpenAI API Key**: Required for AI-powered TOC filtering

### Setting Up Your API Key

Create a `.env` file in the project directory:

```bash
# Create .env file
echo "OPENAI_API_KEY=your-actual-api-key-here" > .env
```

**Get your API key from:** https://platform.openai.com/api-keys

The `.env` file keeps your API key secure and separate from your code.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
git clone <repository-url>
cd scrape_livebooks

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

```python
from livebook_screenshot_tool import LivebookScreenshotTool

# Create tool instance
tool = LivebookScreenshotTool(headless=True)

# Capture full page screenshot (recommended)
url = "https://klettbib.livebook.de/978-3-12-316302-9/"
success = tool.screenshot_livebook_toc(url, "my_screenshot", full_page=True)

if success:
    print("✅ Screenshot captured successfully!")
    print("📁 Check the 'screenshots' folder")

# Clean up
tool.close()
```

### 3. Context Manager (Recommended)

```python
from livebook_screenshot_tool import LivebookScreenshotTool

url = "https://klettbib.livebook.de/978-3-12-316302-9/"

# Automatic cleanup with context manager
with LivebookScreenshotTool(headless=True) as tool:
    success = tool.screenshot_livebook_toc(url, "context_example", full_page=True)
    print("✅ Screenshot captured!" if success else "❌ Failed!")
```

## 📚 Documentation

### Core Components

| File | Description |
|------|-------------|
| `livebook_screenshot_tool.py` | Main tool implementation |
| `usage_examples.py` | Comprehensive usage examples |
| `jupyter_example.ipynb` | Jupyter notebook integration |
| `error_handling_guide.md` | Detailed error handling guide |
| `requirements.txt` | Python dependencies |

### API Reference

#### LivebookScreenshotTool Class

```python
class LivebookScreenshotTool:
    def __init__(self, headless=True, window_size=(1920, 1080)):
        """
        Initialize the screenshot tool.
        
        Args:
            headless (bool): Run browser in headless mode
            window_size (tuple): Browser window size (width, height)
        """
    
    def screenshot_livebook_toc(self, url: str, filename: str, retry_count: int = 3, full_page: bool = True) -> bool:
        """
        Capture screenshot from Livebook URL.
        
        Args:
            url: Target Livebook URL
            filename: Output filename (without extension)
            retry_count: Number of retry attempts
            full_page: If True (default), capture full page; if False, try to find TOC element
            
        Returns:
            bool: True if successful, False otherwise
        """
    
    def screenshot_multiple_urls(self, url_filename_pairs: list, progress_callback=None) -> dict:
        """
        Process multiple URLs with optional progress tracking.
        
        Args:
            url_filename_pairs: List of (url, filename) tuples
            progress_callback: Optional callback function
            
        Returns:
            dict: Results for each URL
        """
    
    def get_page_info(self, url: str) -> dict:
        """
        Analyze page structure for debugging.
        
        Args:
            url: URL to analyze
            
        Returns:
            dict: Page information and element detection results
        """
```

## 🛠️ Configuration Options

### Browser Configuration

```python
# Headless mode (default)
tool = LivebookScreenshotTool(headless=True)

# Visible browser (for debugging)
tool = LivebookScreenshotTool(headless=False)

# Custom window size
tool = LivebookScreenshotTool(
    headless=True,
    window_size=(1920, 1080)
)
```

### Advanced Options

```python
# Modify TOC selectors
tool = LivebookScreenshotTool()
tool.toc_selectors.append("//your-custom-xpath")

# Access WebDriver for custom operations
tool._setup_driver()
driver = tool.driver
```

## 📖 Usage Examples

### Example 1: Basic Screenshot

```python
from livebook_screenshot_tool import LivebookScreenshotTool

with LivebookScreenshotTool() as tool:
    url = "https://klettbib.livebook.de/978-3-12-756141-8/"
    success = tool.screenshot_livebook_toc(url, "basic_example")
    print("✅ Success!" if success else "❌ Failed!")
```

### Example 2: Batch Processing

```python
from livebook_screenshot_tool import LivebookScreenshotTool

urls_and_files = [
    ("https://klettbib.livebook.de/book1/", "book1_toc"),
    ("https://klettbib.livebook.de/book2/", "book2_toc"),
]

def progress(current, total, url):
    print(f"Progress: {current+1}/{total} - {url}")

with LivebookScreenshotTool() as tool:
    results = tool.screenshot_multiple_urls(urls_and_files, progress)
    
    successful = sum(results.values())
    print(f"✅ Completed: {successful}/{len(results)} screenshots")
```

### Example 3: Error Handling

```python
from livebook_screenshot_tool import LivebookScreenshotTool, LivebookScreenshotError

with LivebookScreenshotTool() as tool:
    try:
        success = tool.screenshot_livebook_toc(url, "error_example")
        if success:
            print("✅ Screenshot captured successfully!")
        else:
            print("⚠️ Screenshot failed but no exception raised")
            
    except LivebookScreenshotError as e:
        print(f"❌ Livebook Error: {e}")
        # Handle specific error cases
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        # Handle general errors
```

### Example 4: ISBN Batch Processing

```python
from livebook_screenshot_tool import LivebookScreenshotTool

# List of ISBNs to process
isbn_list = [
    "978-3-12-316302-9",
    "978-3-12-123456-7",
    "978-3-12-789012-3"
]

with LivebookScreenshotTool() as tool:
    # Process all ISBNs, max 10 pages per book
    results = tool.screenshot_isbn_batch(
        isbn_list=isbn_list,
        max_pages=10
    )
    
    # Results organized in directories:
    # screenshots/978-3-12-316302-9/
    # screenshots/978-3-12-123456-7/
    # screenshots/978-3-12-789012-3/
```

### Example 5: All Pages Capture

```python
from livebook_screenshot_tool import LivebookScreenshotTool

with LivebookScreenshotTool() as tool:
    url = "https://klettbib.livebook.de/978-3-12-316302-9/"
    
    # Capture all pages (up to 10 by default)
    results = tool.screenshot_all_pages(
        url=url,
        base_filename="complete_book",
        max_pages=10,
        output_dir="my_custom_directory"
    )
    
    print(f"Captured {results['total_pages']} pages")
```

### Example 6: AI-Powered TOC Filtering

```python
from filter_toc_screenshots import TOCScreenshotFilter

# OpenAI API key is automatically loaded from .env file
# Just make sure you have: OPENAI_API_KEY=your-key in .env

# Filter all screenshots to identify TOC pages
filter_tool = TOCScreenshotFilter()
results = filter_tool.filter_batch_directories(
    screenshots_dir="screenshots",
    confidence_threshold=0.7
)

# Organize files into toc_pages/ and non_toc_pages/ folders
filter_tool.organize_filtered_results(results, organize_files=True)

print(f"Found {results['summary']['total_toc_pages_found']} TOC pages")
```

## 🚀 Complete Workflow

### Method 1: One-Command Workflow (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 3. Run complete workflow
python run_complete_workflow.py
```

### Method 2: Configuration-based Workflow

```bash
# Run with configuration file
python config_example.py workflow
```

**Both methods will:**
1. **Capture** all pages (max 10) for each ISBN in separate directories
2. **Analyze** each screenshot using GPT-4o mini to identify TOC content
3. **Organize** files into `toc_pages/` and `non_toc_pages/` folders
4. **Generate** a detailed JSON analysis report

**The difference:** `run_complete_workflow.py` provides a streamlined, single-script experience with all functionality built-in.

## 🧪 Running Examples

### Command Line Examples

```bash
# Complete workflow (recommended)
python run_complete_workflow.py

# Run basic example
python livebook_screenshot_tool.py

# Test ISBN batch processing
python test_isbn_batch.py

# Test AI TOC filtering
python test_toc_filter.py

# Run comprehensive examples
python usage_examples.py

# Configuration-based workflow
python config_example.py capture  # Screenshots only
python config_example.py filter   # AI filtering only
python config_example.py workflow # Complete workflow
```

### Jupyter Notebook

```bash
# Start Jupyter
jupyter notebook

# Open jupyter_example.ipynb
# Follow the interactive examples
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| ChromeDriver not found | Check internet connection, clear `~/.wdm/drivers/` |
| TOC element not found | Use `get_page_info()` to analyze page structure |
| Permission denied | Check file permissions, try different output directory |
| Page load timeout | Increase timeout, check network connection |
| Memory issues | Use headless mode, restart browser periodically |

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use visible browser for inspection
tool = LivebookScreenshotTool(headless=False)

# Analyze page structure
info = tool.get_page_info(url)
print(info)
```

### Getting Help

1. **Check Error Handling Guide**: See `error_handling_guide.md` for detailed troubleshooting
2. **Enable Debug Logging**: Set logging level to DEBUG for detailed output
3. **Use Page Analysis**: `get_page_info()` provides insights into page structure
4. **Try Visible Mode**: `headless=False` allows manual inspection

## 📁 Project Structure

```
scrape_livebooks/
├── livebook_screenshot_tool.py    # Main tool implementation
├── filter_toc_screenshots.py      # AI-powered TOC filtering using GPT-4o mini
├── run_complete_workflow.py       # Complete workflow script (capture + filter)
├── usage_examples.py              # Comprehensive examples
├── jupyter_example.ipynb          # Jupyter integration with AI filtering
├── test_isbn_batch.py             # Test script for ISBN batch processing
├── test_toc_filter.py             # Test script for AI TOC filtering
├── config_example.py              # Complete workflow configuration
├── error_handling_guide.md        # Error handling documentation
├── requirements.txt               # Python dependencies (includes OpenAI)
├── README.md                      # This file
└── screenshots/                   # Output directory (auto-created)
    └── [ISBN]/                    # Organized by ISBN
        ├── toc_pages/             # AI-identified TOC pages
        └── non_toc_pages/         # Other pages
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd scrape_livebooks

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-cov
```

### Running Tests

```bash
# Run basic functionality test
python livebook_screenshot_tool.py

# Run all examples
python usage_examples.py

# Run specific test
python -c "
from livebook_screenshot_tool import LivebookScreenshotTool
with LivebookScreenshotTool() as tool:
    print('✅ Tool initialized successfully!')
"
```

### Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature-name`
3. **Make changes and test thoroughly**
4. **Update documentation if needed**
5. **Submit pull request**

## 📊 Performance Tips

### Optimization for Batch Processing

```python
# Reuse browser instance
with LivebookScreenshotTool() as tool:
    for url, filename in url_list:
        tool.screenshot_livebook_toc(url, filename)
    # Browser closed automatically

# Use appropriate window size
tool = LivebookScreenshotTool(window_size=(1920, 1080))

# Monitor memory usage for large batches
import psutil
print(f"Memory usage: {psutil.virtual_memory().percent}%")
```

### Network Optimization

```python
# For slow connections, increase timeouts
# Modify _wait_for_page_load timeout in the tool
# Or implement custom retry logic with longer delays
```

## 🔒 Security Considerations

- **Headless Mode**: Recommended for production environments
- **Network Security**: Tool makes HTTP requests to target URLs
- **File Permissions**: Screenshots saved to local filesystem
- **Browser Security**: Uses Chrome security features and sandboxing

## 📄 License

This project is intended for educational and research purposes. Please respect the terms of service of target websites and ensure compliance with applicable laws and regulations.

## 🆘 Support

For issues, questions, or contributions:

1. **Check Documentation**: Review all `.md` files in the project
2. **Run Diagnostics**: Use built-in debugging tools
3. **Search Issues**: Look for similar problems in project issues
4. **Create Issue**: Provide detailed error information and reproduction steps

## 🎉 Acknowledgments

- **Selenium WebDriver**: Browser automation framework
- **webdriver-manager**: Automatic ChromeDriver management
- **Chrome Browser**: Reliable web rendering engine
- **Python Community**: Excellent libraries and documentation

## 📈 Roadmap

Future enhancements being considered:

- [ ] Support for additional browsers (Firefox, Edge)
- [ ] Multi-language TOC detection
- [ ] Advanced screenshot post-processing
- [ ] REST API interface
- [ ] Docker containerization
- [ ] Cloud deployment options
- [ ] Performance monitoring and metrics 