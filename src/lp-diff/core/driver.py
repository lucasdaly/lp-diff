
from simhash import Simhash, SimhashIndex
import preprocess
import set_simhash
import candidates
import match

lists = preprocess.preprocess()
simhashlist = set_simhash.set_simhash(lists[0],lists[1])
can = candidates.createCandidates2(simhashlist[0],simhashlist[1])
finalmatches, splitmatches, mergematches, unmatched_old, unmatched_new = match.compare(lists[0], lists[1], can, threshold=0.5, split_threshold=0.4)
print("=== REGULAR MATCHES ===")
for old_idx, new_idx, score in finalmatches:
    print(f"Old line {old_idx+1} ↔ New line {new_idx+1} (score: {score:.3f})")
    print(f"  Old: {repr(lists[0][old_idx])}")
    print(f"  New: {repr(lists[1][new_idx])}")

print("\n=== SPLIT MATCHES ===")
for old_idx, split_indices, score in splitmatches:
    print(f"Old line {old_idx+1} split into lines {[i+1 for i in split_indices]} (score: {score:.3f})")
    print(f"  Old: {repr(lists[0][old_idx])}")
    print(f"  Split into:")
    for idx in split_indices:
        print(f"    Line {idx+1}: {repr(lists[1][idx])}")

print("\n=== MERGE MATCHES ===")
for merge_indices, new_idx, score in mergematches:
    print(f"Old lines {[i+1 for i in merge_indices]} merged into line {new_idx+1} (score: {score:.3f})")
    print(f"  Merged from:")
    for idx in merge_indices:
        print(f"    Line {idx+1}: {repr(lists[0][idx])}")
    print(f"  Into: {repr(lists[1][new_idx])}")

print("\n=== UNMATCHED OLD LINES (DELETED) ===")
for old_idx in unmatched_old:
    print(f"- Old line {old_idx+1}: {repr(lists[0][old_idx])}")

print("\n=== UNMATCHED NEW LINES (ADDED) ===")
for new_idx in unmatched_new:
    print(f"+ New line {new_idx+1}: {repr(lists[1][new_idx])}")

# Summary statistics
print(f"\n=== SUMMARY ===")
print(f"Regular matches: {len(finalmatches)}")
print(f"Split matches: {len(splitmatches)}")
print(f"Deleted lines: {len(unmatched_old)}")
print(f"Added lines: {len(unmatched_new)}")