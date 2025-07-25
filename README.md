# Table of Contents Scrape and Analyze

A comprehensive system for capturing table of contents from Livebook educational platforms and generating detailed educational taxonomies using AI analysis. This tool combines automated screenshot capture with GPT-4 vision analysis to create structured curricula data.

## 🎯 Complete System Features

### 📸 Screenshot Capture System
- **Automatic ChromeDriver Management**: No manual driver installation required
- **German Language TOC Detection**: Specialized selectors for "Inhaltsverzeichnis"  
- **Smart Screenshot Modes**: Full page (recommended) or element-specific capture
- **Multi-Page Capture**: Automatically capture all pages from Livebooks
- **ISBN Batch Processing**: Process multiple books with organized directory structure
- **AI-Powered TOC Filtering**: Uses OpenAI GPT-4o mini to identify actual TOC pages

### 🧠 Taxonomy Analysis System
- **GPT-4 Vision Analysis**: Intelligent analysis of TOC screenshots to extract educational content
- **Hierarchical Taxonomy Generation**: Creates structured taxonomies with topics, subtopics, and keyterms
- **Educational Content Focus**: Filters out non-educational content (tests, exercises, practice exams)
- **Multi-Language Support**: Analyzes German content, outputs English taxonomies
- **Student-Friendly Naming**: Adjusts topic names for student comprehension
- **Flexible Processing**: Single book analysis or batch processing of entire collections
- **Comprehensive Validation**: JSON structure validation and error recovery
- **Command Line Interface**: Easy-to-use CLI for all operations

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

## 🚀 Complete Workflow: From Livebook to Taxonomy

### Step 1: Get Table of Contents from Livebooks

#### What are Livebooks?
Livebooks are digital educational books hosted at URLs like:
- `https://klettbib.livebook.de/978-3-12-316302-9/` (German textbooks)
- Each book has a unique ISBN identifier in the URL
- The books contain table of contents pages that show the curriculum structure

#### Capturing TOC Screenshots

```bash
# 1. Installation
git clone https://github.com/maximilian-puetz-knowunity/table-of-contents-scrape-and-analyze.git
cd table-of-contents-scrape-and-analyze
pip install -r requirements.txt

# 2. Set up your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 3. Capture TOC screenshots from Livebooks
python run_complete_workflow.py
```

This will:
1. **Capture** screenshots from Livebook URLs (up to 10 pages per book)
2. **Filter** screenshots using AI to identify actual table of contents pages
3. **Organize** results into `tocs/` directory with clean TOC images ready for analysis

#### Input: Livebook URLs
```
https://klettbib.livebook.de/978-3-12-316302-9/  # Math Grade 6
https://klettbib.livebook.de/978-3-12-316303-6/  # Math Grade 7  
https://klettbib.livebook.de/978-3-12-316304-3/  # Math Grade 8
```

#### Output: TOC Screenshots
```
tocs/
├── toc_Deutsch_6_Deutsch_kompetent_6_978-3-12-316302-9/
│   ├── page_01.png
│   ├── page_02.png
│   └── page_03.png
├── toc_Mathematik_7_Lambacher_Schweizer_7_978-3-12-316303-6/
│   ├── page_01.png
│   └── page_02.png
```

### Step 2: Analyze TOC Screenshots and Generate Taxonomies

#### What is Taxonomy Analysis?
The system uses GPT-4 Vision to:
1. **Read** the German text in TOC screenshots
2. **Extract** educational topics, subtopics, and learning progression
3. **Structure** content into hierarchical taxonomies
4. **Generate** English output with student-friendly names
5. **Add** relevant keyterms for each educational concept

#### Single Book Analysis

```bash
# Analyze a single book's table of contents
python analyze_single_book.py tocs/toc_Mathematik_7_Lambacher_Schweizer_7_978-3-12-316303-6/

# With custom options
python analyze_single_book.py --tocs-dir tocs/toc_specific_book/ --output-dir my_results/ --max-depth 3
```

#### Batch Analysis (All Books)

```bash
# Analyze all TOC directories at once
python run_taxonomy_analysis.py --tocs-dir tocs/ --output-dir taxonomies/

# Non-interactive mode for automation
python run_taxonomy_analysis.py --tocs-dir tocs/ --non-interactive
```

#### Interactive Demo

```bash
# Try the system with a guided demo
python demo_single_taxonomy.py --tocs-dir tocs/
```

### Step 3: Understanding the Output

#### Taxonomy JSON Structure
Each analysis produces a structured JSON file with educational taxonomy:

