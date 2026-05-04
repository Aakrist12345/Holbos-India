import re

def find_css_orphans(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Simple check: lines that start with property: but no { preceding them in the same context
    lines = content.split('\n')
    in_style = False
    in_block = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if '<style>' in stripped: in_style = True
        if '</style>' in stripped: in_style = False
        
        if not in_style: continue
        
        if '{' in stripped: in_block = True
        
        # Check for property like pattern at start of line
        # but only if we think we are outside a block
        if not in_block and re.search(r'^[a-zA-Z-]+\s*:', stripped):
            print(f"{file_path}:{i+1}: Orphan property: {stripped}")
            
        if '}' in stripped: in_block = False

if __name__ == "__main__":
    find_css_orphans(r'c:\Users\AAKRIST SHARMA\OneDrive\Desktop\HolbosIndia\accounts\templates\accounts\parentsdashboard.html')
    find_css_orphans(r'c:\Users\AAKRIST SHARMA\OneDrive\Desktop\HolbosIndia\accounts\templates\accounts\dashboard.html')
