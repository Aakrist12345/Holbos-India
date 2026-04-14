import os

def update_project_dashboard():
    project_dashboard = r"c:\Users\AAKRIST SHARMA\OneDrive\Desktop\HolbosIndia\holbos_project\accounts\templates\accounts\dashboard.html"
    
    if os.path.exists(project_dashboard):
        with open(project_dashboard, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Add attendanceTemplate if missing
        if 'id="attendanceTemplate"' not in content:
            template = """
        <!-- ═════════ ATTENDANCE TEMPLATE ═════════ -->
        <div style="display:none;" id="attendanceTemplate">
            <iframe src="/attendance/?autologin=true&user={{ user.username }}" style="width:100%; height:80vh; border:none; border-radius:12px;"></iframe>
        </div>
"""
            # Insert before page-body close or somewhere safe
            insertion = content.find('</div> <!-- /page-body -->')
            if insertion != -1:
                content = content[:insertion] + template + content[insertion:]
        else:
            # Update existing iframe
            content = content.replace('src="/attendance/"', 'src="/attendance/?autologin=true&user={{ user.username }}"')

        # Update openPopup to use the template for attendance
        import re
        content = re.sub(r'(else if \(type === \'attendance\'\) \{[\s\S]*?body\.innerHTML = )([\s\S]*?);', 
                        r"\1document.getElementById('attendanceTemplate').innerHTML;", content)

        with open(project_dashboard, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated project dashboard.html")

if __name__ == "__main__":
    update_project_dashboard()
