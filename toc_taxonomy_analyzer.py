#!/usr/bin/env python3
"""
TOC Taxonomy Analyzer using GPT-4 Vision
========================================

This script analyzes table of contents screenshots using GPT-4 vision capabilities
to create detailed taxonomies based on the actual TOC content. Each Country_Grade_Subject
combination gets a comprehensive taxonomy with hierarchical levels.

Features:
- Parses TOC directory names to extract metadata
- Uses GPT-4 Turbo with vision for detailed analysis
- Generates taxonomies anchored on actual TOC content
- Supports batch processing of multiple books
- Outputs structured JSON according to REQUIREMENTS.md format
- Comprehensive error handling and logging
"""

import os
import json
import base64
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time
from dataclasses import dataclass

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not found. Install with: pip install python-dotenv")

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI library not found. Install with: pip install openai")
    exit(1)

try:
    from PIL import Image
except ImportError:
    print("❌ Pillow library not found. Install with: pip install Pillow")
    exit(1)


@dataclass
class BookMetadata:
    """Metadata extracted from TOC directory name."""
    subject: str
    grade: str
    book_title: str
    isbn: str
    country: str = "DE"  # Default to Germany based on existing content
    full_dir_name: str = ""
    
    
class TaxonomyAnalysisError(Exception):
    """Custom exception for taxonomy analysis errors."""
    pass


