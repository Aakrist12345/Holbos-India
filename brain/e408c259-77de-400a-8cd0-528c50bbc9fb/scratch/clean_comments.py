import os
import re
import tokenize
import io

def remove_comments(source):
    """
    Removes comments and docstrings from Python source code.
    """
    io_obj = io.StringIO(source)
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    
    tokens = tokenize.generate_tokens(io_obj.readline)
    
    for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokens:
        if slineno > last_lineno:
            last_col = 0
        if scol > last_col:
            out += " " * (scol - last_col)
        
        if toktype == tokenize.COMMENT:
            pass
        elif toktype == tokenize.STRING:

            if prev_toktype == tokenize.INDENT or prev_toktype == tokenize.NEWLINE or prev_toktype == tokenize.NL:

                pass
            else:
                out += ttext
        else:
            out += ttext
        
        prev_toktype = toktype
        last_lineno = elineno
        last_col = ecol
        
    return out

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(r'#.*', '', content)

    content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
    content = re.sub(r"'''.*?'''", '', content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

project_root = r"c:\Users\AAKRIST SHARMA\OneDrive\Desktop\HolbosIndia"
apps = ['accounts', 'attendance', 'modules', 'holbos_project']

for app in apps:
    app_path = os.path.join(project_root, app)
    if not os.path.exists(app_path): continue
    for root, dirs, files in os.walk(app_path):
        for file in files:
            if file.endswith('.py'):
                clean_file(os.path.join(root, file))