```json
{
    "country": "DE",
    "grade": "7", 
    "subject": "Mathematics",
    "ISBN": "978-3-12-316303-6",
    "taxonomy": [
        {
            "name": "Algebra",
            "level": 0,
            "keyterms": ["equations", "variables", "expressions", "solving", "coefficients"],
            "children": [
                {
                    "name": "Linear Equations",
                    "level": 1,
                    "keyterms": ["slope", "y-intercept", "graphing", "solving methods"],
                    "children": [
                        {
                            "name": "Solving One-Variable Equations",
                            "level": 2,
                            "keyterms": ["isolation", "inverse operations", "checking solutions"],
                            "children": []
                        }
                    ]
                }
            ]
        },
        {
            "name": "Geometry", 
            "level": 0,
            "keyterms": ["shapes", "area", "perimeter", "angles", "measurement"],
            "children": [...]
        }
    ]
}
```

#### What Each Field Means:
- **name**: Student-friendly topic name (in English)
- **level**: Hierarchy depth (0=main topics, 1=subtopics, 2=concepts)  
- **keyterms**: 5-15 relevant terms students associate with the concept
- **children**: Nested subtopics and concepts
- **country/grade/subject/ISBN**: Metadata for organizing curricula

### Step 4: Using the Results

#### Educational Applications:
1. **Curriculum Mapping**: Understand what's taught at each grade level
2. **Learning Progression**: See how concepts build on each other
3. **Content Alignment**: Compare curricula across different textbooks
4. **Student Resources**: Use keyterms for study guides and search
5. **Educational Technology**: Power adaptive learning systems

#### Output Directory Structure:
```
taxonomies/
├── taxonomy_Deutsch_6_Deutsch_kompetent_6_978-3-12-316302-9.json
├── taxonomy_Mathematik_7_Lambacher_Schweizer_7_978-3-12-316303-6.json
├── taxonomy_Erdkunde_8_Terra_Erdkunde_8_978-3-12-316304-3.json
└── analysis_report.json  # Summary of all processed books
```

## 📚 Documentation

### Core Components

#### Screenshot Capture System
| File | Description |
|------|-------------|
| `livebook_screenshot_tool.py` | Main screenshot capture tool |
| `filter_toc_screenshots.py` | AI-powered TOC page filtering |
| `run_complete_workflow.py` | Complete screenshot workflow |

#### Taxonomy Analysis System
| File | Description |
|------|-------------|
| `toc_taxonomy_analyzer.py` | Core GPT-4 vision analysis engine |
| `analyze_single_book.py` | Single book taxonomy analysis |
| `run_taxonomy_analysis.py` | Batch taxonomy processing |
| `demo_single_taxonomy.py` | Interactive taxonomy demo |

#### Configuration & Documentation
| File | Description |
|------|-------------|
| `REQUIREMENTS.md` | JSON input/output specifications |
| `TAXONOMY_ANALYSIS_README.md` | Detailed taxonomy system documentation |
| `error_handling_guide.md` | Error handling and troubleshooting |
| `requirements.txt` | Python dependencies |

### API Reference

#### TocTaxonomyAnalyzer Class

```python
class TocTaxonomyAnalyzer:
    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo"):
        """
        Initialize the taxonomy analyzer.
        
        Args:
            api_key: OpenAI API key (reads from environment if not provided)
            model: OpenAI model for vision analysis
        """
    
    def analyze_toc_images(self, images: list, metadata: BookMetadata, max_depth: int = 3) -> dict:
        """
        Analyze TOC images and generate educational taxonomy.
        
        Args:
            images: List of image file paths
            metadata: Book metadata (country, grade, subject, ISBN)
            max_depth: Maximum hierarchy depth for taxonomy
            
        Returns:
            dict: Complete taxonomy structure with metadata
        """
    
    def process_all_toc_directories(self, tocs_dir: str, output_dir: str = "taxonomies", max_depth: int = 3) -> dict:
        """
        Process all TOC directories in batch.
        
        Args:
            tocs_dir: Directory containing TOC subdirectories
            output_dir: Output directory for taxonomy JSON files
            max_depth: Maximum taxonomy depth
            
        Returns:
            dict: Processing results and statistics
        """
```

#### Command Line Tools

```bash
# Single book analysis
python analyze_single_book.py [toc_directory] [options]

# Batch processing
python run_taxonomy_analysis.py --tocs-dir [directory] [options]

# Interactive demo
python demo_single_taxonomy.py --tocs-dir [directory]

# Complete workflow (screenshots + analysis)
python run_complete_workflow.py
```

#### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--tocs-dir` | Directory containing TOC images | Required |
| `--output-dir` | Output directory for results | `taxonomies/` |
| `--max-depth` | Maximum taxonomy hierarchy depth | `3` |
| `--non-interactive` | Run without user prompts | `False` |

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

### Example 1: Complete Workflow (Recommended)

```bash
# One command to do everything:
# 1. Capture screenshots from Livebook URLs
# 2. Filter and identify TOC pages  
# 3. Analyze TOC content with GPT-4 Vision
# 4. Generate structured educational taxonomies

python run_complete_workflow.py
```

### Example 2: Analyze Single Book

```bash
# Analyze taxonomy for one specific book
python analyze_single_book.py tocs/toc_Mathematik_7_Lambacher_Schweizer_7_978-3-12-316303-6/

# Custom output directory and depth
python analyze_single_book.py \
    --tocs-dir tocs/toc_Deutsch_6_Deutsch_kompetent_6_978-3-12-316302-9/ \
    --output-dir my_analysis/ \
    --max-depth 4
```

### Example 3: Batch Taxonomy Analysis

```bash
# Analyze all TOC directories at once
python run_taxonomy_analysis.py --tocs-dir tocs/ --output-dir taxonomies/

# Non-interactive mode for automation
python run_taxonomy_analysis.py --tocs-dir tocs/ --non-interactive --max-depth 3
```

### Example 4: Interactive Demo

```bash
# Try the system with guided walkthrough
python demo_single_taxonomy.py --tocs-dir tocs/

# Non-interactive demo
python demo_single_taxonomy.py --tocs-dir tocs/ --non-interactive
```

### Example 5: Using the Python API

```python
from toc_taxonomy_analyzer import TocTaxonomyAnalyzer

# Initialize analyzer
analyzer = TocTaxonomyAnalyzer()

# Process single TOC directory
toc_dir = "tocs/toc_Mathematik_7_Lambacher_Schweizer_7_978-3-12-316303-6/"
results = analyzer.process_single_directory(toc_dir, max_depth=3)

if results['success']:
    print(f"✅ Generated taxonomy with {len(results['taxonomy']['taxonomy'])} main topics")
    print(f"📁 Saved to: {results['output_file']}")
else:
    print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
```

### Example 6: Working with Results

```python
import json

# Load generated taxonomy
with open('taxonomies/taxonomy_Mathematik_7_Lambacher_Schweizer_7_978-3-12-316303-6.json') as f:
    taxonomy = json.load(f)

# Extract all topics and subtopics
def extract_all_topics(taxonomy_items, level=0):
    topics = []
    for item in taxonomy_items:
        topics.append({
            'name': item['name'],
            'level': item['level'],
            'keyterms': item['keyterms']
        })
        if item['children']:
            topics.extend(extract_all_topics(item['children'], level+1))
    return topics

all_topics = extract_all_topics(taxonomy['taxonomy'])
print(f"Total educational concepts found: {len(all_topics)}")

# Find all keyterms for the subject
all_keyterms = []
for topic in all_topics:
    all_keyterms.extend(topic['keyterms'])

unique_keyterms = list(set(all_keyterms))
print(f"Unique educational terms: {len(unique_keyterms)}")
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

#### Screenshot Capture Issues
| Issue | Solution |
|-------|----------|
| ChromeDriver not found | Check internet connection, clear `~/.wdm/drivers/` |
| Page load timeout | Increase timeout, check network connection |
| Permission denied | Check file permissions, try different output directory |
| Memory issues | Use headless mode, restart browser periodically |

#### Taxonomy Analysis Issues  
| Issue | Solution |
|-------|----------|
| OpenAI API key error | Check `.env` file has `OPENAI_API_KEY=your-key` |
| JSON parsing error | Check log files, use `--max-depth 2` for simpler output |
| No TOC images found | Verify TOC directory structure and image files |
| GPT-4 analysis fails | Check API quota, try again later, verify model availability |
| Malformed taxonomy output | Use built-in JSON repair mechanisms, check input images |

### Debug Mode

#### Screenshot Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use visible browser for inspection
from livebook_screenshot_tool import LivebookScreenshotTool
tool = LivebookScreenshotTool(headless=False)
```

#### Taxonomy Analysis Debugging
```python
# Enable detailed logging for taxonomy analysis
from toc_taxonomy_analyzer import TocTaxonomyAnalyzer
import logging

logging.basicConfig(level=logging.DEBUG)
analyzer = TocTaxonomyAnalyzer()

# Test with single directory
results = analyzer.process_single_directory("tocs/test_directory/")
print(f"Debug info: {results}")
```

### Getting Help

