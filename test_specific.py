import os
import sys
sys.path.append('./src/lp-diff/core')

def run_single_test_with_merge(old_file, new_file, xml_file, test_name):
    """Run lp-diff on a single file pair including merge detection"""
    from preprocess import preprocess_files
    import set_simhash
    import candidates
    import match
    from xml_parser import parse_ground_truth_xml
    
    print(f"\n=== Testing {test_name} (with merge detection) ===")
    
    # Parse ground truth
    ground_truth = parse_ground_truth_xml(xml_file)
    
    # Run your algorithm
    lines_result = preprocess_files(old_file, new_file)
    old_lines = lines_result[0]
    new_lines = lines_result[1]
    
    simhashlist = set_simhash.set_simhash(old_lines, new_lines)
    can = candidates.createCandidates2(simhashlist[0], simhashlist[1])
    final_matches, split_matches, merge_matches, unmatched_old, unmatched_new = match.compare(old_lines, new_lines, can, threshold=0.5)
    
    print(f"Results: {len(final_matches)} regular, {len(split_matches)} splits, {len(merge_matches)} merges")
    
    # Show merge matches for DoubleCache
    if test_name == "DoubleCache" and merge_matches:
        print("\nMERGE MATCHES FOUND:")
        for merge_indices, new_idx, score in merge_matches:
            print(f"  Old lines {[i+1 for i in merge_indices]} -> New line {new_idx+1} (score: {score:.3f})")

def test_specific_files():
    """Test specific files to see improvement with merge detection"""
    test_cases = [
        "DoubleCache",     # Was failing - should improve with merge detection!
        "BaseTypes",       # Was working  
        "JavaPerspectiveFactory",  # Was failing
        "asdf"             # Was working
    ]
    
    print("Testing specific cases after adding merge detection...")
    results = []
    
    for test_name in test_cases:
        try:
            old_file = f"test_files/java/{test_name}_1.java"
            new_file = f"test_files/java/{test_name}_2.java" 
            xml_file = f"xmls/{test_name}.xml"
            
            result = run_single_test_with_merge(old_file, new_file, xml_file, test_name)
            results.append((test_name, result))
            
        except Exception as e:
            print(f"Error testing {test_name}: {e}")
    
    return results

def run_single_test_with_merge(old_file, new_file, xml_file, test_name):
    """Run lp-diff on a single file pair including merge detection"""
    from preprocess import preprocess_files
    import set_simhash
    import candidates
    import match
    from xml_parser import parse_ground_truth_xml
    
    print(f"\n=== Testing {test_name} (with merge detection) ===")
    
    # Parse ground truth
    ground_truth = parse_ground_truth_xml(xml_file)
    
    # Run your algorithm
    lines_result = preprocess_files(old_file, new_file)
    old_lines = lines_result[0]
    new_lines = lines_result[1]
    
    simhashlist = set_simhash.set_simhash(old_lines, new_lines)
    can = candidates.createCandidates2(simhashlist[0], simhashlist[1])
    final_matches, split_matches, merge_matches, unmatched_old, unmatched_new = match.compare(old_lines, new_lines, can, threshold=0.5)
    
    print(f"Results: {len(final_matches)} regular, {len(split_matches)} splits, {len(merge_matches)} merges")
    
    # Show merge matches for DoubleCache
    if test_name == "DoubleCache" and merge_matches:
        print("\nMERGE MATCHES FOUND:")
        for merge_indices, new_idx, score in merge_matches:
            print(f"  Old lines {[i+1 for i in merge_indices]} -> New line {new_idx+1} (score: {score:.3f})")
    
    return {"test_name": test_name}

if __name__ == "__main__":
    test_specific_files()