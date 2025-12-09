from similarity import combinedscore
import split

def getcontext(lines, index, context_size=3):
    start = max(0, index-context_size)
    end = min(len(lines),index+context_size+1)
    return " ".join(lines[start:end])

def compare(old_lines,new_lines,candidate_sets,threshold=0.5, split_threshold=0.4):
    final_matches = []
    split_matches = []
    merge_matches = []  # New: track merge matches
    unmatched_old = []
    unmatched_new = []
    matched_old_lines = set()
    used_new_lines = set()
    used_old_lines = set()  # Track used old lines for merge detection

    # PHASE 1: Check for merges FIRST (before regular matches consume lines)
    print("DEBUG: Starting merge detection phase...")
    # Use higher threshold for merges to be more conservative
    merge_threshold = max(0.85, split_threshold + 0.1)
    
    for j in range(len(new_lines)):
        # Always use full search for merge detection to catch lines missed by simhash
        merge_indices, merge_score = checkformerge(old_lines, new_lines[j], used_old_lines, 10)
            
        if merge_score >= merge_threshold and merge_indices and len(merge_indices) > 1:
            # Additional check: don't merge if individual lines would match well as regular matches
            should_merge = True
            if len(merge_indices) == 2:  # For 2-line merges, check if both could match individually
                for old_idx in merge_indices:
                    if old_idx < len(candidate_sets) and candidate_sets[old_idx]:
                        # Check if this old line has good individual candidates
                        for new_line_num in candidate_sets[old_idx]:
                            candidate_idx = new_line_num - 1
                            if candidate_idx not in used_new_lines:
                                oldcontext = getcontext(old_lines, old_idx)
                                newcontext = getcontext(new_lines, candidate_idx)
                                individual_score = combinedscore(old_lines[old_idx], new_lines[candidate_idx], oldcontext, newcontext)
                                # If individual match would be strong, prefer it over merge
                                if individual_score >= 0.8:
                                    should_merge = False
                                    print(f"DEBUG: Preferring individual match over merge: line {old_idx+1} -> {candidate_idx+1} (score: {individual_score:.3f})")
                                    break
                        if not should_merge:
                            break
            
            if should_merge:
                print(f"DEBUG: Merge detected: lines {[i+1 for i in merge_indices]} -> line {j+1} (score: {merge_score:.3f})")
                if not isinstance(merge_indices, list):
                    print(f"Error: merge_indices is {type(merge_indices)}, value: {merge_indices}")
                    continue
                merge_matches.append((merge_indices, j, merge_score))
                used_old_lines.update(merge_indices)
                matched_old_lines.update(merge_indices)
                used_new_lines.add(j)
            else:
                print(f"DEBUG: Merge rejected (preferring individual matches): lines {[i+1 for i in merge_indices]} -> line {j+1} (merge score: {merge_score:.3f})")
        elif merge_indices and len(merge_indices) > 1:
            print(f"DEBUG: Merge rejected (score too low): lines {[i+1 for i in merge_indices]} -> line {j+1} (score: {merge_score:.3f}, threshold: {merge_threshold:.3f})")
        elif merge_indices and len(merge_indices) <= 1:
            print(f"DEBUG: Single-line merge rejected: line {[i+1 for i in merge_indices]} -> line {j+1}")
        elif not merge_indices:
            if j in [101, 102]:  # Only debug lines 102,103
                print(f"DEBUG: No merge found for line {j+1}")
            pass

    print(f"DEBUG: Merge phase complete. Found {len(merge_matches)} merges. Used old lines: {sorted(used_old_lines)}")

    # PHASE 2: Regular matches (excluding lines already used in merges)
    print("DEBUG: Starting regular matching phase...")
    for i, candidates in enumerate(candidate_sets):
        if i in used_old_lines:  # Skip if this old line was already used in a merge
            continue
            
        if not candidates:
            split_indices, split_score = checkforsplit(old_lines[i], new_lines, used_new_lines, 10)
            if split_score >= split_threshold:
                split_matches.append((i, split_indices, split_score))
                used_new_lines.update(split_indices)
                matched_old_lines.add(i)
                used_old_lines.add(i)
            else:
                unmatched_old.append(i)
            continue
    
        best_score = 0
        best_match = -1

        for new_line_num in candidates:
            new_idx = new_line_num-1
        
            if new_idx in used_new_lines:
                continue

            oldcontext = getcontext(old_lines, i)
            newcontext = getcontext(new_lines, new_idx)

            score = combinedscore(old_lines[i], new_lines[new_idx], oldcontext, newcontext)
            
            # Debug output for failing cases
            if score > 0.1:  # Only show promising scores
                print(f"  Old {i+1} vs New {new_idx+1}: score = {score:.3f}")

            if score > best_score and score >= threshold:
                best_score=score
                best_match=new_idx
        
        if best_match!=-1:
            final_matches.append((i, best_match, best_score))
            used_new_lines.add(best_match)
            matched_old_lines.add(i)
            used_old_lines.add(i)
        else:
            split_indices, split_score = checkforsplit(old_lines[i], new_lines, used_new_lines, 10)
            if split_score >= split_threshold:
                split_matches.append((i, split_indices, split_score))
                used_new_lines.update(split_indices)
                matched_old_lines.add(i)
                used_old_lines.add(i)
            else:
                unmatched_old.append(i)
    
    # Find unmatched old lines (excluding those used in merges)
    unmatched_old = [i for i in range(len(old_lines)) if i not in matched_old_lines]
    
    # Find unmatched new lines
    for j in range(len(new_lines)):
        if j not in used_new_lines:
            unmatched_new.append(j)
    
    return final_matches, split_matches, merge_matches, unmatched_old, unmatched_new

def checkforsplit(old_line, new_lines, used_new_lines, max_extra_lines=3):
    best_split = []
    best_score = 0.0

    for start_idx in range(len(new_lines)):
        if start_idx in used_new_lines:
            continue
    
        split_indices, score = split.greedy_split_match(old_line,new_lines,start_idx,max_extra_lines)

        if any(idx in used_new_lines for idx in split_indices):
            continue
        
        if score>best_score:
            best_score=score
            best_split =split_indices
    
    return best_split, best_score

def checkformerge_with_candidates(old_lines, new_line, candidate_indices, max_extra_lines=3):
    """Check if multiple old lines from candidates merged into one new line"""
    if not candidate_indices:
        return [], 0.0
        
    best_merge = []
    best_score = 0.0

    # Try all possible starting points within candidates
    for start_idx in candidate_indices:
        # Find consecutive sequences starting from this candidate
        merge_result = split.greedy_merge_match(old_lines, new_line, start_idx, max_extra_lines)
        
        if isinstance(merge_result, tuple) and len(merge_result) == 2:
            merge_indices, score = merge_result
            if isinstance(merge_indices, list) and score > best_score:
                best_score = score
                best_merge = merge_indices
    
    return best_merge, best_score

def checkformerge(old_lines, new_line, used_old_lines, max_extra_lines=3):
    """Check if multiple old lines merged into one new line"""
    best_merge = []
    best_score = 0.0

    for start_idx in range(len(old_lines)):
        if start_idx in used_old_lines:
            continue
    
        merge_indices, score = split.greedy_merge_match(old_lines, new_line, start_idx, max_extra_lines)

        if any(idx in used_old_lines for idx in merge_indices):
            continue
        
        if score > best_score:
            best_score = score
            best_merge = merge_indices
    
    return best_merge, best_score