1. **Check Documentation**: 
   - `TAXONOMY_ANALYSIS_README.md` for taxonomy system details
   - `error_handling_guide.md` for detailed troubleshooting
2. **Enable Debug Logging**: Set logging level to DEBUG for detailed output
3. **Test Components Separately**: 
   - Test screenshot capture first with `run_complete_workflow.py`
   - Then test taxonomy analysis with `demo_single_taxonomy.py`
4. **Verify API Access**: Ensure your OpenAI API key has GPT-4 vision access

## 📁 Project Structure

```
table-of-contents-scrape-and-analyze/
├── 📸 Screenshot Capture System
│   ├── livebook_screenshot_tool.py     # Main screenshot capture tool
│   ├── filter_toc_screenshots.py       # AI-powered TOC page filtering
│   ├── run_complete_workflow.py        # Complete screenshot workflow
│   └── copy_toc_pages.py               # Utility for organizing TOC files
│
├── 🧠 Taxonomy Analysis System  
│   ├── toc_taxonomy_analyzer.py        # Core GPT-4 vision analysis engine
│   ├── analyze_single_book.py          # Single book taxonomy analysis
│   ├── run_taxonomy_analysis.py        # Batch taxonomy processing
│   ├── demo_single_taxonomy.py         # Interactive taxonomy demo
│   └── test_taxonomy_parser.py         # Testing and validation tools
│
├── 📋 Configuration & Documentation
│   ├── REQUIREMENTS.md                 # JSON input/output specifications
│   ├── TAXONOMY_ANALYSIS_README.md     # Detailed taxonomy documentation
│   ├── error_handling_guide.md         # Error handling and troubleshooting
│   ├── requirements.txt                # Python dependencies
│   ├── .gitignore                      # Git ignore rules
│   └── README.md                       # This file (complete overview)
│
├── 📂 Data Directories (auto-created)
│   ├── screenshots/                    # Raw screenshots from Livebooks
│   │   └── [ISBN]/                     # Organized by book ISBN
│   │       ├── toc_pages/              # AI-identified TOC pages
│   │       └── non_toc_pages/          # Other content pages
│   ├── tocs/                           # Clean TOC images ready for analysis
│   │   └── toc_[Subject]_[Grade]_[Title]_[ISBN]/
│   │       ├── page_01.png
│   │       ├── page_02.png
│   │       └── ...
│   └── taxonomies/                     # Generated educational taxonomies
│       ├── taxonomy_[Subject]_[Grade]_[Title]_[ISBN].json
│       └── analysis_report.json       # Summary of all processed books
│
└── 🗂️ Legacy Files (screenshot system only)
    ├── usage_examples.py               # Old screenshot examples
    ├── jupyter_example.ipynb           # Jupyter screenshot integration
    ├── test_isbn_batch.py              # Screenshot batch testing
    ├── test_toc_filter.py              # TOC filtering tests
    └── config_example.py               # Old configuration system
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

### Core Technologies
- **OpenAI GPT-4 Vision**: Advanced image analysis and content extraction
- **Selenium WebDriver**: Browser automation framework for screenshot capture
- **webdriver-manager**: Automatic ChromeDriver management
- **Chrome Browser**: Reliable web rendering engine

### Educational Domain
- **Klett Publishers**: Educational content and Livebook platform
- **German Educational System**: Rich curriculum structure for analysis
- **Educational Technology Community**: Inspiration for taxonomic approaches

### Development Support
- **Python Community**: Excellent libraries and comprehensive documentation
- **Open Source Contributors**: Foundation libraries and best practices

## 📈 Roadmap

### Short-term Enhancements
- [ ] **Enhanced Language Support**: Multi-language content analysis (French, Spanish textbooks)
- [ ] **Improved Accuracy**: Fine-tuned prompts for specific educational domains
- [ ] **Performance Optimization**: Caching and parallel processing for large datasets
- [ ] **Quality Assurance**: Automated validation of taxonomy structures

### Medium-term Features
- [ ] **REST API Interface**: Web service for taxonomy generation
- [ ] **Curriculum Comparison**: Cross-publisher and cross-regional analysis
- [ ] **Learning Progression Mapping**: Automatic prerequisite detection
- [ ] **Educational Standards Alignment**: Common Core, IB, A-Level mapping

### Long-term Vision
- [ ] **Adaptive Learning Integration**: Power personalized learning systems
- [ ] **Docker Containerization**: Simplified deployment and scaling
- [ ] **Cloud Deployment**: Serverless architecture for high availability
- [ ] **Real-time Monitoring**: Performance metrics and usage analytics
- [ ] **Educational Data Mining**: Advanced analytics on curriculum patterns 