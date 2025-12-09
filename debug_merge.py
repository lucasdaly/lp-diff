import sys
sys.path.append("src/lp-diff/core")
import split

# Test the specific lines that should merge
old_lines = [
    'System.arraycopy(\n',
    'keyTable,\n', 
    '0,\n',
    '(keyTable = new double[elementSize * 2]),\n',
    '0,\n',
    'elementSize);\n'
]

new_line = 'System.arraycopy(keyTable, 0, (keyTable = new double[elementSize * 2]), 0, elementSize);\n'

print("Testing merge detection:")
print(f"Old lines: {old_lines}")
print(f"New line: {new_line}")
print()

# Test the greedy_merge_match function
merge_indices, score = split.greedy_merge_match(old_lines, new_line, 0, 6)
print(f"Result: merge_indices={merge_indices}, score={score}")
print(f"Threshold check (score >= 0.75): {score >= 0.75}")