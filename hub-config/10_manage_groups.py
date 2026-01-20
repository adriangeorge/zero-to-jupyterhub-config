"""Custom groups management page"""
from jupyterhub.handlers import BaseHandler
from jupyterhub import orm
from tornado import web
import json


class ManageGroupsHandler(BaseHandler):
    """Custom group management interface"""
    
    @web.authenticated
    async def get(self):
        """Show group management page"""
        user = self.current_user
        
        if not user.admin:
            self.set_status(403)
            self.write("<h1>Access Denied</h1><p>This page is for administrators only.</p>")
            return
        
        # Get all groups and users
        all_groups = self.db.query(orm.Group).order_by(orm.Group.name).all()
        all_users = self.db.query(orm.User).order_by(orm.User.name).all()
        
        # Define protected users (teachers and admins)
        protected_users = {'admin', 'prof_smith', 'prof_jones', 'prof_doe'}
        
        # Build groups list
        groups_html = ""
        for group in all_groups:
            if group.name in ['admins', 'teachers'] or group.name.startswith('teacher-prof-'):
                member_names = sorted([u.name for u in group.users])
                members_list = ', '.join(member_names) if member_names else '<em style="color: #999;">No members</em>'
                
                # For prof groups, separate prof from students for JSON
                if group.name.startswith('teacher-prof-'):
                    # Only send student names to modal (excluding the prof)
                    student_names = [name for name in member_names if name not in protected_users]
                    members_json = json.dumps(student_names)
                else:
                    members_json = json.dumps(member_names)
                
                # Display name for UI
                display_name = group.name.replace('teacher-prof-', 'Prof. ').replace('-', ' ').title()
                
                # Check if group is editable
                is_editable = group.name not in ['admins', 'teachers']
                
                if is_editable:
                    # Extract prof name for this specific group
                    prof_username = group.name.replace('teacher-', '').replace('-', '_') if group.name.startswith('teacher-prof-') else ''
                    edit_button = f'<button class="btn-action" onclick=\'showEditModal("{group.name}", "{display_name}", {members_json}, "{prof_username}")\'>Edit Members</button>'
                else:
                    edit_button = '<button class="btn-action" disabled style="opacity: 0.5; cursor: not-allowed;">Protected Group</button>'
                
                groups_html += f"""
                <div class="group-card" data-group="{group.name}">
                    <div class="group-header">
                        <h4>{display_name}</h4>
                        <span class="member-count">{len(group.users)} members</span>
                    </div>
                    <div class="group-body">
                        <p class="members-list">{members_list}</p>
                        <div class="group-actions">
                            {edit_button}
                        </div>
                    </div>
                </div>
                """
        
        # Build all users list for the modal - ONLY students (exclude protected users)
        students_only = [{"name": u.name} for u in all_users if u.name not in protected_users]
        all_users_json = json.dumps(students_only)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Manage Groups</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="/hub/static/css/style.min.css" type="text/css" />
            <style>
                body {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                }}
                .page-title {{
                    text-align: center;
                    margin: 40px 0 12px;
                    color: #fff;
                    font-size: 2.8em;
                    font-weight: 800;
                    text-shadow: 0 4px 20px rgba(0,0,0,0.3);
                }}
                .page-subtitle {{
                    text-align: center;
                    margin-bottom: 32px;
                    color: rgba(255, 255, 255, 0.92);
                    font-size: 1.15em;
                }}
                .groups-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .group-card {{
                    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
                    border-radius: 16px;
                    padding: 24px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    border: 1px solid rgba(255,255,255,0.2);
                    transition: transform 0.3s ease;
                }}
                .group-card:hover {{
                    transform: translateY(-4px);
                }}
                .group-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 16px;
                    padding-bottom: 16px;
                    border-bottom: 2px solid #e0e0e0;
                }}
                .group-header h4 {{
                    margin: 0;
                    color: #667eea;
                    font-size: 1.3em;
                }}
                .member-count {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 6px 12px;
                    border-radius: 20px;
                    font-size: 13px;
                    font-weight: 600;
                }}
                .members-list {{
                    color: #555;
                    font-size: 14px;
                    line-height: 1.6;
                    margin-bottom: 16px;
                    min-height: 40px;
                }}
                .btn-action {{
                    width: 100%;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 10px;
                    border: none;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #fff;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .btn-action:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                }}
                .button-row {{
                    text-align: center;
                    margin-top: 30px;
                }}
                .btn {{
                    padding: 14px 28px;
                    font-size: 15px;
                    font-weight: 600;
                    border-radius: 12px;
                    border: none;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #fff;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
                    color: #fff;
                    text-decoration: none;
                }}
                
                /* Modal styles */
                .modal {{
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.6);
                    backdrop-filter: blur(5px);
                }}
                .modal-content {{
                    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
                    margin: 5% auto;
                    padding: 32px;
                    border-radius: 20px;
                    width: 90%;
                    max-width: 600px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }}
                .modal-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 24px;
                }}
                .modal-header h3 {{
                    margin: 0;
                    color: #667eea;
                    font-size: 1.8em;
                }}
                .close {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #999;
                    cursor: pointer;
                    transition: color 0.3s;
                }}
                .close:hover {{
                    color: #667eea;
                }}
                .user-list {{
                    max-height: 400px;
                    overflow-y: auto;
                    margin-bottom: 20px;
                    border: 2px solid #e0e0e0;
                    border-radius: 12px;
                    padding: 16px;
                }}
                .user-item {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px;
                    margin-bottom: 8px;
                    background: #fff;
                    border-radius: 8px;
                    transition: all 0.2s;
                }}
                .user-item:hover {{
                    background: rgba(102, 126, 234, 0.05);
                }}
                .user-item input[type="checkbox"] {{
                    width: 20px;
                    height: 20px;
                    cursor: pointer;
                }}
                .modal-actions {{
                    display: flex;
                    gap: 12px;
                    justify-content: flex-end;
                }}
                .btn-save {{
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 10px;
                    border: none;
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    color: #fff;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                .btn-save:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
                }}
                .btn-cancel {{
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 10px;
                    border: 2px solid #667eea;
                    background: transparent;
                    color: #667eea;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                .btn-cancel:hover {{
                    background: #667eea;
                    color: #fff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="page-title">Manage Groups</h1>
                <p class="page-subtitle">Add or remove users from groups</p>
                
                <div class="groups-grid">
                    {groups_html}
                </div>
                
                <div class="button-row">
                    <a class="btn" href="/hub/admin-panel">Back to Admin Panel</a>
                </div>
            </div>
            
            <!-- Edit Modal -->
            <div id="editModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 id="modalGroupName">Edit Group</h3>
                        <span class="close" onclick="closeModal()">&times;</span>
                    </div>
                    <div class="user-list" id="userList"></div>
                    <div class="modal-actions">
                        <button class="btn-cancel" onclick="closeModal()">Cancel</button>
                        <button class="btn-save" onclick="saveChanges()">Save Changes</button>
                    </div>
                </div>
            </div>
            
            <script>
                const allUsers = {all_users_json};
                let currentGroup = '';
                let currentMembers = [];
                let currentProfessor = '';
                
                function showEditModal(groupName, displayName, members, profUsername) {{
                    currentGroup = groupName;  // Store actual group name (e.g., "teacher-prof-smith")
                    currentMembers = members;
                    currentProfessor = profUsername || '';
                    
                    document.getElementById('modalGroupName').textContent = 'Edit Group: ' + displayName;
                    
                    const userList = document.getElementById('userList');
                    userList.innerHTML = '';
                    
                    // If there's a professor, show them as permanent member
                    if (currentProfessor) {{
                        const profItem = document.createElement('div');
                        profItem.className = 'user-item';
                        profItem.style.background = 'rgba(102, 126, 234, 0.1)';
                        profItem.style.borderLeft = '4px solid #667eea';
                        profItem.innerHTML = `
                            <label style="display: flex; align-items: center; gap: 10px; width: 100%;">
                                <input type="checkbox" checked disabled style="opacity: 0.5;">
                                <span style="font-weight: 600; color: #667eea;">${{currentProfessor}} (Group Owner - Permanent)</span>
                            </label>
                        `;
                        userList.appendChild(profItem);
                        
                        // Add separator
                        const separator = document.createElement('div');
                        separator.style.borderTop = '2px solid #e0e0e0';
                        separator.style.margin = '12px 0';
                        userList.appendChild(separator);
                    }}
                    
                    // Show student users
                    allUsers.forEach(user => {{
                        const isChecked = members.includes(user.name);
                        const item = document.createElement('div');
                        item.className = 'user-item';
                        item.innerHTML = `
                            <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; width: 100%;">
                                <input type="checkbox" value="${{user.name}}" ${{isChecked ? 'checked' : ''}}>
                                <span style="font-weight: 500;">${{user.name}}</span>
                            </label>
                        `;
                        userList.appendChild(item);
                    }});
                    
                    document.getElementById('editModal').style.display = 'block';
                }}
                
                function closeModal() {{
                    document.getElementById('editModal').style.display = 'none';
                }}
                
                async function saveChanges() {{
                    const checkboxes = document.querySelectorAll('#userList input[type="checkbox"]:not([disabled])');
                    const selectedUsers = Array.from(checkboxes)
                        .filter(cb => cb.checked)
                        .map(cb => cb.value);
                    
                    console.log('Saving group:', currentGroup, 'with users:', selectedUsers);
                    
                    const xsrfToken = getCookie('_xsrf');
                    console.log('XSRF token:', xsrfToken);
                    
                    try {{
                        const response = await fetch('/hub/manage-groups', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                                'X-XSRFToken': xsrfToken
                            }},
                            body: JSON.stringify({{
                                group: currentGroup,
                                users: selectedUsers
                            }})
                        }});
                        
                        if (response.ok) {{
                            window.location.reload();
                        }} else {{
                            const error = await response.text();
                            console.error('Error response:', error);
                            alert('Failed to save changes: ' + response.status + ' - ' + error);
                        }}
                    }} catch (error) {{
                        console.error('Error:', error);
                        alert('Error saving changes: ' + error);
                    }}
                }}
                
                function getCookie(name) {{
                    const value = `; ${{document.cookie}}`;
                    const parts = value.split(`; ${{name}}=`);
                    if (parts.length === 2) return parts.pop().split(';').shift();
                }}
                
                // Close modal when clicking outside
                window.onclick = function(event) {{
                    const modal = document.getElementById('editModal');
                    if (event.target == modal) {{
                        closeModal();
                    }}
                }}
            </script>
        </body>
        </html>
        """
        self.finish(html)
    
    @web.authenticated
    async def post(self):
        """Handle group membership updates"""
        user = self.current_user
        
        if not user.admin:
            self.set_status(403)
            self.write({"error": "Access denied"})
            return
        
        import json
        data = json.loads(self.request.body.decode('utf-8'))
        group_name = data.get('group')
        user_names = data.get('users', [])
        
        self.log.info(f"Updating group {group_name} with users: {user_names}")
        
        # Validate: cannot edit protected groups
        if group_name in ['admins', 'teachers']:
            self.set_status(403)
            self.write({"error": f"Group '{group_name}' is protected and cannot be edited"})
            return
        
        # Get the group
        group = self.db.query(orm.Group).filter_by(name=group_name).first()
        if not group:
            self.set_status(404)
            self.write({"error": f"Group '{group_name}' not found"})
            return
        
        # Define protected users (teachers and admins)
        protected_users = {'admin', 'prof_smith', 'prof_jones', 'prof_doe'}
        
        # Validate: prof groups can only contain students (no teachers or admins)
        if group_name.startswith('teacher-prof-'):
            invalid_users = [name for name in user_names if name in protected_users]
            if invalid_users:
                self.set_status(400)
                self.write({"error": f"Cannot add teachers or admins to class groups. Invalid users: {', '.join(invalid_users)}"})
                return
        
        # Get all users to add (only non-protected users)
        users_to_add = []
        for username in user_names:
            u = self.db.query(orm.User).filter_by(name=username).first()
            if u and username not in protected_users:
                users_to_add.append(u)
        
        # For prof groups: enforce that students can only be in ONE prof group
        if group_name.startswith('teacher-prof-'):
            # Get all other prof groups
            all_prof_groups = self.db.query(orm.Group).filter(
                orm.Group.name.like('teacher-prof-%'),
                orm.Group.name != group_name
            ).all()
            
            # Remove students from other prof groups
            for student in users_to_add:
                for other_group in all_prof_groups:
                    if student in other_group.users:
                        other_group.users.remove(student)
                        self.log.info(f"Removed {student.name} from {other_group.name} (moving to {group_name})")
            
            # Extract prof name from group name (e.g., "teacher-prof-smith" -> "prof_smith")
            prof_name = group_name.replace('teacher-', '').replace('-', '_')
            prof_user = self.db.query(orm.User).filter_by(name=prof_name).first()
            if prof_user and prof_user not in users_to_add:
                users_to_add.append(prof_user)
                self.log.info(f"Keeping {prof_name} in their own group {group_name}")
        
        # Update group membership
        group.users = users_to_add
        self.db.commit()
        
        self.log.info(f"Successfully updated group {group_name}")
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({"status": "success"}))
        self.finish()


def register_handler(c):
    """Register the manage groups handler"""
    if not hasattr(c.JupyterHub, 'extra_handlers') or c.JupyterHub.extra_handlers is None:
        c.JupyterHub.extra_handlers = []
    
    c.JupyterHub.extra_handlers.append((r'/manage-groups', ManageGroupsHandler))
    print("✓ Custom groups management available at: /hub/manage-groups")
