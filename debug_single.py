import os
import sys
sys.path.append('./src/lp-diff/core')

from validation import run_single_test
from xml_parser import parse_ground_truth_xml

def test_single_file(test_name):
    """Test a single file pair for debugging"""
    old_file = f"test_files/java/{test_name}_1.java"
    new_file = f"test_files/java/{test_name}_2.java"
    xml_file = f"xmls/{test_name}.xml"
    
    print(f"Testing {test_name}...")
    
    # Import required modules
    sys.path.append('./src/lp-diff/core')
    from preprocess import preprocess_files
    import set_simhash
    import candidates
    from xml_parser import parse_ground_truth_xml
    
    # Show what's in the XML first
    ground_truth = parse_ground_truth_xml(xml_file)
    print(f"\nXML Ground Truth:")
    print(f"  Matches: {ground_truth['matches']}")
    print(f"  Deletions: {ground_truth['deletions']}")
    
    # Load files
    lines_result = preprocess_files(old_file, new_file)
    old_lines = lines_result[0]
    new_lines = lines_result[1]
    
    print(f"\nFile sizes: {len(old_lines)} old, {len(new_lines)} new")
    
    # Check specific XML-mentioned lines
    print(f"\nChecking XML-mentioned lines:")
    for old_line_num, new_line_num in ground_truth['matches'][:5]:  # First 5 matches
        old_idx = old_line_num - 1
        new_idx = new_line_num - 1
        if old_idx < len(old_lines) and new_idx < len(new_lines):
            print(f"  {old_line_num} -> {new_line_num}:")
            print(f"    Old: {repr(old_lines[old_idx][:60])}")
            print(f"    New: {repr(new_lines[new_idx][:60])}")
            
    # Generate candidates and check if XML matches are in candidates
    simhashlist = set_simhash.set_simhash(old_lines, new_lines)
    can = candidates.createCandidates2(simhashlist[0], simhashlist[1])
    
    print(f"\nCandidate analysis for XML matches:")
    missing_candidates = 0
    for old_line_num, new_line_num in ground_truth['matches'][:5]:
        old_idx = old_line_num - 1
        if old_idx < len(can):
            candidates_list = can[old_idx]
            if new_line_num in candidates_list:
                print(f"  OK Line {old_line_num} -> {new_line_num} IS in candidates: {candidates_list}")
            else:
                print(f"  XX Line {old_line_num} -> {new_line_num} MISSING from candidates: {candidates_list}")
                missing_candidates += 1
    
    print(f"\nMissing candidates: {missing_candidates}/{min(5, len(ground_truth['matches']))}")

if __name__ == "__main__":
    # Test one of the failing cases
    print("=== TESTING FAILING CASE ===")
    test_single_file("DoubleCache")
    
    print("\n" + "="*50)
    print("=== TESTING SUCCESS CASE ===")
    test_single_file("BaseTypes")