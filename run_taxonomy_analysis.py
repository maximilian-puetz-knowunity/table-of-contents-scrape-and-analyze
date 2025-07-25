#!/usr/bin/env python3
"""
Batch TOC Taxonomy Analysis
===========================

This script runs the complete taxonomy analysis workflow for all TOC directories,
generating detailed taxonomies for each Country_Grade_Subject combination as 
specified in REQUIREMENTS.md.

Usage:
    python run_taxonomy_analysis.py
    
Output:
    - Individual taxonomy JSON files for each book
    - Summary report with statistics
    - All files saved in taxonomies/ directory
"""

import os
import sys
import time
import argparse
from pathlib import Path
from toc_taxonomy_analyzer import TocTaxonomyAnalyzer, TaxonomyAnalysisError

def show_configuration(tocs_dir_path: str):
    """Display current configuration and requirements."""
    print("📊 TOC Taxonomy Analysis - Batch Processing")
    print("=" * 70)
    print()
    
    # Check environment
    api_key = os.getenv('OPENAI_API_KEY')
    tocs_dir = Path(tocs_dir_path)
    
    print("🔧 Configuration Check:")
    print(f"   • OpenAI API Key: {'✅ Found' if api_key else '❌ Missing'}")
    print(f"   • TOCs Directory: {tocs_dir_path}")
    print(f"   • Directory Exists: {'✅ Found' if tocs_dir.exists() else '❌ Missing'}")
    
    if tocs_dir.exists():
        toc_dirs = [d for d in tocs_dir.iterdir() if d.is_dir()]
        print(f"   • TOC Directories: {len(toc_dirs)} found")
        
        # Show examples
        print(f"\n📚 Example directories:")
        for i, toc_dir in enumerate(toc_dirs[:5], 1):
            name = toc_dir.name.replace('toc_', '')
            if len(name) > 60:
                name = name[:57] + "..."
            print(f"   {i}. {name}")
        if len(toc_dirs) > 5:
            print(f"   ... and {len(toc_dirs) - 5} more")
    
    print()
    
    # Show what this script does
    print("📋 This script will:")
    print("1. 🔍 Parse metadata from each TOC directory name")
    print("2. 🤖 Analyze TOC images using GPT-4 Turbo vision")
    print("3. 📊 Extract detailed educational taxonomies")
    print("4. 💾 Save individual JSON files per Country_Grade_Subject")
    print("5. 📄 Generate comprehensive processing report")
    print()
    
    # Cost estimation
    if tocs_dir.exists():
        total_images = 0
        for toc_dir in toc_dirs:
            screenshots = list(toc_dir.glob("*.png"))
            total_images += len(screenshots)
        
        estimated_cost = total_images * 0.0015  # Rough estimate for GPT-4 vision
        print(f"💰 Cost Estimate:")
        print(f"   • Total images to analyze: {total_images}")
        print(f"   • Estimated cost: ${estimated_cost:.2f}")
        if len(toc_dirs) > 0:
            print(f"   • Average per book: ${estimated_cost/len(toc_dirs):.3f}")
    print()
    
    return api_key is not None and tocs_dir.exists()

