from similarity import levenshtein_similarity

# Check to see if old_line was split into multiple lines in new_lines
# Levenshtein similarity of the actual CONTENT of the lines,
def greedy_split_match(
          

        old_line: str,
        new_lines: list[str],
        start_index: int,
        max_extra_lines: int

        # old_line : old (left) line. We are checking to see if it was split
        # new_lines : lines we are checking to see if old_line was split into
        # start_index : index in new_lines to start checking from
        # max_extra_lines : maximum number of extra lines in the new file to consider for a split


        # return type: tuple
            # list of INDICES** in new_lines that correspond to the split of old_line (if any, returns [] if no split detected)
            # and then the similarity score (float between 0 and 1)
                 ) -> tuple[list[int], float]:
     
     # make sure start_index is in range
     if start_index <0 or start_index >= len(new_lines):
         return [], 0.0
     
     # empty content string to keep adding new lines to
     combined = ""

     # variable to compare current score vs last one (for greedy)
     last_score = 0.0
     
     # if the max number of extra lines goes beyond the length of new_lines, make it the length of new_lines
     bound = min(len(new_lines), start_index + max_extra_lines + 1)

     # if bound is for some reason less than or equal to start_index (incorrect input), return no split
     if bound <= start_index:
         return [], 0.0

     # iterate through new_lines, adding the new lines one by one and checking the similarity score (greedy)
     content_indices = []  # Track which indices have actual content
     for i in range(start_index, bound):
          
          # Only include lines with actual content (ignore empty/whitespace-only lines)
          if new_lines[i].strip():
               combined += new_lines[i]
               content_indices.append(i)
               score = levenshtein_similarity(old_line, combined)

               # if score goes down, return the last content indices and last score
               if score < last_score:
                    remaining_indices = content_indices[:-1]
                    # Only return if we have at least 2 lines
                    if len(remaining_indices) >= 2:
                         return remaining_indices, last_score
                    else:
                         return [], 0.0
               
               last_score = score

     # Only return a split if we have at least 2 lines with actual content  
     if len(content_indices) < 2:
          return [], 0.0
          
     # if it continuous growing until the end, return all content indices and the last score
     return content_indices, score

# testing
# old_line = "abcdefg"
# new_lines = ["abc", "def", "g", "hij"]
# start_index = 0
# max_extra_lines = 2
# print(greedy_split_match(old_line, new_lines, start_index, max_extra_lines))

def greedy_merge_match(
        old_lines: list[str],
        new_line: str,
        start_index: int,
        max_extra_lines: int
        # old_lines : lines we are checking to see if they merged into new_line
        # new_line : new (right) line. We are checking to see if multiple old lines merged into it
        # start_index : index in old_lines to start checking from
        # max_extra_lines : maximum number of extra lines in the old file to consider for a merge

        # return type: tuple
            # list of INDICES in old_lines that correspond to the merge into new_line (if any, returns [] if no merge detected)
            # and then the similarity score (float between 0 and 1)
                 ) -> tuple[list[int], float]:
     
     # make sure start_index is in range
     if start_index < 0 or start_index >= len(old_lines):
         return [], 0.0
     
     # empty content string to keep adding old lines to
     combined = ""

     # variable to compare current score vs last one (for greedy)
     last_score = 0.0
     
     # if the max number of extra lines goes beyond the length of old_lines, make it the length of old_lines
     bound = min(len(old_lines), start_index + max_extra_lines + 1)

     # if bound is for some reason less than or equal to start_index (incorrect input), return no merge
     if bound <= start_index:
         return [], 0.0

     # iterate through old_lines, adding the old lines one by one and checking the similarity score (greedy)
     content_indices = []  # Track which indices have actual content
     for i in range(start_index, bound):
          
          # Only include lines with actual content (ignore empty/whitespace-only lines)
          if old_lines[i].strip():  
               combined += old_lines[i]
               content_indices.append(i)
               score = levenshtein_similarity(combined, new_line)

               # if score goes down, return the last content indices and last score
               if score < last_score:
                    remaining_indices = content_indices[:-1]
                    # Only return if we have at least 2 lines
                    if len(remaining_indices) >= 2:
                         return remaining_indices, last_score
                    else:
                         return [], 0.0
               
               last_score = score
     
     # Only return a merge if we have at least 2 lines with actual content
     if len(content_indices) < 2:
          return [], 0.0
          
     # if it continues growing until the end, return all content indices and the last score
     return content_indices, score









