import os
import re

def clean_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        stripped = line.strip()

        if re.match(r'^#\s*[═─=]{3,}.*', stripped): continue
        if re.match(r'^/\*\s*[═─=-]{3,}.*\*\/', stripped): continue
        if re.match(r'^<!--\s*[═─=-]{3,}.*-->', stripped): continue

        ai_phrases = [
            'Refined dashboard:',
            'Pre-calculate counts',
            'Get current month metadata',
            'attendance map for THIS month',
            'weekly history (last 5 records)',
            'specific absent dates',
            'Global stats',
            'Calculate per-child stats',
            'Fill comp section details',
            'Our JS expects',
            'Handle autologin',
            'Fetch children whose',
            'Get attendance records for all',
            'Build weekly history',
            'managed via JS',
            'SECTION:',
            'TEMPLATE ═════════',
            'Init logos',
            'Scroll reveal',
            'GENERIC POPUP',
            'REAL LOGO',
            'Inline comp',
            'Main comp slot',
            'Spider web',
            'Spider layout',
            'mandala-rings',
            'Node colours',
            'Progress ring',
            'Bar chart',
            'Footer, Toast, Reveal',
            'Welcome popup'
        ]
        
        is_ai_comment = False
        for phrase in ai_phrases:
            if phrase.lower() in stripped.lower() and (stripped.startswith('#') or stripped.startswith('//') or (stripped.startswith('<!--') and stripped.endswith('-->')) or (stripped.startswith('/*') and stripped.endswith('*/'))):
                is_ai_comment = True
                break
        
        if is_ai_comment: continue

        if stripped.startswith('.') and 'JS expects' in stripped: continue
        if stripped.startswith('the current user\'s email') or stripped == 'the current user\'s email': continue

        new_lines.append(line)

    content = "".join(new_lines)
    content = re.sub(r'(\r?\n\s*){3,}', '\n\n', content)
    
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

dirs_to_clean = ['accounts', 'attendance', 'holbos_project', 'modules']
for d in dirs_to_clean:
    if os.path.exists(d):
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith('.py') or file.endswith('.html'):
                    path = os.path.join(root, file)
                    if '__pycache__' in path or 'migrations' in path: continue
                    print(f"Cleaning {path}...")
                    clean_file(path)

print("Project cleanup complete.")
