import os
import sys
sys.path.append('.')
from preprocess import preprocess_files
import set_simhash
import candidates
import match
from xml_parser import parse_ground_truth_xml, get_file_pairs

def get_xml_mentioned_lines(ground_truth):
    """Get set of old line numbers that are mentioned in the XML"""
    mentioned_old_lines = set()
    
    # Add lines from matches
    for old_line, new_line in ground_truth['matches']:
        mentioned_old_lines.add(old_line)
    
    # Add deleted lines
    for old_line in ground_truth['deletions']:
        mentioned_old_lines.add(old_line)
    
    return mentioned_old_lines

def filter_results_to_xml_scope(our_matches, our_deletions, mentioned_old_lines):
    """Filter our results to only include lines mentioned in XML"""
    filtered_matches = [(old_idx, new_idx) for old_idx, new_idx in our_matches 
                       if old_idx in mentioned_old_lines]
    
    filtered_deletions = [old_idx for old_idx in our_deletions 
                         if old_idx in mentioned_old_lines]
    
    return filtered_matches, filtered_deletions

def read_file_lines(filepath):
    """Read file and return list of lines"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()

def run_single_test(old_file, new_file, xml_file, test_name):
    """Run lp-diff on a single file pair and compare to ground truth"""
    print(f"\n=== Testing {test_name} ===")
    
    # Parse ground truth
    ground_truth = parse_ground_truth_xml(xml_file)
    
    # Run your algorithm
    lines_result = preprocess_files(old_file, new_file)
    old_lines = lines_result[0]
    new_lines = lines_result[1]
    
    print(f"Old file: {len(old_lines)} lines, New file: {len(new_lines)} lines")
    
    simhashlist = set_simhash.set_simhash(old_lines, new_lines)
    can = candidates.createCandidates2(simhashlist[0], simhashlist[1])
    final_matches, split_matches, merge_matches, unmatched_old, unmatched_new = match.compare(old_lines, new_lines, can, threshold=0.5, split_threshold=0.4)
    
    # Convert results to comparable format (1-indexed to match XML)
    our_matches = [(old_idx + 1, new_idx + 1) for old_idx, new_idx, score in final_matches]
    
    # Handle split matches - convert N:M splits to individual matches
    for old_idx, split_indices, score in split_matches:
        for new_idx in split_indices:
            our_matches.append((old_idx + 1, new_idx + 1))
    
    # Handle merge matches - convert M:N merges to individual matches  
    for merge_indices, new_idx, score in merge_matches:
        for old_idx in merge_indices:
            our_matches.append((old_idx + 1, new_idx + 1))
    
    our_deletions = [idx + 1 for idx in unmatched_old]  # Convert to 1-indexed
    our_additions = [idx + 1 for idx in unmatched_new]  # Convert to 1-indexed
    
    # Get only the lines that XML cares about
    mentioned_old_lines = get_xml_mentioned_lines(ground_truth)
    print(f"XML mentions {len(mentioned_old_lines)} old lines out of {len(old_lines)} total")
    
    # Filter our results to only lines mentioned in XML
    filtered_matches, filtered_deletions = filter_results_to_xml_scope(
        our_matches, our_deletions, mentioned_old_lines)
    
    print(f"Filtered results: {len(filtered_matches)} matches ({len(final_matches)} regular + {len(split_matches)} split + {len(merge_matches)} merge), {len(filtered_deletions)} deletions")
    
    # Calculate actual additions from ground truth
    gt_additions = []
    for i in range(1, len(new_lines) + 1):
        if i not in ground_truth['used_new_lines']:
            gt_additions.append(i)
    ground_truth['additions'] = gt_additions
    
    # Compare results using only XML-scope
    results = compare_results(
        ground_truth['matches'], filtered_matches,
        ground_truth['deletions'], filtered_deletions,
        ground_truth['additions'], our_additions,  # Keep all additions for now
        test_name
    )
    
    return results

def compare_results(gt_matches, our_matches, gt_deletions, our_deletions, gt_additions, our_additions, test_name):
    """Compare ground truth vs our results (now scoped to XML-mentioned lines)"""
    
    print(f"Ground truth scope: {len(gt_matches)} matches, {len(gt_deletions)} deletions")
    print(f"Our results scope:  {len(our_matches)} matches, {len(our_deletions)} deletions")
    
    # Calculate precision, recall for matches
    gt_match_set = set(gt_matches)
    our_match_set = set(our_matches)
    
    true_positives = len(gt_match_set.intersection(our_match_set))
    false_positives = len(our_match_set - gt_match_set)
    false_negatives = len(gt_match_set - our_match_set)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Show some examples of mismatches for debugging
    if false_positives > 0:
        print(f"False positives (our extra matches): {list(our_match_set - gt_match_set)[:5]}")
    if false_negatives > 0:
        print(f"False negatives (missed matches): {list(gt_match_set - our_match_set)[:5]}")
    
    return {
        'test_name': test_name,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives
    }

def run_full_validation():
    """Run validation on all test file pairs"""
    file_pairs = get_file_pairs()
    all_results = []
    
    print(f"Found {len(file_pairs)} test file pairs...")
    
    for old_file, new_file, xml_file, test_name in file_pairs:
        try:
            result = run_single_test(old_file, new_file, xml_file, test_name)
            all_results.append(result)
            
            print(f"{test_name}: P={result['precision']:.3f}, R={result['recall']:.3f}, F1={result['f1_score']:.3f}")
            
        except Exception as e:
            print(f"Error testing {test_name}: {e}")
            import traceback
            traceback.print_exc()
    
    if all_results:
        # Calculate overall statistics
        avg_precision = sum(r['precision'] for r in all_results) / len(all_results)
        avg_recall = sum(r['recall'] for r in all_results) / len(all_results)
        avg_f1 = sum(r['f1_score'] for r in all_results) / len(all_results)
        
        print(f"\n=== OVERALL RESULTS ({len(all_results)} tests) ===")
        print(f"Average Precision: {avg_precision:.3f}")
        print(f"Average Recall: {avg_recall:.3f}")
        print(f"Average F1-Score: {avg_f1:.3f}")
    
    return all_results