class TocTaxonomyAnalyzer:
    """
    Analyzes TOC screenshots to create detailed educational taxonomies.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1"):
        """
        Initialize the taxonomy analyzer.
        
        Args:
            api_key: OpenAI API key (will try to get from environment if not provided)
            model: OpenAI model to use (default: gpt-4.1 for best vision analysis)
        """
        self.model = model
        self.setup_logging()
        
        # Initialize OpenAI client
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise TaxonomyAnalysisError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                    "or pass api_key parameter."
                )
            self.client = OpenAI(api_key=api_key)
        
        self.logger.info(f"Initialized taxonomy analyzer with model: {model}")
    
    def setup_logging(self):
        """Setup logging for the analyzer."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def parse_directory_name(self, dir_name: str) -> BookMetadata:
        """
        Parse TOC directory name to extract metadata.
        
        Expected format: toc_{Subject}_{Grade}_{Book_Title}_{ISBN}
        
        Args:
            dir_name: Directory name to parse
            
        Returns:
            BookMetadata object with extracted information
        """
        self.logger.debug(f"Parsing directory name: {dir_name}")
        
        # Remove 'toc_' prefix if present
        clean_name = dir_name.replace('toc_', '') if dir_name.startswith('toc_') else dir_name
        
        # Split by underscore, but be careful with book titles that may contain underscores
        parts = clean_name.split('_')
        
        if len(parts) < 4:
            raise TaxonomyAnalysisError(f"Invalid directory name format: {dir_name}")
        
        # Extract ISBN (should be at the end and match ISBN pattern)
        isbn_pattern = r'978-\d-\d{2}-\d{6}-\d'
        isbn = None
        isbn_index = -1
        
        for i, part in enumerate(parts):
            if re.match(isbn_pattern, part):
                isbn = part
                isbn_index = i
                break
        
        if not isbn:
            raise TaxonomyAnalysisError(f"No valid ISBN found in directory name: {dir_name}")
        
        # Extract subject (first part)
        subject = parts[0]
        
        # Extract grade (second part, but handle complex grade patterns)
        grade = parts[1]
        
        # Handle complex grade patterns like "5_6", "12_13", "11_(G9)", "1._Fremdsprache", etc.
        grade_parts = [parts[1]]
        next_idx = 2
        
        # Check if next parts are also part of the grade
        while next_idx < isbn_index and len(parts[next_idx]) <= 15:  # Increased limit for "Fremdsprache"
            part = parts[next_idx]
            # Include if it's a grade pattern
            if (any(char.isdigit() for char in part) or 
                part in ['(G8)', '(G9)'] or 
                'Fremdsprache' in part or
                part in ['Berufliche', 'Schulen', 'Oberstufe']):
                grade_parts.append(part)
                next_idx += 1
            else:
                break
        
        grade = '_'.join(grade_parts)
        
        # Everything between grade and ISBN is book title
        book_title_parts = parts[next_idx:isbn_index]
        book_title = '_'.join(book_title_parts)
        
        # Normalize subject name
        subject_normalized = self._normalize_subject(subject)
        
        return BookMetadata(
            subject=subject_normalized,
            grade=grade,
            book_title=book_title,
            isbn=isbn,
            country="DE",  # Default to Germany
            full_dir_name=dir_name
        )
    
    def _normalize_subject(self, subject: str) -> str:
        """Normalize German subject names to standard format."""
        subject_mapping = {
            'Mathematik': 'Mathematics',
            'Deutsch': 'German Language',
            'Erdkunde': 'Geography', 
            'Geographie': 'Geography',
            'Geschichte': 'History',
            'Französisch': 'French',
            'Physik': 'Physics',
            'Chemie': 'Chemistry',
            'Biologie': 'Biology',
            'Informatik': 'Computer Science'
        }
        
        # Handle compound subjects (separated by commas or underscores)
        if ',' in subject:
            # Split by comma and clean each part
            subjects = [s.strip().replace('_', '') for s in subject.split(',')]
            normalized = [subject_mapping.get(s, s) for s in subjects]
            return ', '.join(normalized)
        
        return subject_mapping.get(subject, subject)
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 for OpenAI API.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise TaxonomyAnalysisError(f"Failed to encode image {image_path}: {e}")
    
    def analyze_toc_images(self, toc_dir: str, metadata: BookMetadata, max_depth: int = 3) -> Dict[str, Any]:
        """
        Analyze all TOC images in a directory to create a detailed taxonomy.
        
        Args:
            toc_dir: Path to directory containing TOC screenshots
            metadata: Book metadata
            max_depth: Maximum taxonomy depth levels
            
        Returns:
            Complete taxonomy structure according to REQUIREMENTS.md format
        """
        toc_path = Path(toc_dir)
        if not toc_path.exists():
            raise TaxonomyAnalysisError(f"TOC directory not found: {toc_dir}")
        
        # Find all PNG screenshots
        screenshots = list(toc_path.glob("*.png"))
        if not screenshots:
            raise TaxonomyAnalysisError(f"No screenshots found in {toc_dir}")
        
        # Sort screenshots by page number
        screenshots.sort(key=lambda x: x.name)
        
        self.logger.info(f"Analyzing {len(screenshots)} TOC screenshots for {metadata.subject} Grade {metadata.grade}")
        
        # Encode all images
        encoded_images = []
        for screenshot in screenshots:
            try:
                encoded_image = self.encode_image(str(screenshot))
                encoded_images.append({
                    'filename': screenshot.name,
                    'data': encoded_image
                })
            except Exception as e:
                self.logger.warning(f"Failed to encode {screenshot.name}: {e}")
                continue
        
        if not encoded_images:
            raise TaxonomyAnalysisError("No images could be encoded successfully")
        
        # Create comprehensive analysis prompt
        prompt = self._create_analysis_prompt(metadata, max_depth)
        
        # Prepare messages with all images
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ] + [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img['data']}",
                            "detail": "high"
                        }
                    } for img in encoded_images
                ]
            }
        ]
        
        try:
            self.logger.info(f"Sending {len(encoded_images)} images to GPT-4 for taxonomy analysis...")
            
            # Try with higher token limit first
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=4096,  # Increased for complex taxonomies
                    temperature=0.1  # Low temperature for consistent taxonomies
                )
            except Exception as e:
                if "maximum context length" in str(e).lower():
                    # Retry with lower token limit
                    self.logger.warning("Retrying with reduced token limit due to context length")
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=4000,
                        temperature=0.1
                    )
                else:
                    raise
            
            content = response.choices[0].message.content.strip()
            
            # Parse the JSON response with enhanced error handling
            try:
                # Clean up the response
                cleaned_content = self._clean_json_response(content)
                
                taxonomy_data = json.loads(cleaned_content)
                
                # Validate the structure
                self._validate_taxonomy_structure(taxonomy_data)
                
                self.logger.info(f"Successfully analyzed taxonomy with {len(taxonomy_data.get('taxonomy', []))} top-level topics")
                return taxonomy_data
                
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.error(f"Failed to parse taxonomy JSON: {e}")
                self.logger.error(f"Raw response length: {len(content)} chars")
                self.logger.debug(f"Raw response: {content}")
                
                # Try to repair the JSON
                repaired_data = self._attempt_json_repair(content, metadata)
                if repaired_data:
                    self.logger.warning("Used fallback JSON repair - results may be incomplete")
                    return repaired_data
                
                raise TaxonomyAnalysisError(f"Invalid JSON response from AI: {e}")
                
        except Exception as e:
            self.logger.error(f"Failed to analyze TOC images: {e}")
            raise TaxonomyAnalysisError(f"AI analysis failed: {e}")
    
    def _create_analysis_prompt(self, metadata: BookMetadata, max_depth: int) -> str:
        """Create detailed analysis prompt for GPT-4."""
        return f"""
You are an educational taxonomy generator. Analyze table of contents images and extract a hierarchical educational taxonomy.

**TASK**: Create a JSON taxonomy reflecting the actual curriculum structure for {metadata.subject}, Grade {metadata.grade}, {metadata.country}.

**ANALYSIS STEPS**:
1. Extract ALL visible topics and subtopics from the TOC images
2. Identify the pedagogical progression and learning sequence  
3. Group related educational concepts logically
4. Structure into hierarchy (max {max_depth} levels: 0=main topics, 1=subtopics, etc.)

**REQUIREMENTS**:
- Extract educational content only (exclude "Practice Exam", "Tests", "Exercises")
- Output in English
- Maintain educational sequence from source material
- Use exact JSON format below
- Depth should be so that the lowest level is something like "product rule" or "integration by parts" which is an isolated concept
- Names of the Topics and Subtopics should be adjusted so that students can understand them
- Include 5-15 relevant keyterms for each topic that students would associate with that concept (these don't have to appear in the TOC)

**OUTPUT FORMAT** (JSON only, no explanations):
```json
{{
    "country": "{metadata.country}",
    "grade": "{metadata.grade}", 
    "subject": "{metadata.subject}",
    "ISBN": "{metadata.isbn}",
    "taxonomy": [
        {{
            "name": "Main educational topic",
            "level": 0,
            "keyterms": ["term1", "term2", "term3", "term4", "term5"],
            "children": [
                {{
                    "name": "Subtopic",
                    "level": 1,
                    "keyterms": ["concept1", "concept2", "concept3"],
                    "children": []
                }}
            ]
        }}
    ]
}}
"""
    
    def _validate_taxonomy_structure(self, taxonomy_data: Dict[str, Any]) -> None:
        """Validate that taxonomy structure matches requirements."""
        required_fields = ['country', 'grade', 'subject', 'ISBN', 'taxonomy']
        for field in required_fields:
            if field not in taxonomy_data:
                raise TaxonomyAnalysisError(f"Missing required field: {field}")
        
        if not isinstance(taxonomy_data['taxonomy'], list):
            raise TaxonomyAnalysisError("Taxonomy must be a list")
        
        # Validate each taxonomy item
        for item in taxonomy_data['taxonomy']:
            self._validate_taxonomy_item(item)
    
    def _validate_taxonomy_item(self, item: Dict[str, Any]) -> None:
        """Validate individual taxonomy item structure."""
        required_fields = ['name', 'level', 'keyterms', 'children']
        for field in required_fields:
            if field not in item:
                raise TaxonomyAnalysisError(f"Missing required field in taxonomy item: {field}")
        
        if not isinstance(item['level'], int) or item['level'] < 0:
            raise TaxonomyAnalysisError(f"Invalid level: {item['level']}")
        
        if not isinstance(item['children'], list):
            raise TaxonomyAnalysisError("Children must be a list")
        
        if not isinstance(item['keyterms'], list):
            raise TaxonomyAnalysisError("Keyterms must be a list")
        
        # Validate keyterms length
        if len(item['keyterms']) < 3 or len(item['keyterms']) > 15:
            self.logger.warning(f"Keyterms for '{item['name']}' should have 5-15 items, found {len(item['keyterms'])}")
        
        # Recursively validate children
        for child in item['children']:
            self._validate_taxonomy_item(child)
    
    def process_all_toc_directories(self, tocs_dir: str = "tocs", output_dir: str = "taxonomies", max_depth: int = 3) -> Dict[str, Any]:
        """
        Process all TOC directories and generate taxonomies for each Country_Grade_Subject combination.
        
        Args:
            tocs_dir: Directory containing all TOC subdirectories
            output_dir: Directory to save taxonomy JSON files
            max_depth: Maximum taxonomy depth
            
        Returns:
            Summary of processing results
        """
        tocs_path = Path(tocs_dir)
        if not tocs_path.exists():
            raise TaxonomyAnalysisError(f"TOCs directory not found: {tocs_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Find all TOC directories
        toc_dirs = [d for d in tocs_path.iterdir() if d.is_dir()]
        if not toc_dirs:
            raise TaxonomyAnalysisError(f"No TOC directories found in {tocs_dir}")
        
        self.logger.info(f"Found {len(toc_dirs)} TOC directories to process")
        
        results = {
            'processed_books': {},
            'failed_books': {},
            'summary': {
                'total_books': len(toc_dirs),
                'successful': 0,
                'failed': 0,
                'total_topics_extracted': 0
            }
        }
        
        for i, toc_dir in enumerate(toc_dirs, 1):
            dir_name = toc_dir.name
            self.logger.info(f"Processing {i}/{len(toc_dirs)}: {dir_name}")
            
            try:
                # Parse metadata
                metadata = self.parse_directory_name(dir_name)
                
                # Analyze TOC images
                taxonomy_data = self.analyze_toc_images(str(toc_dir), metadata, max_depth)
                
                # Save taxonomy to file
                output_filename = f"taxonomy_{metadata.country}_{metadata.grade}_{metadata.subject}_{metadata.isbn}.json"
                output_file = output_path / output_filename
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(taxonomy_data, f, indent=2, ensure_ascii=False)
                
                # Track results
                topic_count = self._count_topics(taxonomy_data['taxonomy'])
                results['processed_books'][dir_name] = {
                    'metadata': metadata.__dict__,
                    'output_file': str(output_file),
                    'topic_count': topic_count,
                    'success': True
                }
                
                results['summary']['successful'] += 1
                results['summary']['total_topics_extracted'] += topic_count
                
                self.logger.info(f"✅ {dir_name}: {topic_count} topics extracted → {output_filename}")
                
                # Small delay to avoid overwhelming the API
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ {dir_name}: Failed - {e}")
                results['failed_books'][dir_name] = {
                    'error': str(e),
                    'error_type': type(e).__name__
                }
                results['summary']['failed'] += 1
        
        # Save processing report
        report_file = output_path / "processing_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Processing complete: {results['summary']['successful']}/{results['summary']['total_books']} successful")
        self.logger.info(f"Total topics extracted: {results['summary']['total_topics_extracted']}")
        self.logger.info(f"Report saved: {report_file}")
        
        return results
    
    def _clean_json_response(self, content: str) -> str:
        """Clean and prepare JSON response for parsing."""
        # Remove markdown code blocks
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        elif content.startswith('```'):
            content = content.replace('```', '').strip()
        
        # Handle common truncation issues
        content = content.strip()
        
        # If response is truncated, try to close JSON structures
        if not content.endswith('}') and not content.endswith(']'):
            # Count open brackets and try to close them
            open_braces = content.count('{') - content.count('}')
            open_brackets = content.count('[') - content.count(']')
            
            # Add missing closing brackets/braces
            for _ in range(open_brackets):
                content += ']'
            for _ in range(open_braces):
                content += '}'
        
        return content
    
    def _attempt_json_repair(self, content: str, metadata: BookMetadata) -> Optional[Dict[str, Any]]:
        """Attempt to repair truncated or malformed JSON."""
        try:
            # Find the taxonomy array start
            taxonomy_start = content.find('"taxonomy": [')
            if taxonomy_start == -1:
                return None
            
            # Extract what we can parse
            partial_content = content[:taxonomy_start + 13]  # Include "taxonomy": [
            
            # Try to extract at least some taxonomy items
            items = []
            current_pos = taxonomy_start + 13
            
            # Look for complete taxonomy items
            bracket_count = 0
            current_item = ""
            in_item = False
            
            for i, char in enumerate(content[current_pos:], current_pos):
                if char == '{':
                    if bracket_count == 0:
                        in_item = True
                        current_item = "{"
                    else:
                        current_item += char
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    current_item += char
                    if bracket_count == 0 and in_item:
                        # Complete item found
                        try:
                            item_data = json.loads(current_item)
                            items.append(item_data)
                            current_item = ""
                            in_item = False
                        except:
                            pass
                elif in_item:
                    current_item += char
                
                # Stop if we have enough items or hit length limit
                if len(items) >= 5 or i > len(content) - 100:
                    break
            
            if items:
                # Create minimal valid taxonomy with keyterms
                for item in items[:5]:
                    if 'keyterms' not in item:
                        item['keyterms'] = []
                
                return {
                    "country": metadata.country,
                    "grade": metadata.grade,
                    "subject": metadata.subject,
                    "ISBN": metadata.isbn,
                    "taxonomy": items[:5]  # Limit to first 5 items
                }
        
        except Exception as e:
            self.logger.debug(f"JSON repair attempt failed: {e}")
        
        return None
    
    def _count_topics(self, taxonomy: List[Dict[str, Any]]) -> int:
        """Count total number of topics in taxonomy."""
        count = len(taxonomy)
        for item in taxonomy:
            count += self._count_topics(item.get('children', []))
        return count
    
    def _get_max_level(self, item: Dict[str, Any]) -> int:
        """Get the maximum level in a taxonomy item and its children."""
        max_level = item.get('level', 0)
        for child in item.get('children', []):
            child_max = self._get_max_level(child)
            max_level = max(max_level, child_max)
        return max_level


