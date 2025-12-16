"""Custom admin groups page with correct student counts"""
from jupyterhub.handlers import BaseHandler
from jupyterhub import orm
from tornado import web


class CustomAdminGroupsHandler(BaseHandler):
    """Custom admin groups page showing correct student counts"""
    
    @web.authenticated
    async def get(self):
        """Show list of groups with correct student counts"""
        user = self.current_user
        
        if not user.admin:
            self.set_status(403)
            self.write("<h1>Access Denied</h1><p>This page is for administrators only.</p>")
            return
        
        # Get all groups
        groups = self.db.query(orm.Group).order_by(orm.Group.name).all()
        
        # Define who counts as a teacher/admin (not a student)
        teacher_names = {'prof_smith', 'prof_jones', 'prof_doe', 'admin'}
        
        self.log.info(f"AdminGroups DEBUG: Found {len(groups)} total groups")
        
        group_rows = ""
        total_students_across_all = 0
        
        for group in groups:
            # Count students (excluding teachers and admins)
            student_count = sum(1 for u in group.users if u.name not in teacher_names)
            total_users = len(group.users)
            
            if group.name.startswith('teacher-prof-'):
                self.log.info(f"AdminGroups DEBUG: Group {group.name} - Total: {total_users}, Students: {student_count}")
                self.log.info(f"AdminGroups DEBUG:   Members: {[u.name for u in group.users]}")
                total_students_across_all += student_count
            
            # Determine group type
            if group.name == 'teachers':
                group_type = '👨‍🏫 Teachers'
                badge_class = 'badge-teacher'
            elif group.name.startswith('teacher-prof-'):
                teacher_name = group.name.replace('teacher-prof-', 'Prof. ').replace('-', ' ').title()
                group_type = f'📚 {teacher_name}\'s Class'
                badge_class = 'badge-class'
            else:
                group_type = '👥 General'
                badge_class = 'badge-general'
            
            # List users
            user_list = ', '.join([u.name for u in group.users[:5]])
            if len(group.users) > 5:
                user_list += f' and {len(group.users) - 5} more'
            if not user_list:
                user_list = '<em>No members</em>'
            
            group_rows += f"""
            <tr>
                <td>
                    <strong>{group.name}</strong>
                    <span class="group-badge {badge_class}">{group_type}</span>
                </td>
                <td class="count-cell">
                    <div class="count-display">
                        <span class="count-number">{student_count}</span>
                        <span class="count-label">Students</span>
                    </div>
                </td>
                <td class="count-cell">
                    <div class="count-display">
                        <span class="count-number">{total_users}</span>
                        <span class="count-label">Total</span>
                    </div>
                </td>
                <td class="user-list">{user_list}</td>
                <td>
                    <a href="/hub/admin#/groups/{group.name}" class="btn-small btn-primary">Manage</a>
                </td>
            </tr>
            """
        
        if not groups:
            group_rows = '<tr><td colspan="5" style="text-align: center; color: #999;">No groups found</td></tr>'
        
        self.log.info(f"AdminGroups DEBUG: TOTAL STUDENTS ACROSS ALL CLASSES: {total_students_across_all}")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Group Management - Admin</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                    min-height: 100vh;
                    padding: 30px;
                    animation: gradientShift 15s ease infinite;
                    background-size: 200% 200%;
                }}
                
                @keyframes gradientShift {{
                    0% {{ background-position: 0% 50%; }}
                    50% {{ background-position: 100% 50%; }}
                    100% {{ background-position: 0% 50%; }}
                }}
                
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}
                
                .header {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    margin-bottom: 30px;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }}
                
                h1 {{
                    color: #1a202c;
                    margin-bottom: 10px;
                    font-size: 36px;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }}
                
                .subtitle {{
                    color: #718096;
                    font-size: 16px;
                    font-weight: 500;
                }}
                
                .content {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }}
                
                h2 {{
                    color: #1a202c;
                    font-size: 24px;
                    font-weight: 700;
                    margin-bottom: 25px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: separate;
                    border-spacing: 0;
                    margin-top: 20px;
                }}
                
                th {{
                    text-align: left;
                    padding: 16px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-weight: 600;
                    font-size: 14px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                th:first-child {{
                    border-top-left-radius: 12px;
                }}
                
                th:last-child {{
                    border-top-right-radius: 12px;
                }}
                
                td {{
                    padding: 16px;
                    border-bottom: 1px solid #e2e8f0;
                    background: white;
                    color: #2d3748;
                    font-size: 15px;
                    vertical-align: middle;
                }}
                
                tbody tr {{
                    transition: all 0.2s ease;
                }}
                
                tbody tr:hover {{
                    background: #f7fafc;
                    transform: scale(1.01);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                }}
                
                tbody tr:last-child td:first-child {{
                    border-bottom-left-radius: 12px;
                }}
                
                tbody tr:last-child td:last-child {{
                    border-bottom-right-radius: 12px;
                }}
                
                .group-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                    margin-left: 10px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                .badge-teacher {{
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                    color: white;
                }}
                
                .badge-class {{
                    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                    color: white;
                }}
                
                .badge-general {{
                    background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
                    color: white;
                }}
                
                .count-cell {{
                    text-align: center;
                }}
                
                .count-display {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 4px;
                }}
                
                .count-number {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #667eea;
                }}
                
                .count-label {{
                    font-size: 11px;
                    color: #718096;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    font-weight: 600;
                }}
                
                .user-list {{
                    color: #4a5568;
                    font-size: 14px;
                    max-width: 300px;
                }}
                
                .btn-small {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 13px;
                    transition: all 0.2s ease;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                
                .btn-primary {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                
                .btn-primary:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                }}
                
                .nav-links {{
                    margin-top: 30px;
                    padding-top: 30px;
                    border-top: 2px solid #e2e8f0;
                    display: flex;
                    gap: 20px;
                    flex-wrap: wrap;
                }}
                
                .nav-links a {{
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 12px 24px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 10px;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                }}
                
                .nav-links a:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
                    background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
                }}
                
                .refresh {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 12px 24px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    font-weight: 600;
                    font-size: 14px;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    font-family: 'Inter', sans-serif;
                }}
                
                .refresh:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
                    background: linear-gradient(135deg, #059669 0%, #047857 100%);
                }}
                
                @media (max-width: 768px) {{
                    body {{
                        padding: 15px;
                    }}
                    
                    .header, .content {{
                        padding: 25px;
                    }}
                    
                    h1 {{
                        font-size: 28px;
                    }}
                    
                    h2 {{
                        font-size: 20px;
                        flex-direction: column;
                        align-items: flex-start;
                        gap: 15px;
                    }}
                    
                    table {{
                        font-size: 13px;
                    }}
                    
                    th, td {{
                        padding: 10px;
                    }}
                    
                    .user-list {{
                        max-width: 200px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚙️ Group Management</h1>
                    <p class="subtitle">View and manage all JupyterHub groups with correct student counts</p>
                    <div class="stats" style="display: flex; gap: 20px; margin-top: 20px;">
                        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 20px; border-radius: 12px; color: white; flex: 1; text-align: center;">
                            <div style="font-size: 36px; font-weight: bold;">{total_students_across_all}</div>
                            <div style="font-size: 14px; margin-top: 5px;">Total Students Enrolled</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 20px; border-radius: 12px; color: white; flex: 1; text-align: center;">
                            <div style="font-size: 36px; font-weight: bold;">{len(groups)}</div>
                            <div style="font-size: 14px; margin-top: 5px;">Total Groups</div>
                        </div>
                    </div>
                </div>
                
                <div class="content">
                    <h2>
                        <span>📊 All Groups</span>
                        <button class="refresh" onclick="location.reload()">🔄 Refresh</button>
                    </h2>
                    <table>
                        <thead>
                            <tr>
                                <th>👥 Group Name</th>
                                <th>🎓 Students</th>
                                <th>👤 Total Users</th>
                                <th>📋 Members</th>
                                <th>⚙️ Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {group_rows}
                        </tbody>
                    </table>
                    
                    <div class="nav-links">
                        <a href="/hub/home">← Back to Home</a>
                        <a href="/hub/admin">⚙️ Full Admin Panel</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        self.finish(html)


def register_handler(c):
    """Register the custom admin groups handler"""
    if not hasattr(c.JupyterHub, 'extra_handlers') or c.JupyterHub.extra_handlers is None:
        c.JupyterHub.extra_handlers = []
    
    c.JupyterHub.extra_handlers.append((r'/admin-groups', CustomAdminGroupsHandler))
    print("✓ Custom admin groups page available at: /hub/admin-groups")

