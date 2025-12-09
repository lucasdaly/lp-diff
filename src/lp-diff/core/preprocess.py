import os

def normalized(line: str) -> str:
    return line.lstrip()

def preprocess_files(old_file_path, new_file_path):
    """Read and preprocess two files, returning normalized line lists"""
    old_lines = []
    new_lines = []
    
    try:
        with open(old_file_path, "r", encoding="utf-8") as f_old:
            for line in f_old:
                normalize = normalized(line)
                old_lines.append(normalize)
    except FileNotFoundError:
        print(f"An error occurred. Could not open: {old_file_path}")
        return [], []
    
    try:
        with open(new_file_path, "r", encoding="utf-8") as f_new:
            for line in f_new:
                normalize = normalized(line)
                new_lines.append(normalize)
    except FileNotFoundError:
        print(f"An error occurred. Could not open: {new_file_path}")
        return [], []
    
    return [old_lines, new_lines]

def preprocess():

    # ext functions as actual file extension for path, as well as folder name within test_files
    ext = input("Enter file extension (java, py): ").strip()
    file = input("Enter a file to scan: ").strip()

    new_path = os.path.join(f"test_files\\{ext}", f"{file}_2.{ext}") #this is depended on OS
    old_path = os.path.join(f"test_files\\{ext}", f"{file}_1.{ext}")

    new_lines = []
    old_lines = []
    print(new_path)
    try:
        with open(new_path, "r", encoding="utf-8") as f_new:
            for line in f_new:
                normalize = normalized(line)
                new_lines.append(normalize)
    except FileNotFoundError:
        print(f"An error occured. Could not open: {new_path}")
    
    try:
        with open(old_path, "r", encoding="utf-8") as f_old:
            for line in f_old:
                normalize = normalized(line)
                old_lines.append(normalize)
    except FileNotFoundError:
        print(f"An error occured. Could not open: {old_path}")
    
    #print(new_lines)
    #print("-")
    #print(old_lines)
    lines_merge = [old_lines, new_lines]
    #print(lines_merge)
    return lines_merge
    
if __name__ == "__main__":
    preprocess()