def run_batch_analysis(tocs_dir: str, output_dir: str = None, max_depth: int = None, interactive: bool = True):
    """Run the complete batch analysis."""
    
    # Configuration check
    if not show_configuration(tocs_dir):
        print("❌ Configuration incomplete. Please fix the issues above and try again.")
        return False
    
    # Get user configuration
    if interactive:
        print("⚙️  Analysis Configuration:")
        
        if max_depth is None:
            max_depth_input = input("Maximum taxonomy depth (1-5, default=3): ").strip()
            try:
                max_depth = max(1, min(5, int(max_depth_input)))
            except ValueError:
                max_depth = 3
        
        if output_dir is None:
            output_dir = input("Output directory (default=taxonomies): ").strip()
            if not output_dir:
                output_dir = "taxonomies"
        
        # Confirmation
        print(f"\n✅ Configuration:")
        print(f"   • Model: GPT-4 Turbo")
        print(f"   • Input directory: {tocs_dir}")
        print(f"   • Max depth: {max_depth} levels")
        print(f"   • Output directory: {output_dir}/")
        print()
        
        proceed = input("Start batch analysis? This may take several minutes (y/N): ").strip().lower()
        if proceed != 'y':
            print("Analysis cancelled.")
            return False
    else:
        # Non-interactive mode - use defaults if not provided
        if max_depth is None:
            max_depth = 3
        if output_dir is None:
            output_dir = "taxonomies"
        
        print(f"\n✅ Running analysis:")
        print(f"   • Input directory: {tocs_dir}")
        print(f"   • Max depth: {max_depth} levels")
        print(f"   • Output directory: {output_dir}/")
    
    print("\n🚀 Starting batch taxonomy analysis...")
    print("=" * 50)
    
    try:
        # Initialize analyzer
        analyzer = TocTaxonomyAnalyzer()
        
        # Run batch processing
        start_time = time.time()
        results = analyzer.process_all_toc_directories(
            tocs_dir=tocs_dir,
            output_dir=output_dir,
            max_depth=max_depth
        )
        total_time = time.time() - start_time
        
        # Display comprehensive results
        print(f"\n🎉 Batch Analysis Complete!")
        print("=" * 50)
        
        summary = results['summary']
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        print(f"📚 Books processed: {summary['total_books']}")
        print(f"✅ Successful: {summary['successful']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📖 Total topics extracted: {summary['total_topics_extracted']}")
        
        if summary['successful'] > 0:
            avg_topics = summary['total_topics_extracted'] / summary['successful']
            avg_time = total_time / summary['successful']
            print(f"📊 Average topics per book: {avg_topics:.1f}")
            print(f"⚡ Average time per book: {avg_time:.1f}s")
        
        # Show successful results by subject
        if results['processed_books']:
            print(f"\n📈 Results by Subject:")
            subject_stats = {}
            for book_info in results['processed_books'].values():
                if book_info['success']:
                    subject = book_info['metadata']['subject']
                    if subject not in subject_stats:
                        subject_stats[subject] = {'count': 0, 'topics': 0}
                    subject_stats[subject]['count'] += 1
                    subject_stats[subject]['topics'] += book_info['topic_count']
            
            for subject, stats in sorted(subject_stats.items()):
                avg_topics = stats['topics'] / stats['count']
                print(f"   • {subject}: {stats['count']} books, {avg_topics:.1f} avg topics")
        
        # Show failed results
        if summary['failed'] > 0:
            print(f"\n❌ Failed Analysis ({summary['failed']} books):")
            for book, error_info in results['failed_books'].items():
                short_name = book.replace('toc_', '')[:50]
                if len(short_name) < len(book) - 4:
                    short_name += "..."
                print(f"   • {short_name}")
                print(f"     Error: {error_info['error']}")
        
        print(f"\n💾 Results saved in: {output_dir}/")
        print(f"📄 Processing report: {output_dir}/processing_report.json")
        
        # Show sample output files
        output_path = Path(output_dir)
        json_files = list(output_path.glob("taxonomy_*.json"))
        if json_files:
            print(f"\n📁 Sample output files:")
            for i, json_file in enumerate(json_files[:3], 1):
                print(f"   {i}. {json_file.name}")
            if len(json_files) > 3:
                print(f"   ... and {len(json_files) - 3} more")
        
        return True
        
    except TaxonomyAnalysisError as e:
        print(f"❌ Analysis failed: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⏸️  Analysis interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_usage_examples():
    """Show usage examples and next steps."""
    print("\n💡 Usage Examples:")
    print("=" * 40)
    print()
    print("🔍 Test single analysis first:")
    print("   python demo_single_taxonomy.py")
    print("   python demo_single_taxonomy.py --tocs-dir custom_tocs/")
    print()
    print("🧪 Test parsing logic:")
    print("   python test_taxonomy_parser.py")
    print()
    print("🚀 Run full batch analysis:")
    print("   python run_taxonomy_analysis.py")
    print("   python run_taxonomy_analysis.py --tocs-dir tocs/ --output-dir results/")
    print("   python run_taxonomy_analysis.py --tocs-dir custom_tocs/ --max-depth 4 --output-dir custom_output/")
    print()
    print("📊 Command line options:")
    print("   --tocs-dir DIR       Input directory containing TOC subdirectories")
    print("   --output-dir DIR     Output directory for taxonomy JSON files")
    print("   --max-depth N        Maximum taxonomy depth (1-5, default: 3)")
    print("   --non-interactive    Run without user prompts")
    print("   --help              Show detailed help")
    print()
    print("📊 Analyze results:")
    print("   ls taxonomies/")
    print("   cat taxonomies/processing_report.json")
    print()
    print("📁 Expected output structure:")
    print("   taxonomies/")
    print("   ├── taxonomy_DE_5_Mathematics_978-3-12-746811-3.json")
    print("   ├── taxonomy_DE_6_German Language_978-3-12-316302-9.json")
    print("   ├── taxonomy_DE_7_8_Geography_978-3-12-105202-8.json")
    print("   ├── ...")
    print("   └── processing_report.json")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="TOC Taxonomy Analysis System - Analyze table of contents screenshots to generate educational taxonomies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_taxonomy_analysis.py
  python run_taxonomy_analysis.py --tocs-dir custom_tocs/
  python run_taxonomy_analysis.py --tocs-dir tocs/ --output-dir results/ --max-depth 4
  python run_taxonomy_analysis.py --tocs-dir tocs/ --non-interactive

The script analyzes TOC screenshots using GPT-4 Vision and generates detailed
hierarchical taxonomies for each Country_Grade_Subject combination.
        """
    )
    
    parser.add_argument(
        '--tocs-dir',
        type=str,
        default='tocs',
        help='Input directory containing TOC subdirectories (default: tocs)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for taxonomy JSON files (default: taxonomies)'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=None,
        help='Maximum taxonomy depth levels (default: 3)'
    )
    
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run without user prompts using default values'
    )
    
    return parser.parse_args()

def main():
    """Main function."""
    print("🏁 TOC Taxonomy Analysis System")
    print("=" * 40)
    print()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Check for basic requirements
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key required!")
        print("Set your API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   or create .env file with: OPENAI_API_KEY=your-key")
        print()
        show_usage_examples()
        return
    
    # Check if specified TOCs directory exists
    tocs_path = Path(args.tocs_dir)
    if not tocs_path.exists():
        print(f"❌ TOCs directory not found: {args.tocs_dir}")
        print("Specify a valid directory with --tocs-dir or create the directory")
        print()
        show_usage_examples()
        return
    
    # Show configuration
    print(f"📁 Input directory: {args.tocs_dir}")
    if args.output_dir:
        print(f"📁 Output directory: {args.output_dir}")
    if args.max_depth:
        print(f"📊 Max depth: {args.max_depth}")
    if args.non_interactive:
        print("🤖 Non-interactive mode")
    print()
    
    # Run analysis
    success = run_batch_analysis(
        tocs_dir=args.tocs_dir,
        output_dir=args.output_dir,
        max_depth=args.max_depth,
        interactive=not args.non_interactive
    )
    
    if success:
        print("\n🎯 Analysis completed successfully!")
        output_dir = args.output_dir or "taxonomies"
        print(f"Check the {output_dir}/ directory for your results.")
    else:
        print("\n⚠️  Analysis completed with issues.")
        print("Check the error messages above for details.")

if __name__ == "__main__":
    main() 