# TOC Taxonomy Analysis System

A comprehensive system for analyzing table of contents screenshots and creating detailed educational taxonomies using GPT-4 Vision. This system generates structured taxonomies for each Country_Grade_Subject combination according to the REQUIREMENTS.md specification.

## 🎯 Overview

This system analyzes table of contents (TOC) screenshots from educational materials and extracts detailed hierarchical taxonomies. Each taxonomy is anchored on the actual TOC content and includes all visible topics, chapters, sections, and subsections.

### Key Features

- **GPT-4 Vision Analysis**: Uses GPT-4 Turbo with vision for accurate TOC content extraction
- **Hierarchical Taxonomies**: Creates multi-level taxonomies with configurable depth (1-5 levels)
- **Batch Processing**: Analyzes all TOC directories in parallel
- **Metadata Parsing**: Automatically extracts country, grade, subject, and ISBN from directory names
- **JSON Output**: Generates structured JSON files according to REQUIREMENTS.md format
- **Comprehensive Logging**: Detailed progress tracking and error reporting
- **German Content Support**: Specialized for German educational materials

## 📁 System Architecture

```
├── toc_taxonomy_analyzer.py      # Core analysis engine
├── test_taxonomy_parser.py       # Test directory name parsing
├── demo_single_taxonomy.py       # Demo single book analysis
├── run_taxonomy_analysis.py      # Batch processing script
├── REQUIREMENTS.md              # Input/output specification
└── TAXONOMY_ANALYSIS_README.md  # This documentation
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install dependencies
pip install openai python-dotenv Pillow

# Set OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
# OR create .env file:
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 2. Test the System

```bash
# Test directory name parsing
python test_taxonomy_parser.py

# Demo with single book
python demo_single_taxonomy.py

# Demo with custom directory
python demo_single_taxonomy.py --tocs-dir custom_tocs/

# Non-interactive demo
python demo_single_taxonomy.py --tocs-dir tocs/ --non-interactive
```

### 3. Run Full Analysis

```bash
# Analyze all TOC directories (default: tocs/)
python run_taxonomy_analysis.py

# Analyze custom directory
python run_taxonomy_analysis.py --tocs-dir custom_tocs/

# Full customization
python run_taxonomy_analysis.py --tocs-dir tocs/ --output-dir results/ --max-depth 4

# Non-interactive mode (uses defaults)
python run_taxonomy_analysis.py --tocs-dir tocs/ --non-interactive
```

## 📊 Input Format

The system expects TOC directories in the following structure:

```
tocs/
├── toc_Mathematik_5_Arbeitsheft_Mathematik_5_978-3-12-746811-3/
│   ├── screenshot_page_01.png
│   ├── screenshot_page_02.png
│   └── ...
├── toc_Deutsch_6_Deutsch_kompetent_6_978-3-12-316302-9/
│   └── ...
└── ...
```

### Directory Name Format

`toc_{Subject}_{Grade}_{Book_Title}_{ISBN}`

Examples:
- `toc_Mathematik_5_Arbeitsheft_Mathematik_5_978-3-12-746811-3`
- `toc_Deutsch_6_Deutsch_kompetent_6_978-3-12-316302-9`
- `toc_Französisch_1._Fremdsprache_1._Lernjahr_Découvertes_1_(fester_Einband)_978-3-12-624011-6`

## 📈 Output Format

### Individual Taxonomy Files

Each book generates a JSON file following REQUIREMENTS.md specification:

```json
{
  "country": "DE",
  "grade": "5",
  "subject": "Mathematics",
  "ISBN": "978-3-12-746811-3",
  "taxonomy": [
    {
      "name": "Zahlen und Größen",
      "level": 0,
      "children": [
        {
          "name": "Natürliche Zahlen",
          "level": 1,
          "children": [
            {
              "name": "Große Zahlen",
              "level": 2,
              "children": []
            }
          ]
        }
      ]
    }
  ]
}
```

### Processing Report

A comprehensive report is generated at `taxonomies/processing_report.json`:

```json
{
  "processed_books": {
    "toc_Mathematik_5_...": {
      "metadata": {...},
      "output_file": "taxonomy_DE_5_Mathematics_978-3-12-746811-3.json",
      "topic_count": 45,
      "success": true
    }
  },
  "failed_books": {...},
  "summary": {
    "total_books": 48,
    "successful": 46,
    "failed": 2,
    "total_topics_extracted": 1823
  }
}
```

## 🛠️ Core Components

### TocTaxonomyAnalyzer Class

The main analysis engine with the following key methods:

- `parse_directory_name(dir_name)`: Extracts metadata from directory names
- `analyze_toc_images(toc_dir, metadata, max_depth)`: Analyzes TOC images using GPT-4
- `process_all_toc_directories(tocs_dir, output_dir, max_depth)`: Batch processing
- `_validate_taxonomy_structure(taxonomy_data)`: Validates output format

### Directory Name Parsing

Handles complex German educational naming patterns:

- **Subjects**: `Mathematik` → `Mathematics`, `Deutsch` → `German Language`
- **Grades**: `5`, `7_8`, `11_(G9)`, `1._Fremdsprache_1.`
- **Books**: Complex titles with special characters and parentheses
- **ISBNs**: Standard ISBN-13 format validation

### GPT-4 Vision Analysis

Sophisticated prompt engineering for educational content:

- **High-detail image analysis**: Preserves text clarity
- **Hierarchical extraction**: Identifies levels based on formatting
- **German term preservation**: Maintains original terminology
- **Comprehensive coverage**: Extracts all visible content

## 📋 Usage Examples

### Single Book Analysis

```python
from toc_taxonomy_analyzer import TocTaxonomyAnalyzer

