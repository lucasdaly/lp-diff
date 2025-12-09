from similarity import combinedscore
import split

def getcontext(lines, index, context_size=3):
    start = max(0, index-context_size)
    end = min(len(lines),index+context_size+1)
    return " ".join(lines[start:end])

def compare(old_lines,new_lines,candidate_sets,threshold=0.7, split_threshold=0.8):
    final_matches = []
    split_matches = []
    unmatched_old = []
    unmatched_new = []
    matched_old_lines = set()
    used_new_lines = set()

    for i, candidates in enumerate(candidate_sets):
        if not candidates:
            split_indices, split_score = checkforsplit(old_lines[i], new_lines, used_new_lines, 3)
            if split_score >= split_threshold:
                split_matches.append((i, split_indices, split_score))
                used_new_lines.update(split_indices)
                matched_old_lines.add(i)
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

            if score > best_score and score >= threshold:
                best_score=score
                best_match=new_idx
        
        if best_match!=-1:
            final_matches.append((i, best_match, best_score))
            used_new_lines.add(best_match)
            matched_old_lines.add(i)
        else:
            split_indices, split_score = checkforsplit(old_lines[i], new_lines, used_new_lines, 3)
            if split_score >= split_threshold:
                split_matches.append((i, split_indices, split_score))
                used_new_lines.update(split_indices)
                matched_old_lines.add(i)
            else:
                unmatched_old.append(i)
    
    # Find unmatched new lines
    for j in range(len(new_lines)):
        if j not in used_new_lines:
            unmatched_new.append(j)
    
    return final_matches, split_matches, unmatched_old, unmatched_new

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
