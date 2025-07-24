#!/usr/bin/env python3
"""
TOC Screenshot Filter using OpenAI GPT-4o mini
==============================================

This script uses OpenAI's GPT-4o mini with vision capabilities to automatically
analyze screenshots and filter out those that are not part of a book's table of contents.

Features:
- Analyzes screenshots using AI vision
- Identifies genuine TOC content vs other book pages
- Organizes filtered results
- Supports batch processing of multiple ISBN directories
- Provides confidence scores and detailed analysis
"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import time

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except ImportError:
    print("⚠️ python-dotenv not found. Install with: pip install python-dotenv")
    print("💡 You can still set OPENAI_API_KEY as a regular environment variable")

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


class TOCFilterError(Exception):
    """Custom exception for TOC filtering operations."""
    pass


class TOCScreenshotFilter:
    """
    AI-powered filter to identify table of contents screenshots.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the TOC filter.
        
        Args:
            api_key: OpenAI API key (will try to get from environment if not provided)
            model: OpenAI model to use (default: gpt-4o-mini)
        """
        self.model = model
        self.setup_logging()
        
        # Initialize OpenAI client
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Try to get from environment
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise TOCFilterError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                    "or pass api_key parameter."
                )
            self.client = OpenAI(api_key=api_key)
        
        self.logger.info(f"Initialized TOC filter with model: {model}")
    
    def setup_logging(self):
        """Setup logging for the filter."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 for OpenAI API.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        try:
            # Optimize image size for API (reduce if too large)
            with Image.open(image_path) as img:
                # Resize if image is too large (max 2048px width)
                if img.width > 2048:
                    ratio = 2048 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((2048, new_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save to temporary bytes
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                image_bytes = buffer.getvalue()
            
            return base64.b64encode(image_bytes).decode('utf-8')
            
        except Exception as e:
            raise TOCFilterError(f"Failed to encode image {image_path}: {e}")
    
    def analyze_screenshot(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze a single screenshot to determine if it contains TOC content.
        
        Args:
            image_path: Path to the screenshot to analyze
            
        Returns:
            Dict with analysis results including is_toc, confidence, and reasoning
        """
        self.logger.info(f"Analyzing screenshot: {image_path}")
        
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Prepare the prompt
            prompt = """
            You are an expert at analyzing educational book screenshots to identify table of contents (TOC) pages.
            
            Please analyze this screenshot and determine if it contains a table of contents or index.
            
            Look for these TOC indicators:
            - Chapter listings with page numbers
            - Organized hierarchical content structure
            - "Inhaltsverzeichnis", "Inhalt", "Contents", "Index" headings
            - Sequential chapter/section numbering
            - Lists of topics with corresponding page numbers
            - Structured layout typical of a table of contents
            
            NOT table of contents:
            - Regular book content/text pages
            - Exercise pages
            - Images or diagrams without TOC structure
            - Individual chapters or lessons
            - Navigation elements that aren't content listings
            
            Respond with a JSON object containing:
            {
                "is_toc": boolean (true if this is a table of contents),
                "confidence": float (0.0-1.0, how confident you are),
                "reasoning": string (explanation of your decision),
                "toc_elements_found": array of strings (specific TOC elements you identified),
                "language": string (detected language of the content)
            }
            """
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent analysis
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            try:
                # Try to parse as JSON
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                result = json.loads(content)
                
                # Validate required fields
                required_fields = ['is_toc', 'confidence', 'reasoning']
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Missing required field: {field}")
                
                self.logger.info(f"Analysis complete: TOC={result['is_toc']}, Confidence={result['confidence']:.2f}")
                return result
                
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(f"Failed to parse AI response as JSON: {e}")
                # Fallback: analyze text response
                is_toc = any(keyword in content.lower() for keyword in [
                    'table of contents', 'is a toc', 'contains toc', 'inhaltsverzeichnis'
                ])
                
                return {
                    'is_toc': is_toc,
                    'confidence': 0.5,
                    'reasoning': f"Fallback analysis based on keywords in: {content[:200]}...",
                    'toc_elements_found': [],
                    'language': 'unknown',
                    'raw_response': content
                }
                
        except Exception as e:
            self.logger.error(f"Failed to analyze screenshot {image_path}: {e}")
            return {
                'is_toc': False,
                'confidence': 0.0,
                'reasoning': f"Analysis failed: {str(e)}",
                'error': str(e)
            }
    
    def filter_isbn_directory(self, isbn_dir: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Filter all screenshots in an ISBN directory to identify TOC pages.
        
        Args:
            isbn_dir: Path to the ISBN directory containing screenshots
            confidence_threshold: Minimum confidence score to consider a page as TOC
            
        Returns:
            Dict with filtering results and TOC pages identified
        """
        isbn_path = Path(isbn_dir)
        if not isbn_path.exists():
            raise TOCFilterError(f"ISBN directory not found: {isbn_dir}")
        
        isbn = isbn_path.name
        self.logger.info(f"Filtering screenshots for ISBN: {isbn}")
        
        # Find all PNG screenshots
        screenshots = list(isbn_path.glob("*.png"))
        if not screenshots:
            self.logger.warning(f"No screenshots found in {isbn_dir}")
            return {
                'isbn': isbn,
                'total_screenshots': 0,
                'toc_pages': [],
                'non_toc_pages': [],
                'analysis_results': []
            }
        
        # Sort screenshots by page number
        screenshots.sort(key=lambda x: x.name)
        
        self.logger.info(f"Found {len(screenshots)} screenshots to analyze")
        
        analysis_results = []
        toc_pages = []
        non_toc_pages = []
        
        for i, screenshot in enumerate(screenshots, 1):
            self.logger.info(f"Analyzing page {i}/{len(screenshots)}: {screenshot.name}")
            
            # Analyze screenshot
            result = self.analyze_screenshot(str(screenshot))
            result['filename'] = screenshot.name
            result['page_number'] = i
            
            analysis_results.append(result)
            
            # Categorize based on confidence threshold
            if result.get('is_toc', False) and result.get('confidence', 0) >= confidence_threshold:
                toc_pages.append({
                    'filename': screenshot.name,
                    'confidence': result['confidence'],
                    'reasoning': result['reasoning'],
                    'page_number': i
                })
            else:
                non_toc_pages.append({
                    'filename': screenshot.name,
                    'is_toc': result.get('is_toc', False),
                    'confidence': result.get('confidence', 0),
                    'reasoning': result['reasoning'],
                    'page_number': i
                })
            
            # Small delay to avoid API rate limits
            time.sleep(0.5)
        
        result_summary = {
            'isbn': isbn,
            'total_screenshots': len(screenshots),
            'toc_pages': toc_pages,
            'non_toc_pages': non_toc_pages,
            'analysis_results': analysis_results,
            'confidence_threshold': confidence_threshold
        }
        
        self.logger.info(f"Filtering complete for {isbn}: {len(toc_pages)} TOC pages, {len(non_toc_pages)} non-TOC pages")
        
        return result_summary
    
    def filter_batch_directories(self, screenshots_dir: str = "screenshots", 
                                confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Filter screenshots in all ISBN directories.
        
        Args:
            screenshots_dir: Base screenshots directory containing ISBN subdirectories
            confidence_threshold: Minimum confidence score to consider a page as TOC
            
        Returns:
            Dict with results for all ISBNs processed
        """
        screenshots_path = Path(screenshots_dir)
        if not screenshots_path.exists():
            raise TOCFilterError(f"Screenshots directory not found: {screenshots_dir}")
        
        # Find all ISBN directories (directories that look like ISBNs)
        isbn_dirs = [d for d in screenshots_path.iterdir() 
                    if d.is_dir() and any(c.isdigit() for c in d.name)]
        
        if not isbn_dirs:
            self.logger.warning(f"No ISBN directories found in {screenshots_dir}")
            return {'processed_isbns': {}, 'summary': {}}
        
        self.logger.info(f"Found {len(isbn_dirs)} ISBN directories to process")
        
        batch_results = {}
        
        for isbn_dir in isbn_dirs:
            try:
                self.logger.info(f"Processing ISBN directory: {isbn_dir.name}")
                result = self.filter_isbn_directory(str(isbn_dir), confidence_threshold)
                batch_results[isbn_dir.name] = result
                
            except Exception as e:
                self.logger.error(f"Failed to process {isbn_dir.name}: {e}")
                batch_results[isbn_dir.name] = {
                    'error': str(e),
                    'isbn': isbn_dir.name,
                    'total_screenshots': 0,
                    'toc_pages': [],
                    'non_toc_pages': []
                }
        
        # Generate summary
        total_books = len(batch_results)
        total_screenshots = sum(r.get('total_screenshots', 0) for r in batch_results.values())
        total_toc_pages = sum(len(r.get('toc_pages', [])) for r in batch_results.values())
        total_non_toc_pages = sum(len(r.get('non_toc_pages', [])) for r in batch_results.values())
        
        summary = {
            'total_books_processed': total_books,
            'total_screenshots_analyzed': total_screenshots,
            'total_toc_pages_found': total_toc_pages,
            'total_non_toc_pages': total_non_toc_pages,
            'confidence_threshold': confidence_threshold
        }
        
        self.logger.info(f"Batch filtering complete: {total_toc_pages} TOC pages found from {total_screenshots} screenshots across {total_books} books")
        
        return {
            'processed_isbns': batch_results,
            'summary': summary
        }
    
    def organize_filtered_results(self, batch_results: Dict[str, Any], 
                                 organize_files: bool = True) -> None:
        """
        Organize filtered results by moving TOC screenshots to separate directories.
        
        Args:
            batch_results: Results from filter_batch_directories
            organize_files: If True, actually move files; if False, just report what would be moved
        """
        if 'processed_isbns' not in batch_results:
            raise TOCFilterError("Invalid batch results format")
        
        for isbn, results in batch_results['processed_isbns'].items():
            if 'error' in results:
                continue
            
            isbn_dir = Path("screenshots") / isbn
            toc_dir = isbn_dir / "toc_pages"
            non_toc_dir = isbn_dir / "non_toc_pages"
            
            if organize_files:
                # Create directories
                toc_dir.mkdir(exist_ok=True)
                non_toc_dir.mkdir(exist_ok=True)
            
            # Move TOC pages
            for toc_page in results.get('toc_pages', []):
                source = isbn_dir / toc_page['filename']
                target = toc_dir / toc_page['filename']
                
                if organize_files and source.exists():
                    source.rename(target)
                    self.logger.info(f"Moved TOC page: {toc_page['filename']} -> toc_pages/")
                else:
                    self.logger.info(f"Would move TOC page: {toc_page['filename']} -> toc_pages/")
            
            # Move non-TOC pages
            for non_toc_page in results.get('non_toc_pages', []):
                source = isbn_dir / non_toc_page['filename']
                target = non_toc_dir / non_toc_page['filename']
                
                if organize_files and source.exists():
                    source.rename(target)
                    self.logger.info(f"Moved non-TOC page: {non_toc_page['filename']} -> non_toc_pages/")
                else:
                    self.logger.info(f"Would move non-TOC page: {non_toc_page['filename']} -> non_toc_pages/")
    
    def save_analysis_report(self, batch_results: Dict[str, Any], 
                           output_file: str = "toc_analysis_report.json") -> None:
        """
        Save detailed analysis report to JSON file.
        
        Args:
            batch_results: Results from filter_batch_directories
            output_file: Path to save the report
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(batch_results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Analysis report saved to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save analysis report: {e}")


def main():
    """Main function to run TOC filtering."""
    print("📚 TOC Screenshot Filter using OpenAI GPT-4o mini")
    print("=" * 60)
    print()
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("Set your API key with: export OPENAI_API_KEY='your-api-key-here'")
        print("Or pass it as a parameter to the TOCScreenshotFilter class")
        return
    
    try:
        # Initialize filter
        filter_tool = TOCScreenshotFilter()
        
        # Filter all screenshots
        print("🔍 Analyzing all screenshots to identify TOC pages...")
        results = filter_tool.filter_batch_directories(confidence_threshold=0.7)
        
        # Display results
        print("\n📊 Analysis Results:")
        print("-" * 50)
        
        summary = results['summary']
        print(f"📚 Books processed: {summary['total_books_processed']}")
        print(f"📄 Screenshots analyzed: {summary['total_screenshots_analyzed']}")
        print(f"✅ TOC pages found: {summary['total_toc_pages_found']}")
        print(f"❌ Non-TOC pages: {summary['total_non_toc_pages']}")
        print(f"🎯 Confidence threshold: {summary['confidence_threshold']}")
        
        # Show details for each book
        print(f"\n📋 Detailed Results by ISBN:")
        print("-" * 50)
        
        for isbn, book_results in results['processed_isbns'].items():
            if 'error' in book_results:
                print(f"❌ {isbn}: Error - {book_results['error']}")
                continue
            
            toc_count = len(book_results['toc_pages'])
            total_count = book_results['total_screenshots']
            
            print(f"📖 {isbn}:")
            print(f"   📄 Total pages: {total_count}")
            print(f"   ✅ TOC pages: {toc_count}")
            
            if toc_count > 0:
                print("   📑 TOC pages found:")
                for toc_page in book_results['toc_pages']:
                    conf = toc_page['confidence']
                    print(f"      • {toc_page['filename']} (confidence: {conf:.2f})")
        
        # Ask about organizing files
        print(f"\n🗂️ File Organization:")
        organize = input("Do you want to organize files into toc_pages/ and non_toc_pages/ subdirectories? (y/N): ").strip().lower()
        
        if organize == 'y':
            print("📁 Organizing files...")
            filter_tool.organize_filtered_results(results, organize_files=True)
            print("✅ Files organized!")
        else:
            print("📋 Files not moved. You can run organization later.")
        
        # Save report
        print("\n💾 Saving analysis report...")
        filter_tool.save_analysis_report(results)
        print("✅ Report saved to: toc_analysis_report.json")
        
    except TOCFilterError as e:
        print(f"❌ TOC Filter Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main() 