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
     for i in range(start_index, bound):
          
          combined += new_lines[i]
          score = levenshtein_similarity(old_line, combined)

          # if score goes down, return the last indices and last score
          if score < last_score:
               return list(range(start_index, i)), last_score
          
          last_score = score
     # if it continuous growing until the end, return all the indices and the last score
     return list(range(start_index, i + 1)) ,score


# ok So thats detecting one line --> multiple lines, now this is the other way around
# multiple lines --> one line
def greedy_merge_match(
          
          #new_line: right line we think multiple old lines couldve merged into
          # old_lines: list of old left lines
          # start_index: index in old_lines to start from
          # max_extra lines: maximum number of additional lines to consider

          # returns: 
          
          new_line : str,
          old_lines: list[str],
          start_index:int,
          max_extra_lines: int
          
          ) -> tuple[list[int], float]:








     


# testing
# old_line = "abcdefg"
# new_lines = ["abc", "def", "g", "hij"]
# start_index = 0
# max_extra_lines = 2
# print(greedy_split_match(old_line, new_lines, start_index, max_extra_lines))









