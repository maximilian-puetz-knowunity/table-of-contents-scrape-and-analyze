#!/usr/bin/env python3
"""
Demo: Single TOC Taxonomy Analysis
=================================

This script demonstrates the complete taxonomy analysis workflow by analyzing
a single TOC directory and showing the detailed taxonomy extraction process.
"""

import os
import json
import argparse
from pathlib import Path
from toc_taxonomy_analyzer import TocTaxonomyAnalyzer, TaxonomyAnalysisError

def demo_single_analysis(tocs_dir_path: str = "tocs"):
    """Demonstrate taxonomy analysis with a single TOC directory."""
    
    print("🚀 Demo: Single TOC Taxonomy Analysis")
    print("=" * 60)
    print()
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("This demo requires an OpenAI API key to analyze TOC images.")
        print("Set your API key with: export OPENAI_API_KEY='your-api-key-here'")
        print("Or create .env file with: OPENAI_API_KEY=your-key-here")
        return
    
    # Find available TOC directories
    tocs_dir = Path(tocs_dir_path)
    print(f"📁 Looking for TOC directories in: {tocs_dir_path}")
    if not tocs_dir.exists():
        print(f"❌ TOCs directory not found: {tocs_dir_path}")
        return
    
    toc_dirs = [d for d in tocs_dir.iterdir() if d.is_dir()]
    if not toc_dirs:
        print("❌ No TOC directories found")
        return
    
    # Show available directories and let user choose
    print("📚 Available TOC Directories:")
    print()
    
    # Filter for some good examples (prefer simpler subjects first)
    examples = []
    for toc_dir in toc_dirs:
        name = toc_dir.name
        if any(subject in name for subject in ['Mathematik_5_', 'Mathematik_9_', 'Deutsch_5_', 'Deutsch_6_']):
            examples.append(toc_dir)
    
    # If no good examples, use first few directories
    if not examples:
        examples = toc_dirs[:5]
    
    for i, toc_dir in enumerate(examples[:5], 1):
        name = toc_dir.name
        # Shorten name for display
        display_name = name.replace('toc_', '').replace('_978-3-12-', '_')
        if len(display_name) > 60:
            display_name = display_name[:57] + "..."
        print(f"   {i}. {display_name}")
    
    print()
    choice = input(f"Choose a directory to analyze (1-{min(5, len(examples))}, default=1): ").strip()
    
    try:
        choice_idx = int(choice) - 1 if choice else 0
        if choice_idx < 0 or choice_idx >= len(examples):
            choice_idx = 0
    except ValueError:
        choice_idx = 0
    
    selected_dir = examples[choice_idx]
    print(f"\n📖 Selected: {selected_dir.name}")
    print()
    
    try:
        # Initialize analyzer
        print("🔧 Initializing taxonomy analyzer...")
        analyzer = TocTaxonomyAnalyzer()
        
        # Parse directory metadata
        print("📝 Parsing directory metadata...")
        metadata = analyzer.parse_directory_name(selected_dir.name)
        
        print(f"   • Subject: {metadata.subject}")
        print(f"   • Grade: {metadata.grade}")
        print(f"   • Book: {metadata.book_title}")
        print(f"   • ISBN: {metadata.isbn}")
        print(f"   • Country: {metadata.country}")
        print()
        
        # Check images in directory
        screenshots = list(selected_dir.glob("*.png"))
        print(f"📸 Found {len(screenshots)} TOC screenshots:")
        for screenshot in screenshots:
            size_mb = screenshot.stat().st_size / (1024 * 1024)
            print(f"   • {screenshot.name} ({size_mb:.1f}MB)")
        print()
        
        # Ask for confirmation and max depth
        max_depth = input("Maximum taxonomy depth (1-5, default=3): ").strip()
        try:
            max_depth = max(1, min(5, int(max_depth)))
        except ValueError:
            max_depth = 3
        
        print(f"\n🚀 Starting analysis with max depth {max_depth}...")
        print("⏳ This may take 30-60 seconds depending on the number of images...")
        print()
        
        # Perform analysis
        taxonomy_data = analyzer.analyze_toc_images(str(selected_dir), metadata, max_depth)
        
        # Display results
        print("✅ Analysis completed successfully!")
        print()
        print("📊 Taxonomy Results:")
        print("=" * 40)
        
        # Display basic info
        print(f"Country: {taxonomy_data['country']}")
        print(f"Grade: {taxonomy_data['grade']}")
        print(f"Subject: {taxonomy_data['subject']}")
        print(f"ISBN: {taxonomy_data['ISBN']}")
        print()
        
        # Display taxonomy structure
        taxonomy = taxonomy_data['taxonomy']
        total_topics = analyzer._count_topics(taxonomy)
        print(f"📖 Extracted {total_topics} topics in {len(taxonomy)} main categories:")
        print()
        
        # Display structured taxonomy
        def display_taxonomy_item(item, indent=""):
            level_indicator = "  " * item['level']
            print(f"{indent}{level_indicator}• {item['name']} (Level {item['level']})")
            for child in item.get('children', []):
                display_taxonomy_item(child, indent)
        
        for i, item in enumerate(taxonomy):
            print(f"{i+1}. {item['name']} (Level {item['level']})")
            for child in item.get('children', []):
                display_taxonomy_item(child, "   ")
            print()
        
        # Save results
        output_dir = Path("demo_output")
        output_dir.mkdir(exist_ok=True)
        
        output_filename = f"demo_taxonomy_{metadata.country}_{metadata.grade}_{metadata.subject}_{metadata.isbn}.json"
        output_file = output_dir / output_filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(taxonomy_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Taxonomy saved to: {output_file}")
        
        # Show JSON structure sample
        print("\n📄 Sample JSON structure:")
        print("-" * 30)
        sample_json = {
            "country": taxonomy_data['country'],
            "grade": taxonomy_data['grade'],
            "subject": taxonomy_data['subject'],
            "ISBN": taxonomy_data['ISBN'],
            "taxonomy": taxonomy_data['taxonomy'][:1]  # Show just first item
        }
        print(json.dumps(sample_json, indent=2, ensure_ascii=False))
        
        print()
        print("🎉 Demo completed successfully!")
        print(f"📊 Total topics extracted: {total_topics}")
        print(f"📚 Levels used: 0-{max([item['level'] for item in taxonomy if 'level' in item])}")
        
    except TaxonomyAnalysisError as e:
        print(f"❌ Analysis failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def show_demo_info():
    """Show information about the demo."""
    print("ℹ️  Demo Information")
    print("=" * 30)
    print()
    print("This demo will:")
    print("1. 📚 Show available TOC directories")
    print("2. 🔍 Let you choose one to analyze")
    print("3. 📝 Parse the directory metadata")
    print("4. 🤖 Use GPT-4 Vision to analyze TOC images")
    print("5. 📊 Extract a detailed educational taxonomy")
    print("6. 💾 Save results in JSON format")
    print()
    print("Requirements:")
    print("• OpenAI API key in environment or .env file")
    print("• TOC images in the selected directory")
    print("• Internet connection for GPT-4 API calls")
    print()
    print("Cost estimate: ~$0.01-0.05 per book (depending on image count)")
    print()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demo: Single TOC Taxonomy Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_single_taxonomy.py
  python demo_single_taxonomy.py --tocs-dir custom_tocs/
  python demo_single_taxonomy.py --tocs-dir tocs/ --non-interactive

This demo analyzes a single TOC directory to demonstrate the complete
taxonomy analysis workflow using GPT-4 Vision.
        """
    )
    
    parser.add_argument(
        '--tocs-dir',
        type=str,
        default='tocs',
        help='Input directory containing TOC subdirectories (default: tocs)'
    )
    
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run demo automatically without prompts'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    if not args.non_interactive:
        show_demo_info()
        proceed = input("Proceed with demo? (y/N): ").strip().lower()
        if proceed != 'y':
            print("Demo cancelled.")
            exit()
    
    demo_single_analysis(args.tocs_dir) 