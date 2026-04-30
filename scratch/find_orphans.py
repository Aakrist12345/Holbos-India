import re

def find_css_orphans(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    in_block = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if '{' in stripped:
            in_block = True
        if '}' in stripped:
            in_block = False
        
        # If we see a property (key: value;) but we are not in a block
        if not in_block and re.search(r'^[a-zA-Z-]+\s*:', stripped):
            print(f"Orphan property at line {i+1}: {stripped}")
        
        # If we see a closing brace but we weren't in a block
        if not in_block and stripped == '}':
            # This is hard to detect without full state, but simple for now
            pass

if __name__ == "__main__":
    find_css_orphans(r'c:\Users\AAKRIST SHARMA\OneDrive\Desktop\HolbosIndia\accounts\templates\accounts\parentsdashboard.html')
