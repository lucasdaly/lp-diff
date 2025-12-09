import xml.etree.ElementTree as ET
import os

def parse_ground_truth_xml(xml_file):
    """
    Parse XML ground truth file and extract line mappings
    Returns dict with 'matches', 'deletions', 'additions'
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # For now, let's use VERSION 2 (the more complex one)
    version2 = root.find(".//VERSION[@NUMBER='2']")
    if version2 is None:
        # Fall back to VERSION 1 if VERSION 2 doesn't exist
        version2 = root.find(".//VERSION[@NUMBER='1']")
    
    matches = []
    deletions = []
    additions = []  # We'll need to infer these
    
    # Track which new line numbers are used
    used_new_lines = set()
    
    for location in version2.findall('LOCATION'):
        orig = int(location.get('ORIG'))
        new = location.get('NEW')
        
        if new == "-1":
            # Line was deleted
            deletions.append(orig)
        else:
            # Line was matched/moved
            new_num = int(new)
            matches.append((orig, new_num))
            used_new_lines.add(new_num)
    
    # For additions, we'd need to know the total number of lines in the new file
    # For now, we'll leave additions empty and calculate them in validation
    
    return {
        'matches': matches,
        'deletions': deletions,
        'additions': additions,
        'used_new_lines': used_new_lines
    }

def get_file_pairs():
    """Get all corresponding file pairs from test_files"""
    # Get the root directory of the project
    current_dir = os.getcwd()
    
    # If we're in the core directory, go up 3 levels, otherwise assume we're at root
    if current_dir.endswith('core'):
        base_path = "../../../test_files/java"
        xml_path = "../../../xmls"
    else:
        base_path = "test_files/java"
        xml_path = "xmls"
    
    file_pairs = []
    
    # Check if paths exist
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"XML path not found: {xml_path}. Current dir: {current_dir}")
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Test files path not found: {base_path}. Current dir: {current_dir}")
    
    # Find all XML files and their corresponding java files
    for xml_filename in os.listdir(xml_path):
        if xml_filename.endswith('.xml'):
            base_name = xml_filename[:-4]  # Remove '.xml'
            
            # Skip test1 as it doesn't follow the pattern
            if base_name == 'test1':
                continue
                
            old_file = os.path.join(base_path, f"{base_name}_1.java")
            new_file = os.path.join(base_path, f"{base_name}_2.java")
            xml_file = os.path.join(xml_path, xml_filename)
            
            if os.path.exists(old_file) and os.path.exists(new_file):
                file_pairs.append((old_file, new_file, xml_file, base_name))
    
    return file_pairs