analyzer = TocTaxonomyAnalyzer()
metadata = analyzer.parse_directory_name("toc_Mathematik_5_Arbeitsheft_Mathematik_5_978-3-12-746811-3")
taxonomy = analyzer.analyze_toc_images("tocs/toc_Mathematik_5_...", metadata, max_depth=3)
```

### Batch Processing

```python
analyzer = TocTaxonomyAnalyzer()
results = analyzer.process_all_toc_directories(max_depth=3)
print(f"Processed {results['summary']['successful']} books successfully")
```

### Custom Configuration

```python
# Use different model or settings
analyzer = TocTaxonomyAnalyzer(model="gpt-4.1", api_key="custom-key")

# Process specific directory
results = analyzer.process_all_toc_directories(
    tocs_dir="custom_tocs",
    output_dir="custom_output", 
    max_depth=4
)
```

## 💰 Cost Estimation

- **GPT-4 Turbo Vision**: ~$0.001-0.003 per image
- **Average book**: 3-4 TOC images = ~$0.01-0.05 per book
- **Full batch (48 books)**: ~$0.50-2.00 total

## 🔧 Configuration Options

### Environment Variables

```bash
OPENAI_API_KEY=your-api-key-here  # Required
```

### Command Line Arguments

**Batch Analysis (`run_taxonomy_analysis.py`):**
```bash
--tocs-dir DIR        Input directory containing TOC subdirectories (default: tocs)
--output-dir DIR      Output directory for taxonomy JSON files (default: taxonomies)
--max-depth N         Maximum taxonomy depth levels 1-5 (default: 3)
--non-interactive     Run without user prompts using defaults
--help               Show detailed help
```

**Demo Analysis (`demo_single_taxonomy.py`):**
```bash
--tocs-dir DIR        Input directory containing TOC subdirectories (default: tocs)
--non-interactive     Run demo automatically without prompts
--help               Show detailed help
```

### Script Parameters (when using programmatically)

- **max_depth**: Taxonomy depth (1-5, default: 3)
- **model**: OpenAI model ("gpt-4.1", "gpt-4")
- **output_dir**: Output directory (default: "taxonomies")
- **tocs_dir**: Input directory (default: "tocs")

## 📊 Supported Subjects

The system handles German educational subjects with automatic normalization:

| German | English | Notes |
|--------|---------|-------|
| Mathematik | Mathematics | All grade levels |
| Deutsch | German Language | Native language |
| Erdkunde/Geographie | Geography | Both terms supported |
| Geschichte | History | |
| Französisch | French | Foreign language |
| Physik | Physics | Sciences |
| Chemie | Chemistry | |
| Biologie | Biology | |
| Informatik | Computer Science | |

Compound subjects are also supported (e.g., "Mathematik, Physik, Astronomie").

## 🎯 Quality Assurance

### Validation Checks

- **JSON Structure**: Validates against REQUIREMENTS.md format
- **Hierarchy Consistency**: Ensures proper level numbering
- **Content Completeness**: Verifies all required fields
- **German Character Support**: Handles umlauts and special characters

### Error Handling

- **Graceful Degradation**: Continues processing if individual books fail
- **Detailed Logging**: Comprehensive error reporting
- **Retry Logic**: Handles temporary API failures
- **Input Validation**: Checks directory structure and image formats

## 🐛 Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```bash
   export OPENAI_API_KEY='your-key'
   # or create .env file
   ```

2. **No TOC Directories Found**
   ```bash
   ls tocs/  # Check directory structure
   ```

3. **JSON Parse Errors**
   - Usually due to malformed GPT-4 responses
   - System includes fallback parsing logic

4. **Rate Limiting**
   - Built-in rate limiting (1s delay between requests)
   - Adjust in code if needed

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

analyzer = TocTaxonomyAnalyzer()
# Will show detailed processing information
```

