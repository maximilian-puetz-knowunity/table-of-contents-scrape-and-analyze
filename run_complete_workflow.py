#!/usr/bin/env python3
"""
Complete Livebook TOC Extraction Workflow
=========================================

This script demonstrates the complete workflow for extracting table of contents from Livebooks:

1. 📸 Screenshot Capture: Capture all pages for specified ISBNs
2. 🤖 AI Filtering: Use GPT-4o mini to identify actual TOC pages  
3. 📁 Organization: Automatically organize files into TOC and non-TOC folders

Prerequisites:
- OpenAI API Key: Create a .env file with OPENAI_API_KEY=your-key-here
- Dependencies: Run pip install -r requirements.txt
- Chrome Browser: Installed on your system
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any

# Import additional modules for cleaning
import re

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not found. Install with: pip install python-dotenv")
    print("💡 You can still set OPENAI_API_KEY as a regular environment variable")

# Import our tools
try:
    from livebook_screenshot_tool import LivebookScreenshotTool
    print("✅ Screenshot tool imported successfully")
except ImportError as e:
    print(f"❌ Failed to import screenshot tool: {e}")
    exit(1)

try:
    from filter_toc_screenshots import TOCScreenshotFilter, TOCFilterError
    print("✅ AI filter tool imported successfully")
except ImportError as e:
    print(f"❌ Failed to import AI filter tool: {e}")
    exit(1)

print("\n🚀 All imports completed!")

def clean_filename(text: str) -> str:
    """
    Clean text to be safe for use in filenames and directory names.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text safe for filesystem use
    """
    # Replace problematic characters with underscores
    cleaned = re.sub(r'[<>:"/\\|?*\s]', '_', str(text))
    
    # Remove multiple consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    
    return cleaned

def generate_book_directory_name(book: Dict[str, str]) -> str:
    """
    Generate a consistent directory name for a book.
    
    Args:
        book (Dict[str, str]): Book dictionary with keys: isbn, name, subject, grade
        
    Returns:
        str: Directory name in format {subject}_{grade}_{name}_{isbn}
    """
    subject = clean_filename(book['subject'])
    grade = clean_filename(book['grade'])
    name = clean_filename(book['name'])
    isbn = clean_filename(book['isbn'])
    
    return f"{subject}_{grade}_{name}_{isbn}"

# Configuration Settings
# =====================

# ISBN List to Process
BOOK_LIST = [
{
    "isbn": "978-3-12-316301-2",
    "name": "Deutsch kompetent 5",
    "subject": "Deutsch",
    "grade": "5"
},
{
    "isbn": "978-3-12-316302-9",
    "name": "Deutsch kompetent 6",
    "subject": "Deutsch",
    "grade": "6"
},
{
    "isbn": "978-3-12-316303-6",
    "name": "Deutsch kompetent 7",
    "subject": "Deutsch",
    "grade": "7"
},
{
    "isbn": "978-3-12-316304-3",
    "name": "Deutsch kompetent 8",
    "subject": "Deutsch",
    "grade": "8"
},
{
    "isbn": "978-3-12-316305-0",
    "name": "Deutsch kompetent 9",
    "subject": "Deutsch",
    "grade": "9"
},
{
    "isbn": "978-3-12-316306-7",
    "name": "Deutsch kompetent 10",
    "subject": "Deutsch",
    "grade": "10"
},
{
    "isbn": "978-3-12-350550-8",
    "name": "Deutsch kompetent 11",
    "subject": "Deutsch",
    "grade": "11"
},
{
    "isbn": "978-3-12-350552-2",
    "name": "Deutsch kompetent 11-13",
    "subject": "Deutsch",
    "grade": "11-13"
},
{
    "isbn": "978-3-12-350551-5",
    "name": "Deutsch kompetent 12/13",
    "subject": "Deutsch",
    "grade": "12/13"
},
{
    "isbn": "978-3-12-746811-3",
    "name": "Arbeitsheft Mathematik 5",
    "subject": "Mathematik",
    "grade": "5"
},
{
    "isbn": "978-3-12-746812-0",
    "name": "Arbeitsheft Mathematik 6",
    "subject": "Mathematik",
    "grade": "6"
},
{
    "isbn": "978-3-12-746813-7",
    "name": "Arbeitsheft Mathematik 7",
    "subject": "Mathematik",
    "grade": "7"
},
{
    "isbn": "978-3-12-746814-4",
    "name": "Arbeitsheft Mathematik 8",
    "subject": "Mathematik",
    "grade": "8"
},
{
    "isbn": "978-3-12-746815-1",
    "name": "Arbeitsheft Mathematik 9",
    "subject": "Mathematik",
    "grade": "9"
},
{
    "isbn": "978-3-12-746816-8",
    "name": "Arbeitsheft Mathematik 10",
    "subject": "Mathematik",
    "grade": "10"
},
{
    "isbn": "978-3-12-735471-3",
    "name": "Lambacher Schweizer Mathematik Einführungsphase",
    "subject": "Mathematik",
    "grade": "11"
},
{
    "isbn": "978-3-12-735481-2",
    "name": "Lambacher Schweizer Mathematik Qualifikationsphase Leistungskurs/Grundkurs",
    "subject": "Mathematik",
    "grade": "12/13"
},
{
    "isbn": "978-3-12-735491-1",
    "name": "Lambacher Schweizer Mathematik Qualifikationsphase Grundkurs",
    "subject": "Mathematik",
    "grade": "12/13"
},
{
    "isbn": "978-3-12-770800-4",
    "name": "Physikalische Formeln und Daten",
    "subject": "Physik",
    "grade": "10-13"
},
{
    "isbn": "978-3-12-718510-2",
    "name": "Formelsammlung Mathematik Gymnasium, Mathematik und Physik",
    "subject": "Mathematik, Mathematik Gymnasium, Physik",
    "grade": "8-13"
},
{
    "isbn": "978-3-12-718512-6",
    "name": "Tafelwerk Mathematik, Physik, Astronomie, Chemie, Biologie, Informatik (fester Einband)",
    "subject": "Mathematik, Physik, Astronomie, Chemie, Biologie, Informatik",
    "grade": "8-13"
},
{
    "isbn": "978-3-12-772601-5",
    "name": "Formeln und Daten zur Physik",
    "subject": "Physik",
    "grade": "10-12 (G8), 11-13 (G9)"
},
{
    "isbn": "978-3-12-718513-3",
    "name": "Tafelwerk Mathematik, Physik, Astronomie, Chemie, Biologie, Informatik (flexibler Einband)",
    "subject": "Mathematik, Physik, Astronomie, Chemie, Biologie, Informatik",
    "grade": "8-13"
},
{
    "isbn": "978-3-12-718521-8",
    "name": "Alle Formeln kompakt",
    "subject": "Mathematik",
    "grade": "8-13"
},
{
    "isbn": "978-3-12-718520-1",
    "name": "Alle Formeln kompakt",
    "subject": "Mathematik, Physik",
    "grade": "8-13"
},
{
    "isbn": "978-3-12-718522-5",
    "name": "Alle Formeln kompakt",
    "subject": "Mathematik Berufliche Schulen Oberstufe",
    "grade": "8-13"
},
{
    "isbn": "978-3-12-718523-2",
    "name": "Alle Formeln kompakt - Tafelwerk",
    "subject": "Mathematik, Physik, Astronomie, Informatik, Chemie, Biologie",
    "grade": "8-13"
},
{
    "isbn": "978-3-12-735000-5",
    "name": "IQB Mathematisch-naturwissenschaftliche Formelsammlung für die Abiturprüfung",
    "subject": "Mathematik, Chemie, Physik",
    "grade": "10-12 oder 11-13"
},
{
    "isbn": "ECI70122EBD12",
    "name": "Alle Formeln kompakt - Tafelwerk (eBook PrintPlus Lizenz Schule)",
    "subject": "Mathematik, Physik, Astronomie, Informatik, Chemie, Biologie",
    "grade": "8-13"
},
{
    "isbn": "ECI70122EBA12",
    "name": "Alle Formeln kompakt - Tafelwerk (eBook Einzellizenz)",
    "subject": "Mathematik, Physik, Astronomie, Informatik, Chemie, Biologie",
    "grade": "8-13"
},
{
    "isbn": "978-3-12-744342-4",
    "name": "Formelsammlung Mathematik für Sekundarstufe I",
    "subject": "Mathematik",
    "grade": "5-10"
},
{
    "isbn": "978-3-12-104783-3",
    "name": "Terra Geographie Einführungsphase",
    "subject": "Erdkunde",
    "grade": "11 (G9)"
},
{
    "isbn": "978-3-12-104784-0",
    "name": "Terra Geographie Qualifikationsphase",
    "subject": "Erdkunde",
    "grade": "12/13 (G9)"
},
{
    "isbn": "978-3-12-105201-1",
    "name": "Terra Erdkunde 1",
    "subject": "Erdkunde",
    "grade": "5/6"
},
{
    "isbn": "978-3-12-105202-8",
    "name": "Terra Erdkunde 2",
    "subject": "Erdkunde",
    "grade": "7/8"
},
{
    "isbn": "978-3-12-105204-2",
    "name": "Terra Erdkunde 1 (Arbeitsbuch mit eBook)",
    "subject": "Erdkunde",
    "grade": "5/6"
},
{
    "isbn": "978-3-12-105203-5",
    "name": "Terra Erdkunde 3",
    "subject": "Erdkunde",
    "grade": "9/10"
},
{
    "isbn": "978-3-12-105205-9",
    "name": "Terra Erdkunde 2 (Arbeitsbuch und eBook)",
    "subject": "Erdkunde",
    "grade": "7/8"
},
{
    "isbn": "978-3-12-828730-0",
    "name": "Haack Weltatlas",
    "subject": "Erdkunde",
    "grade": "5-13"
},
{
    "isbn": "978-3-12-828730-0",
    "name": "Haack Weltatlas",
    "subject": "Geographie",
    "grade": "5-13"
},
{
    "isbn": "978-3-12-624012-3",
    "name": "Découvertes 1 (flexibler Einband)",
    "subject": "Französisch 1. Fremdsprache",
    "grade": "1. Lernjahr"
},
{
    "isbn": "978-3-12-624011-6",
    "name": "Découvertes 1 (fester Einband)",
    "subject": "Französisch 1. Fremdsprache",
    "grade": "1. Lernjahr"
},
{
    "isbn": "978-3-12-624022-2",
    "name": "Découvertes 2 (flexibler Einband)",
    "subject": "Französisch 1. Fremdsprache",
    "grade": "2. Lernjahr"
},
{
    "isbn": "978-3-12-624021-5",
    "name": "Découvertes 2 (fester Einband)",
    "subject": "Französisch 1. Fremdsprache",
    "grade": "2. Lernjahr"
},
{
    "isbn": "978-3-12-624032-1",
    "name": "Découvertes 3 (flexibler Einband)",
    "subject": "Französisch 1. Fremdsprache",
    "grade": "3. Lernjahr"
},
{
    "isbn": "978-3-12-624031-4",
    "name": "Découvertes 3 (fester Einband)",
    "subject": "Französisch 1. Fremdsprache",
    "grade": "3. Lernjahr"
},
{
    "isbn": "978-3-12-624041-3",
    "name": "Découvertes 4 (fester Einband)",
    "subject": "Französisch 1. Fremdsprache",
    "grade": "4. Lernjahr"
},
{
    "isbn": "978-3-12-624042-0",
    "name": "Découvertes 4 (flexibler Einband)",
    "subject": "Französisch 1. Fremdsprache",
    "grade": "4. Lernjahr"
},
{
    "isbn": "978-3-12-624052-9",
    "name": "Découvertes 5 (flexibler Einband)",
    "subject": "Französisch 1. Fremdsprache",
    "grade": "5. Lernjahr"
},
{
    "isbn": "978-3-12-624051-2",
    "name": "Découvertes 5 (fester Einband)",
    "subject": "Französisch 1. Fremdsprache",
    "grade": "5. Lernjahr"
},
{
    "isbn": "978-3-12-443015-1",
    "name": "Geschichte und Geschehen 1",
    "subject": "Geschichte",
    "grade": "5/6 (G9)"
},
{
    "isbn": "978-3-12-443025-0",
    "name": "Geschichte und Geschehen 2",
    "subject": "Geschichte",
    "grade": "7/8 (G9)"
},
{
    "isbn": "978-3-12-443035-9",
    "name": "Geschichte und Geschehen 3",
    "subject": "Geschichte",
    "grade": "9 (G9)"
},
{
    "isbn": "978-3-12-443045-8",
    "name": "Geschichte und Geschehen 4",
    "subject": "Geschichte",
    "grade": "10 (G9)"
}
]


# Workflow Settings
MAX_PAGES_PER_BOOK = 10        # Stop after 10 pages per book
CONFIDENCE_THRESHOLD = 0.7     # AI confidence threshold for TOC identification
HEADLESS_MODE = True           # Run browser in headless mode
AUTO_ORGANIZE = True           # Automatically organize files after filtering

def display_configuration():
    """Display current configuration."""
    print("⚙️ Workflow Configuration:")
    print(f"📚 ISBNs to process: {len(BOOK_LIST)}")
    for i, book in enumerate(BOOK_LIST, 1):
        print(f"   {i}. {book['name']} ({book['isbn']})")
    print(f"📄 Max pages per book: {MAX_PAGES_PER_BOOK}")
    print(f"🎯 AI confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"👻 Headless mode: {HEADLESS_MODE}")
    print(f"🗂️ Auto-organize files: {AUTO_ORGANIZE}")

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"🔑 OpenAI API key: {'*' * 20}{api_key[-4:]}")
    else:
        print("❌ OpenAI API key not found!")
        print("   Create .env file with: OPENAI_API_KEY=your-key-here")
        return False

    print("\n✅ Configuration ready!")
    return True

def capture_screenshots_step(book_list: List[Dict[str, str]], max_pages: int = 10) -> Dict[str, Any]:
    """
    Step 1: Capture screenshots for all books.
    """
    print("\n📸 Step 1: Screenshot Capture")
    print("=" * 50)
    
    def progress_callback(book_index, total_books, book_info):
        """Update progress for current book."""
        percent = (book_index + 1) / total_books * 100
        print(f"📊 Progress: {percent:.1f}% - Processing {book_info['name']} ({book_info['isbn']})")
    
    try:
        with LivebookScreenshotTool(headless=HEADLESS_MODE) as tool:
            print("🚀 Starting screenshot capture...")
            
            # Capture screenshots for all books
            results = tool.screenshot_book_batch(
                book_list=book_list,
                max_pages=max_pages,
                progress_callback=progress_callback
            )
            
            # Calculate summary
            successful_books = sum(1 for r in results.values() if r['success'])
            total_pages = sum(r.get('total_pages', 0) for r in results.values() if r['success'])
            total_size = sum(r.get('total_size', 0) for r in results.values() if r['success'])
            
            print(f"\n📊 Screenshot Summary:")
            print(f"   ✅ Successful: {successful_books}/{len(book_list)} books")
            print(f"   📄 Total pages: {total_pages}")
            print(f"   💾 Total size: {total_size / (1024 * 1024):.1f} MB")
            
            for book_key, result in results.items():
                if result['success']:
                    pages = result['total_pages']
                    print(f"   📖 {book_key}: {pages} pages")
                else:
                    print(f"   ❌ {book_key}: Failed")
            
            return results
            
    except Exception as e:
        print(f"❌ Screenshot capture failed: {e}")
        return None

def filter_toc_step(screenshots_dir: str = "screenshots") -> Dict[str, Any]:
    """
    Step 2: Use AI to filter screenshots and identify TOC pages.
    """
    print("\n🤖 Step 2: AI-Powered TOC Filtering")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found!")
        print("   Create .env file with: OPENAI_API_KEY=your-key-here")
        return None
    
    # Find book directories (new format: {subject}_{grade}_{name}_{isbn})
    book_dirs = [d for d in os.listdir(screenshots_dir) 
                if os.path.isdir(os.path.join(screenshots_dir, d)) and d != "testrun"]
    
    if not book_dirs:
        print("❌ No book directories found")
        return None
    
    try:
        # Initialize filter
        print("🔧 Initializing AI filter...")
        filter_tool = TOCScreenshotFilter()
        
        # Track progress and results
        all_results = {}
        total_toc_pages = 0
        total_analyzed = 0
        total_cost = 0.0
        
        for i, book_dir in enumerate(book_dirs):
            print(f"📖 Analyzing {book_dir} ({i + 1}/{len(book_dirs)})...")
            
            try:
                # Analyze this book directory
                book_results = filter_tool.filter_isbn_directory(
                    os.path.join(screenshots_dir, book_dir),
                    confidence_threshold=CONFIDENCE_THRESHOLD
                )
                
                all_results[book_dir] = book_results
                
                # Update counters
                book_toc_pages = len(book_results['toc_pages'])
                book_total_pages = book_results['total_screenshots']
                book_cost = book_total_pages * 0.00015
                
                total_toc_pages += book_toc_pages
                total_analyzed += book_total_pages
                total_cost += book_cost
                
                print(f"   ✅ {book_dir}: {book_toc_pages}/{book_total_pages} pages are TOC (${book_cost:.4f})")
                
                if book_toc_pages > 0:
                    for page in book_results['toc_pages']:
                        conf = page['confidence']
                        print(f"      📄 {page['filename']} (confidence: {conf:.2f})")
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ {book_dir}: Failed - {e}")
                all_results[book_dir] = {'error': str(e)}
        
        # Create summary results
        summary_results = {
            'processed_books': all_results,
            'summary': {
                'total_books_processed': len(book_dirs),
                'total_screenshots_analyzed': total_analyzed,
                'total_toc_pages_found': total_toc_pages,
                'total_non_toc_pages': total_analyzed - total_toc_pages,
                'confidence_threshold': CONFIDENCE_THRESHOLD,
                'estimated_cost': total_cost
            }
        }
        
        print(f"\n📊 AI Analysis Summary:")
        print(f"   📚 Books analyzed: {len(book_dirs)}")
        print(f"   📄 Screenshots analyzed: {total_analyzed}")
        print(f"   ✅ TOC pages found: {total_toc_pages}")
        print(f"   ❌ Non-TOC pages: {total_analyzed - total_toc_pages}")
        print(f"   💰 Total cost: ${total_cost:.4f}")
        
        return summary_results
        
    except Exception as e:
        print(f"❌ AI filtering failed: {e}")
        return None

def organize_files_step(filter_results: Dict[str, Any]) -> None:
    """
    Step 3: Organize filtered files into TOC and non-TOC folders.
    """
    print("\n📁 Step 3: File Organization")
    print("=" * 50)
    
    if not filter_results:
        print("❌ No filter results available. Step 2 must complete successfully first.")
        return
    
    try:
        # Initialize filter tool for organization
        filter_tool = TOCScreenshotFilter()
        
        if AUTO_ORGANIZE:
            print("🗂️ Automatically organizing files...")
            
            # Organize files
            filter_tool.organize_filtered_results(filter_results, organize_files=True)
            
            print("✅ Files organized successfully!")
        else:
            print("📋 File organization preview (not moving files):")
            filter_tool.organize_filtered_results(filter_results, organize_files=False)
        
        # Save detailed report
        report_file = "reports/toc_analysis_report.json"
        filter_tool.save_analysis_report(filter_results, report_file)
        print(f"💾 Detailed report saved: {report_file}")
        
        # Display organization summary
        print("\n📊 Final Organization Summary:")
        print("-" * 60)
        
        for book_dir, results in filter_results['processed_books'].items():
            if 'error' in results:
                print(f"❌ {book_dir}: {results['error']}")
                continue
            
            toc_count = len(results['toc_pages'])
            non_toc_count = len(results['non_toc_pages'])
            total_count = results['total_screenshots']
            
            print(f"📖 {book_dir}:")
            print(f"   📄 Total pages: {total_count}")
            print(f"   ✅ TOC pages: {toc_count} → screenshots/{book_dir}/toc_pages/")
            print(f"   ❌ Other pages: {non_toc_count} → screenshots/{book_dir}/non_toc_pages/")
            
            if toc_count > 0:
                print("   📑 TOC files:")
                for page in results['toc_pages']:
                    conf = page['confidence']
                    print(f"      • {page['filename']} (confidence: {conf:.2f})")
            print()
        
        summary = filter_results['summary']
        print(f"🎯 Step 3 Complete!")
        print(f"   📚 Books processed: {summary['total_books_processed']}")
        print(f"   📄 Pages analyzed: {summary['total_screenshots_analyzed']}")
        print(f"   ✅ TOC pages found: {summary['total_toc_pages_found']}")
        print(f"   💰 AI analysis cost: ${summary['estimated_cost']:.4f}")
        
    except Exception as e:
        print(f"❌ File organization failed: {e}")

def display_final_summary(screenshot_results, filter_results):
    """
    Display final workflow summary and next steps.
    """
    print("\n🎉 Complete Livebook TOC Extraction Workflow - FINISHED!")
    print("=" * 70)
    
    if not screenshot_results:
        print("❌ Screenshot capture was not successful")
        return
    
    if not filter_results:
        print("❌ AI filtering was not successful")
        return
    
    # Success! Show complete summary
    summary = filter_results['summary']
    
    print(f"✅ Workflow completed successfully!")
    print(f"\n📊 Final Results:")
    print(f"   📚 Books processed: {summary['total_books_processed']}")
    print(f"   📄 Screenshots captured: {summary['total_screenshots_analyzed']}")
    print(f"   🎯 TOC pages identified: {summary['total_toc_pages_found']}")
    print(f"   💰 Total AI cost: ${summary['estimated_cost']:.4f}")
    
    print(f"\n📁 Your organized files are available in:")
    for book in BOOK_LIST:
        # Create directory name using the utility function
        dir_name = generate_book_directory_name(book)
        
        book_dir = Path(f"screenshots/{dir_name}")
        if book_dir.exists():
            toc_dir = book_dir / "toc_pages"
            non_toc_dir = book_dir / "non_toc_pages"
            
            if toc_dir.exists():
                toc_files = list(toc_dir.glob("*.png"))
                print(f"   📖 {book['name']} ({book['isbn']}):")
                print(f"      ✅ TOC pages: {len(toc_files)} files in {toc_dir}")
                if non_toc_dir.exists():
                    non_toc_files = list(non_toc_dir.glob("*.png"))
                    print(f"      📄 Other pages: {len(non_toc_files)} files in {non_toc_dir}")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Review TOC pages in the toc_pages/ folders")
    print(f"   2. Check the detailed report: reports/toc_analysis_report.json")
    print(f"   3. Use the TOC screenshots for your project")
    
    print(f"\n💡 To run this workflow again:")
    print(f"   1. Update the BOOK_LIST in this script")
    print(f"   2. Run: python run_complete_workflow.py")
    
    print(f"\n🎯 Perfect! You now have clean, AI-filtered TOC screenshots!")

def confirm_before_analysis():
    """
    Ask user to check the Google Drive content before proceeding with analysis.
    Returns True if user confirms, False if they cancel.
    """
    print("\n" + "="*60)
    print("📋 IMPORTANT: Before Starting Analysis")
    print("="*60)
    print()
    print("🔍 Please review the content and instructions at:")
    print("🔗 https://drive.google.com/drive/folders/17xeeabkqmq1hABvsymUSPOusC-Aqbmes?usp=drive_link")
    print()
    print("📖 This contains important information about:")
    print("   • Data collection guidelines")
    print("   • Usage requirements") 
    print("   • Best practices for analysis")
    print("   • Legal and ethical considerations")
    print()
    print("⚠️  Please read through the content in the Google Drive before proceeding.")
    print()
    
    while True:
        response = input("✅ Have you reviewed the content and want to proceed with the analysis? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\n✅ Proceeding with analysis...")
            return True
        elif response in ['n', 'no', '']:
            print("\n❌ Analysis cancelled. Please review the content and run again when ready.")
            return False
        else:
            print("⚠️  Please enter 'y' for yes or 'n' for no.")

def main():
    """
    Run the complete workflow: capture -> filter -> organize.
    """
    print("🚀 Complete Livebook TOC Extraction Workflow")
    print("=" * 60)
    print(f"📋 Processing {len(BOOK_LIST)} books")
    print(f"📄 Max {MAX_PAGES_PER_BOOK} pages per book")
    print(f"🎯 AI confidence threshold: {CONFIDENCE_THRESHOLD}")
    print()
    
    # Display and check configuration
    if not display_configuration():
        print("❌ Configuration invalid. Please fix and try again.")
        return
    
    # Ask user to confirm after reviewing Google Drive content
    if not confirm_before_analysis():
        return
    
    print("\n" + "="*60)
    print("Starting 3-step workflow...")
    print("="*60)
    
    # Step 1: Capture screenshots
    screenshot_results = capture_screenshots_step(BOOK_LIST, MAX_PAGES_PER_BOOK)
    if not screenshot_results:
        print("❌ Workflow stopped - screenshot capture failed")
        return
    
    # Step 2: Filter TOC pages with AI
    filter_results = filter_toc_step()
    if not filter_results:
        print("❌ Workflow stopped - AI filtering failed")
        return
    
    # Step 3: Organize files
    organize_files_step(filter_results)
    
    # Final summary
    display_final_summary(screenshot_results, filter_results)

if __name__ == "__main__":
    main() 