#!/usr/bin/env python3
"""
Single Book TOC Taxonomy Analysis
=================================

This script analyzes a single TOC book directory and generates a detailed
taxonomy. Perfect for analyzing one specific book.

Usage:
    python analyze_single_book.py path/to/toc_book_directory/
    python analyze_single_book.py --tocs-dir path/to/toc_book_directory/ --output-dir results/
"""

import os
import sys
import argparse
import json
from pathlib import Path
from toc_taxonomy_analyzer import TocTaxonomyAnalyzer, TaxonomyAnalysisError

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Single Book TOC Taxonomy Analysis - Analyze one TOC book directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_single_book.py tocs/toc_Mathematik_5_Arbeitsheft_Mathematik_5_978-3-12-746811-3/
  python analyze_single_book.py --tocs-dir tocs/toc_Deutsch_5_.../ --output-dir results/
  python analyze_single_book.py --tocs-dir tocs/toc_Mathematik_12_13_.../ --max-depth 4

Analyzes a single TOC book directory and generates a detailed taxonomy JSON file.
        """
    )
    
    parser.add_argument(
        'toc_directory',
        nargs='?',
        help='Path to single TOC book directory (alternative to --tocs-dir)'
    )
    
    parser.add_argument(
        '--tocs-dir',
        type=str,
        help='Path to single TOC book directory'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='taxonomies',
        help='Output directory for taxonomy JSON file (default: taxonomies)'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=3,
        help='Maximum taxonomy depth levels (default: 3)'
    )
    
    return parser.parse_args()

def analyze_single_book(toc_dir: str, output_dir: str = "taxonomies", max_depth: int = 3):
    """Analyze a single TOC book directory."""
    
    print("📖 Single Book TOC Taxonomy Analysis")
    print("=" * 50)
    print()
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key required!")
        print("Set your API key: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Validate input directory
    toc_path = Path(toc_dir)
    if not toc_path.exists():
        print(f"❌ TOC directory not found: {toc_dir}")
        return False
    
    if not toc_path.is_dir():
        print(f"❌ Path is not a directory: {toc_dir}")
        return False
    
    # Check for TOC images
    screenshots = list(toc_path.glob("*.png"))
    if not screenshots:
        print(f"❌ No PNG screenshots found in: {toc_dir}")
        return False
    
    print(f"📁 Analyzing: {toc_path.name}")
    print(f"📸 Found: {len(screenshots)} TOC screenshots")
    print(f"📊 Max depth: {max_depth} levels")
    print(f"💾 Output: {output_dir}/")
    print()
    
    try:
        # Initialize analyzer
        print("🔧 Initializing analyzer...")
        analyzer = TocTaxonomyAnalyzer()
        
        # Parse directory metadata
        print("📝 Parsing directory metadata...")
        try:
            metadata = analyzer.parse_directory_name(toc_path.name)
            print(f"   • Subject: {metadata.subject}")
            print(f"   • Grade: {metadata.grade}")
            print(f"   • Book: {metadata.book_title}")
            print(f"   • ISBN: {metadata.isbn}")
            print(f"   • Country: {metadata.country}")
        except Exception as e:
            print(f"❌ Failed to parse directory name: {e}")
            return False
        
        print()
        print("🚀 Starting analysis...")
        print("⏳ This may take 30-60 seconds...")
        print()
        
        # Analyze TOC images
        taxonomy_data = analyzer.analyze_toc_images(str(toc_path), metadata, max_depth)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save taxonomy
        output_filename = f"taxonomy_{metadata.country}_{metadata.grade}_{metadata.subject}_{metadata.isbn}.json"
        output_file = output_path / output_filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(taxonomy_data, f, indent=2, ensure_ascii=False)
        
        # Display results
        print("✅ Analysis completed successfully!")
        print()
        print("📊 Results:")
        print(f"   • Country: {taxonomy_data['country']}")
        print(f"   • Grade: {taxonomy_data['grade']}")
        print(f"   • Subject: {taxonomy_data['subject']}")
        print(f"   • ISBN: {taxonomy_data['ISBN']}")
        
        taxonomy = taxonomy_data['taxonomy']
        total_topics = analyzer._count_topics(taxonomy)
        print(f"   • Total topics: {total_topics}")
        print(f"   • Main categories: {len(taxonomy)}")
        
        if taxonomy:
            max_level = max([analyzer._get_max_level(item) for item in taxonomy])
            print(f"   • Levels used: 0-{max_level}")
        
        print()
        print(f"💾 Saved to: {output_file}")
        
        # Show sample taxonomy structure
        if taxonomy:
            print("\n📖 Sample taxonomy structure:")
            print("-" * 40)
            for i, item in enumerate(taxonomy[:3], 1):  # Show first 3 items
                print(f"{i}. {item['name']} (Level {item['level']})")
                for child in item.get('children', [])[:2]:  # Show first 2 children
                    print(f"   • {child['name']} (Level {child['level']})")
            if len(taxonomy) > 3:
                print(f"   ... and {len(taxonomy) - 3} more main topics")
        
        return True
        
    except TaxonomyAnalysisError as e:
        print(f"❌ Analysis failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    args = parse_arguments()
    
    # Determine TOC directory
    toc_dir = args.toc_directory or args.tocs_dir
    
    if not toc_dir:
        print("❌ TOC directory required!")
        print("Usage:")
        print("  python analyze_single_book.py path/to/toc_directory/")
        print("  python analyze_single_book.py --tocs-dir path/to/toc_directory/")
        print()
        print("Examples:")
        print("  python analyze_single_book.py tocs/toc_Mathematik_5_Arbeitsheft_Mathematik_5_978-3-12-746811-3/")
        return
    
    # Run analysis
    success = analyze_single_book(
        toc_dir=toc_dir,
        output_dir=args.output_dir,
        max_depth=args.max_depth
    )
    
    if success:
        print("\n🎉 Single book analysis completed successfully!")
    else:
        print("\n⚠️ Analysis failed. Check error messages above.")

if __name__ == "__main__":
    main() 