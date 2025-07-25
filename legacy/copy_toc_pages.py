#!/usr/bin/env python3
"""
Copy TOC Pages to Organized Structure
=====================================

This script copies all table of contents screenshots from the 
screenshots/{isbn}/toc_pages/ directories into a new organized
structure: tocs/toc_{isbn}/

Usage: python copy_toc_pages.py
"""

import os
import shutil
from pathlib import Path

def copy_toc_pages():
    """Copy all TOC pages to organized tocs/ directory structure."""
    
    screenshots_dir = Path("screenshots")
    tocs_dir = Path("tocs")
    
    # Create base tocs directory
    tocs_dir.mkdir(exist_ok=True)
    
    # Track statistics
    total_books = 0
    total_files_copied = 0
    books_with_toc = 0
    
    print("📚 Copying TOC Screenshots to Organized Structure")
    print("=" * 60)
    print()
    
    # Find all ISBN directories
    isbn_dirs = [d for d in screenshots_dir.iterdir() if d.is_dir()]
    isbn_dirs.sort(key=lambda x: x.name)
    
    for isbn_dir in isbn_dirs:
        isbn_name = isbn_dir.name
        toc_pages_dir = isbn_dir / "toc_pages"
        
        total_books += 1
        
        # Check if toc_pages directory exists and has files
        if not toc_pages_dir.exists():
            print(f"⚠️  {isbn_name}: No toc_pages directory")
            continue
        
        # Find all PNG files in toc_pages
        toc_files = list(toc_pages_dir.glob("*.png"))
        
        if not toc_files:
            print(f"📖 {isbn_name}: No TOC pages found")
            continue
        
        books_with_toc += 1
        
        # Create target directory
        target_dir = tocs_dir / f"toc_{isbn_name}"
        target_dir.mkdir(exist_ok=True)
        
        print(f"📚 {isbn_name}")
        print(f"   📄 Found {len(toc_files)} TOC pages")
        
        # Copy each file
        files_copied = 0
        for toc_file in toc_files:
            target_file = target_dir / toc_file.name
            
            try:
                shutil.copy2(toc_file, target_file)
                files_copied += 1
                total_files_copied += 1
                print(f"   ✅ {toc_file.name}")
                
            except Exception as e:
                print(f"   ❌ Failed to copy {toc_file.name}: {e}")
        
        print(f"   📁 Saved to: {target_dir}")
        print()
    
    # Display summary
    print("📊 Copy Summary:")
    print("-" * 40)
    print(f"📚 Total books processed: {total_books}")
    print(f"✅ Books with TOC pages: {books_with_toc}")
    print(f"📄 Total files copied: {total_files_copied}")
    print(f"📁 Output directory: {tocs_dir.absolute()}")
    
    # Show directory structure sample
    if total_files_copied > 0:
        print(f"\n📂 Directory structure created:")
        print("-" * 40)
        
        # Show first few directories as examples
        example_dirs = list(tocs_dir.glob("toc_*"))[:3]
        for example_dir in example_dirs:
            print(f"📁 {example_dir.name}/")
            example_files = list(example_dir.glob("*.png"))[:2]
            for example_file in example_files:
                print(f"   📄 {example_file.name}")
            if len(list(example_dir.glob("*.png"))) > 2:
                remaining = len(list(example_dir.glob("*.png"))) - 2
                print(f"   ... and {remaining} more files")
        
        if len(example_dirs) < books_with_toc:
            remaining_dirs = books_with_toc - len(example_dirs)
            print(f"... and {remaining_dirs} more directories")


if __name__ == "__main__":
    try:
        copy_toc_pages()
        print("\n🎉 TOC pages copied successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1) 