"""Custom home page with role-based action buttons"""
from jupyterhub.handlers import BaseHandler
from tornado import web


class CustomHomeHandler(BaseHandler):
    """Custom home page with role-based action buttons"""
    
    @web.authenticated
    async def get(self):
        """Show custom home page with appropriate buttons"""
        user = self.current_user
        username = user.name
        
        # Get user groups from ORM
        orm_user = self.db.query(self.hub.orm.User).filter_by(name=username).first()
        user_groups = {g.name for g in orm_user.groups} if orm_user else set()
        self.log.info(f"CustomHome DEBUG: User {username} has groups: {user_groups}")
        
        # Check user roles - EXPLICIT LOGIC
        is_admin = user.admin
        is_teacher_by_name = username in ['prof_smith', 'prof_jones', 'prof_doe']
        is_teacher = 'teachers' in user_groups or is_teacher_by_name
        is_student = not is_admin and not is_teacher
        
        self.log.info(f"CustomHome DEBUG: User={username}, Groups={user_groups}")
        self.log.info(f"CustomHome DEBUG: is_admin={is_admin}, is_teacher={is_teacher}, is_student={is_student}")
        self.log.info(f"CustomHome DEBUG: Will show Admin buttons: {is_admin}, Teacher buttons: {is_teacher}, Student info: {is_student}")
        
        # Check server status
        try:
            spawner = user.orm_spawners[0] if user.orm_spawners else None
            server_running = spawner.server is not None if spawner else False
        except:
            server_running = False
        
        # Get student's current class (if student)
        current_class = None
        if is_student and user_groups:
            for group_name in user_groups:
                if group_name.startswith('teacher-prof-'):
                    current_class = group_name.replace('teacher-prof-', 'Prof. ').replace('-', ' ').title()
                    break
        
        actions_html = ""
        
        # Server control card
        if server_running:
            actions_html += f'''
            <div class="action-card server-running">
                <div class="action-icon">🚀</div>
                <h3>Your Server is Running</h3>
                <p>JupyterLab environment is active</p>
                <div class="button-group">
                    <a href="/user/{username}/" class="btn btn-primary">
                        <span class="btn-icon">📊</span> Open JupyterLab
                    </a>
                    <form method="post" action="/hub/api/users/{username}/server" style="display: inline;">
                        <input type="hidden" name="_xsrf" value="{self.xsrf_token.decode('utf-8')}" />
                        <button type="submit" class="btn btn-danger">
                            <span class="btn-icon">⏹️</span> Stop Server
                        </button>
                    </form>
                </div>
            </div>
            '''
        else:
            actions_html += f'''
            <div class="action-card server-stopped">
                <div class="action-icon">💤</div>
                <h3>Start Your Server</h3>
                <p>Launch your JupyterLab environment</p>
                <a href="/hub/spawn" class="btn btn-success">
                    <span class="btn-icon">▶️</span> Start Server
                </a>
            </div>
            '''
        
        # Student-specific actions
        if is_student:
            class_display = f'<strong>{current_class}</strong>' if current_class else 'Not enrolled yet'
            actions_html += f'''
            <div class="action-card student-class">
                <div class="action-icon">👥</div>
                <h3>My Class</h3>
                <p class="class-info">Currently enrolled in:<br/>{class_display}</p>
                <p class="help-text">To change classes, stop your server and restart to choose a new one</p>
            </div>
            '''
        
        # Teacher-specific actions - prominently display student management
        if is_teacher:
            self.log.info(f"CustomHome DEBUG: Adding TEACHER BUTTON for {username}")
            
            # Get teacher's group to show student count
            teacher_group_name = None
            student_count = 0
            for group_name in user_groups:
                if group_name.startswith('teacher-prof-'):
                    teacher_group_name = group_name
                    # Get actual student count
                    try:
                        group = self.db.query(self.hub.orm.Group).filter_by(name=teacher_group_name).first()
                        if group:
                            teacher_names = {'prof_smith', 'prof_jones', 'prof_doe', 'admin'}
                            student_count = sum(1 for u in group.users if u.name not in teacher_names)
                            self.log.info(f"CustomHome DEBUG: Teacher group {teacher_group_name} has {student_count} students")
                    except Exception as e:
                        self.log.error(f"CustomHome ERROR: Failed to count students: {e}")
                    break
            
            student_text = f'{student_count} student{"s" if student_count != 1 else ""} enrolled'
            
            actions_html += f'''
            <div class="action-card teacher-students">
                <div class="action-icon">👨‍🎓</div>
                <h3>My Students</h3>
                <p class="student-count-badge">{student_text}</p>
                <p>View and monitor students in your class</p>
                <a href="/hub/my-students" class="btn btn-info">
                    <span class="btn-icon">📋</span> View My Students
                </a>
            </div>
            '''
            self.log.info(f"CustomHome DEBUG: TEACHER BUTTON ADDED successfully")
        
        # Admin-specific actions
        if is_admin:
            self.log.info(f"CustomHome DEBUG: Adding ADMIN BUTTONS for {username}")
            
            actions_html += '''
            <div class="action-card admin-panel">
                <div class="action-icon">⚙️</div>
                <h3>Admin Panel</h3>
                <p>Manage users, servers, and system settings</p>
                <a href="/hub/admin" class="btn btn-warning">
                    <span class="btn-icon">🔧</span> Admin Panel
                </a>
            </div>
            <div class="action-card admin-authorize">
                <div class="action-icon">✅</div>
                <h3>Authorize Users</h3>
                <p>Approve or reject pending registrations</p>
                <a href="/hub/authorize" class="btn btn-primary">
                    <span class="btn-icon">👤</span> Authorize Users
                </a>
            </div>
            <div class="action-card admin-groups">
                <div class="action-icon">👥</div>
                <h3>Manage Groups</h3>
                <p>View groups with correct student counts</p>
                <a href="/hub/admin-groups" class="btn btn-info">
                    <span class="btn-icon">📊</span> View Groups
                </a>
            </div>
            '''
            self.log.info(f"CustomHome DEBUG: ADMIN BUTTONS ADDED successfully (including Manage Groups button)")
        
        # Common action - change password
        actions_html += '''
        <div class="action-card change-password">
            <div class="action-icon">🔒</div>
            <h3>Change Password</h3>
            <p>Update your account security</p>
            <a href="/hub/change-password" class="btn btn-secondary">
                <span class="btn-icon">🔑</span> Change Password
            </a>
        </div>
        '''
        
        # User badge
        if is_admin:
            user_badge = '<span class="badge badge-admin">👑 Administrator</span>'
        elif is_teacher:
            user_badge = '<span class="badge badge-teacher">👨‍🏫 Teacher</span>'
        else:
            user_badge = '<span class="badge badge-student">🎓 Student</span>'
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>JupyterHub - Home</title>
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
                    padding: 20px;
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
                
                .header h1 {{
                    color: #1a202c;
                    margin-bottom: 10px;
                    font-size: 32px;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }}
                
                .header p {{
                    color: #718096;
                    font-size: 18px;
                    font-weight: 500;
                }}
                
                .badge {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 25px;
                    font-size: 14px;
                    font-weight: 600;
                    margin-left: 12px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
                }}
                
                .badge-admin {{
                    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                    color: white;
                }}
                
                .badge-teacher {{
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                    color: white;
                }}
                
                .badge-student {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                }}
                
                .actions-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                    gap: 25px;
                    margin-bottom: 30px;
                }}
                
                .action-card {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    padding: 35px;
                    border-radius: 16px;
                    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
                    text-align: center;
                    transition: all 0.3s ease;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    position: relative;
                    overflow: hidden;
                }}
                
                .action-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    opacity: 0;
                    transition: opacity 0.3s ease;
                }}
                
                .action-card:hover {{
                    transform: translateY(-8px);
                    box-shadow: 0 12px 30px rgba(0,0,0,0.2);
                }}
                
                .action-card:hover::before {{
                    opacity: 1;
                }}
                
                .server-running::before {{ background: linear-gradient(90deg, #10b981 0%, #059669 100%); }}
                .server-stopped::before {{ background: linear-gradient(90deg, #6b7280 0%, #4b5563 100%); }}
                .student-class::before {{ background: linear-gradient(90deg, #8b5cf6 0%, #7c3aed 100%); }}
                .teacher-students::before {{ background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); }}
                .admin-panel::before {{ background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%); }}
                .admin-authorize::before {{ background: linear-gradient(90deg, #10b981 0%, #059669 100%); }}
                .admin-groups::before {{ background: linear-gradient(90deg, #8b5cf6 0%, #7c3aed 100%); }}
                .change-password::before {{ background: linear-gradient(90deg, #6b7280 0%, #4b5563 100%); }}
                
                .action-icon {{
                    font-size: 56px;
                    margin-bottom: 20px;
                    display: block;
                    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
                }}
                
                .action-card h3 {{
                    color: #1a202c;
                    margin-bottom: 12px;
                    font-size: 22px;
                    font-weight: 700;
                }}
                
                .action-card p {{
                    color: #718096;
                    margin-bottom: 20px;
                    font-size: 15px;
                    line-height: 1.6;
                }}
                
                .student-count-badge {{
                    display: inline-block;
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 15px;
                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                }}
                
                .class-info {{
                    color: #4a5568;
                    font-size: 16px;
                    margin-bottom: 10px;
                }}
                
                .help-text {{
                    color: #a0aec0;
                    font-size: 13px;
                    font-style: italic;
                    margin-top: 10px;
                }}
                
                .button-group {{
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                    flex-wrap: wrap;
                }}
                
                .btn {{
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 14px 28px;
                    border-radius: 10px;
                    text-decoration: none;
                    font-weight: 600;
                    margin: 5px;
                    border: none;
                    cursor: pointer;
                    font-size: 16px;
                    transition: all 0.2s ease;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    text-align: center;
                    font-family: 'Inter', sans-serif;
                }}
                
                .btn-icon {{
                    font-size: 18px;
                }}
                
                .btn-primary {{
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                    color: white;
                }}
                
                .btn-primary:hover {{
                    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
                }}
                
                .btn-success {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                }}
                
                .btn-success:hover {{
                    background: linear-gradient(135deg, #059669 0%, #047857 100%);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(5, 150, 105, 0.4);
                }}
                
                .btn-danger {{
                    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                    color: white;
                }}
                
                .btn-danger:hover {{
                    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(220, 38, 38, 0.4);
                }}
                
                .btn-warning {{
                    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                    color: white;
                }}
                
                .btn-warning:hover {{
                    background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(217, 119, 6, 0.4);
                }}
                
                .btn-secondary {{
                    background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
                    color: white;
                }}
                
                .btn-secondary:hover {{
                    background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(75, 85, 99, 0.4);
                }}
                
                .btn-info {{
                    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                    color: white;
                }}
                
                .btn-info:hover {{
                    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(124, 58, 237, 0.4);
                }}
                
                .logout-section {{
                    text-align: center;
                    margin-top: 40px;
                    padding: 25px;
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                
                .logout-link {{
                    color: white;
                    text-decoration: none;
                    font-size: 18px;
                    font-weight: 600;
                    padding: 12px 24px;
                    border-radius: 10px;
                    display: inline-block;
                    transition: all 0.2s ease;
                    background: rgba(255, 255, 255, 0.1);
                }}
                
                .logout-link:hover {{
                    background: rgba(255, 255, 255, 0.2);
                    transform: scale(1.05);
                }}
                
                @media (max-width: 768px) {{
                    .actions-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .header h1 {{
                        font-size: 24px;
                    }}
                    
                    .button-group {{
                        flex-direction: column;
                    }}
                    
                    .btn {{
                        width: 100%;
                        justify-content: center;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome, {username}! {user_badge}</h1>
                    <p>JupyterHub Control Panel</p>
                </div>
                
                <div class="actions-grid">
                    {actions_html}
                </div>
                
                <div class="logout-section">
                    <a href="/hub/logout" class="logout-link">🚪 Logout</a>
                </div>
            </div>
        </body>
        </html>
        '''
        self.finish(html)


def replace_home_handler(web_app):
    """Hook to replace the built-in home handler with our custom one"""
    if not hasattr(web_app, 'handlers'):
        return
    
    for host_pattern, handlers_list in web_app.handlers:
        for i, handler_tuple in enumerate(handlers_list):
            pattern = handler_tuple[0]
            handler_class = handler_tuple[1]
            
            # Get pattern string
            if hasattr(pattern, 'pattern'):
                pattern_str = pattern.pattern
            else:
                pattern_str = str(pattern)
            
            # Find and replace the home handler
            if '/home' in pattern_str and handler_class.__name__ == 'HomeHandler':
                print(f"  → Found built-in HomeHandler at pattern: {pattern_str}")
                # Replace with our custom handler, keeping other tuple elements
                handlers_list[i] = (pattern, CustomHomeHandler) + handler_tuple[2:]
                print(f"  → Replaced with CustomHomeHandler")
                return

def register_handler(c):
    """Register the custom home handler to override built-in /home"""
    
    # Set the hook to replace the handler after web app is initialized
    original_init_webapp = getattr(c.JupyterHub, 'init_webapp', None)
    
    def custom_init_webapp(self):
        """Initialize webapp and replace home handler"""
        # Call original init_webapp if it exists
        if original_init_webapp and callable(original_init_webapp):
            result = original_init_webapp(self)
        else:
            result = None
        
        # Now replace the home handler
        if hasattr(self, 'web_app') and self.web_app:
            replace_home_handler(self.web_app)
        
        return result
    
    c.JupyterHub.init_webapp = custom_init_webapp
    
    print("✓ Custom home page handler will replace built-in /home")
