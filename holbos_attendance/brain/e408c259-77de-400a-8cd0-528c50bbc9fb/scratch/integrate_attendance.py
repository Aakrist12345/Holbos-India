import os

def integrate_attendance():
    root_dir = r"c:\Users\AAKRIST SHARMA\OneDrive\Desktop\HolbosIndia"

    attendance_file = os.path.join(root_dir, "accounts", "templates", "accounts", "attendance.html")
    dashboard_file = os.path.join(root_dir, "accounts", "templates", "accounts", "dashboard.html")

    if os.path.exists(attendance_file):
        with open(attendance_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'autologin' not in content:
            replacement = """        document.getElementById('attDate').value = new Date().toISOString().split('T')[0];

        // Auto-login logic for dash integration
        window.addEventListener('load', () => {
            const params = new URLSearchParams(window.location.search);
            if (params.get('autologin') === 'true') {
                const username = params.get('user') || 'Trainer';
                currentTrainer = { id: 999, name: username, username: username };
                // Hide redundant UI
                const sidebar = document.getElementById('sidebar');
                if (sidebar) sidebar.style.display = 'none';
                const navbar = document.querySelector('.navbar');
                if (navbar) navbar.style.display = 'none';
                const mainContent = document.querySelector('.main-content');
                if (mainContent) mainContent.style.paddingLeft = '1rem';
                
                launchApp();
            }
        });
    </script>"""
            content = content.replace("document.getElementById('attDate').value = new Date().toISOString().split('T')[0];\n    </script>", replacement)
            with open(attendance_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Updated attendance.html")

    if os.path.exists(dashboard_file):
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()

        old_part_start = '<div class="node web-node" id="node4" onclick="openPopup(\'attendance\')">'
        if old_part_start in content:

            insertion_point = content.find('</div>', content.find('<div class="node-icon-wrap"', content.find(old_part_start)))
            if insertion_point != -1:
                insertion_point += 6 # after </div>
                new_text = """
                    <h3>Attendance</h3>
                    <p>Record daily presence.</p>
                    <span class="node-tag">Track</span>
                    <span class="node-arrow">→</span>"""
                if '<h3>Attendance</h3>' not in content:
                    content = content[:insertion_point] + new_text + content[insertion_point:]

            content = content.replace('src="/attendance/"', 'src="/attendance/?autologin=true&user={{ user.username }}"')
            
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Updated dashboard.html")

if __name__ == "__main__":
    integrate_attendance()