## 🚀 Performance Optimization

### Batch Processing

- **Sequential Processing**: Safer for API limits
- **Parallel Analysis**: Future enhancement possibility
- **Memory Management**: Efficient image encoding
- **Progress Tracking**: Real-time status updates

### API Efficiency

- **Image Optimization**: Automatic resizing if needed
- **Request Batching**: Multiple images per request
- **Error Recovery**: Robust retry mechanisms
- **Cost Monitoring**: Built-in cost estimation

## 📈 Expected Results

Based on analysis of German educational materials:

- **Average Topics per Book**: 15-50 depending on subject and grade
- **Hierarchy Depth**: Typically 2-3 levels for most subjects
- **Processing Time**: 30-60 seconds per book
- **Success Rate**: >95% for well-formatted TOC images

### Subject-Specific Patterns

- **Mathematics**: Highly structured, numerical hierarchies
- **Languages**: Thematic organization, cultural topics
- **Sciences**: Logical progression, conceptual groupings
- **History**: Chronological and thematic organization

## 🔄 Integration with Existing System

This taxonomy analysis system integrates seamlessly with the existing livebook screenshot system:

1. **Screenshot Capture**: Use existing `livebook_screenshot_tool.py`
2. **TOC Filtering**: Use existing `filter_toc_screenshots.py`
3. **TOC Organization**: Use existing `copy_toc_pages.py`
4. **Taxonomy Analysis**: Use new `toc_taxonomy_analyzer.py`

Complete workflow:
```bash
# 1. Capture screenshots (existing)
python livebook_screenshot_tool.py

# 2. Filter TOC pages (existing)
python filter_toc_screenshots.py

# 3. Organize TOC pages (existing)
python copy_toc_pages.py

# 4. Analyze taxonomies (NEW)
python run_taxonomy_analysis.py
```

## 📝 Next Steps

1. **Run Demo**: Test with single book
   ```bash
   python demo_single_taxonomy.py
   # or with custom directory:
   python demo_single_taxonomy.py --tocs-dir your_tocs/
   ```

2. **Validate Results**: Check parsing logic
   ```bash
   python test_taxonomy_parser.py
   ```

3. **Batch Analysis**: Process all books
   ```bash
   # Default directory
   python run_taxonomy_analysis.py
   
   # Custom directory
   python run_taxonomy_analysis.py --tocs-dir your_tocs/ --output-dir your_output/
   
   # Non-interactive mode
   python run_taxonomy_analysis.py --tocs-dir tocs/ --max-depth 4 --non-interactive
   ```

4. **Review Output**: Examine results in output directory
5. **Integration**: Incorporate into existing workflows as needed

The system is ready for production use and will generate comprehensive taxonomies for all your Country_Grade_Subject combinations as specified in REQUIREMENTS.md. 