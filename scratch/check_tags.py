import re

def check_html_balance(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Simple tag balancer
    # We only care about major tags like div, section, main, etc.
    tags = re.findall(r'<(div|section|main|nav|header|footer|ul|ol|li|script|style|head|body|html)[^>]*>|<\/(div|section|main|nav|header|footer|ul|ol|li|script|style|head|body|html)>', content)
    
    stack = []
    for open_tag, close_tag in tags:
        if open_tag:
            # Handle self-closing if any (though we only listed non-self-closing ones)
            if not open_tag.endswith('/'):
                stack.append(open_tag.split()[0])
        else:
            if not stack:
                print(f"Unexpected closing tag: </{close_tag}>")
            else:
                last = stack.pop()
                if last != close_tag:
                    print(f"Mismatched tag: Expected </{last}>, found </{close_tag}>")
    
    if stack:
        print(f"Unclosed tags: {stack}")
    else:
        print("Tags are balanced (major ones).")

if __name__ == "__main__":
    check_html_balance(r'c:\Users\AAKRIST SHARMA\OneDrive\Desktop\HolbosIndia\accounts\templates\accounts\parentsdashboard.html')
