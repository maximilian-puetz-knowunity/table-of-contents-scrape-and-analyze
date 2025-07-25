#!/usr/bin/env python3
"""
Test TOC Directory Name Parsing
===============================

This script tests the directory name parsing logic to ensure it correctly
extracts metadata from TOC directory names before running the full analysis.
"""

import os
from pathlib import Path
from toc_taxonomy_analyzer import TocTaxonomyAnalyzer, BookMetadata

def test_directory_parsing():
    """Test the directory name parsing with real TOC directories."""
    
    print("🧪 Testing TOC Directory Name Parsing")
    print("=" * 50)
    print()
    
    # Initialize analyzer (without API key for parsing test)
    try:
        analyzer = TocTaxonomyAnalyzer()
    except Exception:
        # If no API key, create analyzer manually for testing parsing only
        class TestAnalyzer:
            def parse_directory_name(self, dir_name):
                from toc_taxonomy_analyzer import TocTaxonomyAnalyzer
                return TocTaxonomyAnalyzer.parse_directory_name(TocTaxonomyAnalyzer(), dir_name)
            def _normalize_subject(self, subject):
                from toc_taxonomy_analyzer import TocTaxonomyAnalyzer
                return TocTaxonomyAnalyzer._normalize_subject(TocTaxonomyAnalyzer(), subject)
        analyzer = TestAnalyzer()
    
    # Find real TOC directories
    tocs_dir = Path("tocs")
    if not tocs_dir.exists():
        print("❌ TOCs directory not found")
        return
    
    toc_dirs = [d.name for d in tocs_dir.iterdir() if d.is_dir()]
    if not toc_dirs:
        print("❌ No TOC directories found")
        return
    
    print(f"📚 Found {len(toc_dirs)} TOC directories")
    print()
    
    # Test parsing with first 10 directories
    test_dirs = toc_dirs[:10]
    successful = 0
    failed = 0
    
    for i, dir_name in enumerate(test_dirs, 1):
        print(f"🔍 {i:2}. Testing: {dir_name}")
        
        try:
            metadata = analyzer.parse_directory_name(dir_name)
            
            print(f"    ✅ Subject: {metadata.subject}")
            print(f"    ✅ Grade: {metadata.grade}")
            print(f"    ✅ Book: {metadata.book_title}")
            print(f"    ✅ ISBN: {metadata.isbn}")
            print(f"    ✅ Country: {metadata.country}")
            print()
            
            successful += 1
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            print()
            failed += 1
    
    print("📊 Parsing Test Results:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    
    if failed > 0:
        print(f"\n🔧 Consider updating the parsing logic for failed cases")
    else:
        print(f"\n🎉 All test cases passed! Ready for full analysis.")

def test_subject_normalization():
    """Test subject name normalization."""
    
    print("\n🧪 Testing Subject Normalization")
    print("=" * 40)
    
    test_subjects = [
        "Mathematik",
        "Deutsch", 
        "Erdkunde",
        "Geschichte",
        "Französisch",
        "Physik",
        "Mathematik,_Physik",
        "Mathematik,_Physik,_Astronomie,_Chemie,_Biologie,_Informatik"
    ]
    
    try:
        analyzer = TocTaxonomyAnalyzer()
    except Exception:
        class TestAnalyzer:
            def _normalize_subject(self, subject):
                from toc_taxonomy_analyzer import TocTaxonomyAnalyzer
                return TocTaxonomyAnalyzer._normalize_subject(TocTaxonomyAnalyzer(), subject)
        analyzer = TestAnalyzer()
    
    for subject in test_subjects:
        normalized = analyzer._normalize_subject(subject)
        print(f"   {subject:50} → {normalized}")

if __name__ == "__main__":
    test_directory_parsing()
    test_subject_normalization() 