def main():
    """Main function to run taxonomy analysis."""
    print("📊 TOC Taxonomy Analyzer using GPT-4 Vision")
    print("=" * 60)
    print()
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("Set your API key with: export OPENAI_API_KEY='your-api-key-here'")
        print("Or create .env file with: OPENAI_API_KEY=your-key-here")
        return
    
    try:
        # Initialize analyzer
        print("🔧 Initializing taxonomy analyzer...")
        analyzer = TocTaxonomyAnalyzer()
        
        # Ask for configuration
        max_depth = input("Maximum taxonomy depth (1-5, default=3): ").strip()
        try:
            max_depth = max(1, min(5, int(max_depth)))
        except ValueError:
            max_depth = 3
        
        print(f"\n📊 Configuration:")
        print(f"   • Model: GPT-4 Turbo")
        print(f"   • Max depth: {max_depth} levels")
        print(f"   • Output: taxonomies/ directory")
        print()
        
        # Process all TOC directories
        print("🚀 Starting batch taxonomy analysis...")
        start_time = time.time()
        
        results = analyzer.process_all_toc_directories(max_depth=max_depth)
        
        total_time = time.time() - start_time
        
        # Display results
        print(f"\n📊 Analysis Results (completed in {total_time:.1f}s):")
        print("-" * 60)
        
        summary = results['summary']
        print(f"📚 Books analyzed: {summary['total_books']}")
        print(f"✅ Successful: {summary['successful']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📖 Total topics extracted: {summary['total_topics_extracted']}")
        
        if summary['failed'] > 0:
            print(f"\n❌ Failed books:")
            for book, error_info in results['failed_books'].items():
                print(f"   • {book}: {error_info['error']}")
        
        avg_topics = summary['total_topics_extracted'] / max(summary['successful'], 1)
        print(f"\n📊 Average topics per book: {avg_topics:.1f}")
        print(f"💾 Taxonomies saved in: taxonomies/")
        print(f"📄 Processing report: taxonomies/processing_report.json")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")


if __name__ == "__main__":
    main() 