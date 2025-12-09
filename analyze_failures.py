import os
import sys
sys.path.append('./src/lp-diff/core')

from xml_parser import parse_ground_truth_xml
from preprocess import preprocess_files

def analyze_failing_cases():
    """Analyze the worst performing test cases to understand the patterns"""
    
    failing_tests = [
        "DoubleCache",           # F1 ≈ 0.1
        "SaveManager",           # F1 = 0.0
        "TabFolder",            # F1 = 0.0
        "PluginSearchScope",    # F1 = 0.0
        "ResourceInfo"          # F1 ≈ 0.3
    ]
    
    for test_name in failing_tests:
        print(f"\n{'='*60}")
        print(f"ANALYZING: {test_name}")
        print('='*60)
        
        try:
            # Load files and XML
            old_file = f"test_files/java/{test_name}_1.java"
            new_file = f"test_files/java/{test_name}_2.java"
            xml_file = f"xmls/{test_name}.xml"
            
            ground_truth = parse_ground_truth_xml(xml_file)
            lines_result = preprocess_files(old_file, new_file)
            old_lines = lines_result[0]
            new_lines = lines_result[1]
            
            print(f"File sizes: {len(old_lines)} old lines, {len(new_lines)} new lines")
            print(f"XML scope: {len(ground_truth['matches'])} matches, {len(ground_truth['deletions'])} deletions")
            
            # Analyze the first few XML matches to see what's expected
            print(f"\nFirst 3 expected matches:")
            for i, (old_line_num, new_line_num) in enumerate(ground_truth['matches'][:3]):
                old_idx = old_line_num - 1
                new_idx = new_line_num - 1
                
                if old_idx < len(old_lines) and new_idx < len(new_lines):
                    old_content = old_lines[old_idx].strip()[:80]
                    new_content = new_lines[new_idx].strip()[:80]
                    
                    print(f"  {old_line_num} -> {new_line_num}:")
                    print(f"    Old: '{old_content}'")
                    print(f"    New: '{new_content}'")
                    
                    # Quick similarity check
                    if old_content == new_content:
                        print(f"    Status: IDENTICAL")
                    elif old_content in new_content or new_content in old_content:
                        print(f"    Status: SUBSTRING MATCH")
                    else:
                        print(f"    Status: DIFFERENT - may be refactored/moved")
            
            # Check deleted lines
            if ground_truth['deletions']:
                print(f"\nFirst 3 expected deletions:")
                for i, old_line_num in enumerate(ground_truth['deletions'][:3]):
                    old_idx = old_line_num - 1
                    if old_idx < len(old_lines):
                        old_content = old_lines[old_idx].strip()[:80]
                        print(f"  Line {old_line_num}: '{old_content}'")
            
            # Analyze the pattern - are these major refactoring cases?
            match_ratio = len(ground_truth['matches']) / len(old_lines)
            print(f"\nMatch ratio: {match_ratio:.3f} ({len(ground_truth['matches'])}/{len(old_lines)})")
            
            if match_ratio < 0.1:
                print("❌ MAJOR REFACTORING: Most lines changed - very few unchanged lines")
            elif match_ratio < 0.3:
                print("⚠️  SIGNIFICANT CHANGES: Many lines modified")
            else:
                print("✅ MODERATE CHANGES: Should be trackable")
                
        except Exception as e:
            print(f"Error analyzing {test_name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    analyze_failing_cases()