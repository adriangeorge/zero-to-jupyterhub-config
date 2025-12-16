"""Teacher dashboard - view students in their class"""
from jupyterhub.handlers import BaseHandler
from jupyterhub import orm
from tornado import web
from datetime import datetime, timezone


class MyStudentsHandler(BaseHandler):
    """Handler for teachers to view their students"""
    
    @web.authenticated
    async def get(self):
        """Show list of students in teacher's class"""
        user = self.current_user
        
        user_groups = {g.name for g in user.groups}
        if 'teachers' not in user_groups and not user.admin:
            self.set_status(403)
            self.write("<h1>Access Denied</h1><p>This page is for teachers only.</p>")
            return
        
        teacher_group_name = None
        for group_name in user_groups:
            if group_name.startswith('teacher-prof-'):
                teacher_group_name = group_name
                break
        
        if not teacher_group_name:
            self.write("<h1>No Class Found</h1><p>You don't have a class assigned yet.</p>")
            return
        
        group = self.db.query(orm.Group).filter_by(name=teacher_group_name).first()
        
        if not group:
            self.write("<h1>Class Not Found</h1>")
            return
        
        teacher_names = {'prof_smith', 'prof_jones', 'prof_doe', 'admin'}
        students = [u for u in group.users if u.name not in teacher_names]
        
        active_count = 0
        
        student_rows = ""
        for student in students:
            try:
                student_spawners = self.db.query(orm.Spawner).filter_by(user_id=student.id).all()
                is_active = any(s.server is not None for s in student_spawners)
                if is_active:
                    active_count += 1
            except:
                is_active = False
            
            status = "🟢 Active" if is_active else "⚪ Offline"
            
            last_activity = student.last_activity
            if last_activity:
                now = datetime.now(timezone.utc)
                if last_activity.tzinfo is None:
                    last_activity = last_activity.replace(tzinfo=timezone.utc)
                
                time_ago = now - last_activity
                if time_ago.days > 0:
                    activity_str = f"{time_ago.days} days ago"
                elif time_ago.seconds > 3600:
                    activity_str = f"{time_ago.seconds // 3600} hours ago"
                elif time_ago.seconds > 60:
                    activity_str = f"{time_ago.seconds // 60} minutes ago"
                else:
                    activity_str = "Just now"
            else:
                activity_str = "Never"
            
            student_rows += f"""
            <tr>
                <td>{student.name}</td>
                <td>{status}</td>
                <td>{activity_str}</td>
            </tr>
            """
        
        if not students:
            student_rows = '<tr><td colspan="3" style="text-align: center; color: #999;">No students in your class yet</td></tr>'
        
        teacher_name = teacher_group_name.replace('teacher-prof-', 'Prof. ').replace('-', ' ').title()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>My Students - {teacher_name}</title>
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
                    max-width: 1200px;
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
                    margin-bottom: 20px;
                }}
                
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-top: 25px;
                }}
                
                .stat-box {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 25px;
                    border-radius: 16px;
                    text-align: center;
                    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
                    transition: all 0.3s ease;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                
                .stat-box:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
                }}
                
                .stat-box:nth-child(2) {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
                }}
                
                .stat-box:nth-child(2):hover {{
                    box-shadow: 0 12px 30px rgba(16, 185, 129, 0.4);
                }}
                
                .stat-number {{
                    font-size: 48px;
                    font-weight: 700;
                    color: white;
                    margin-bottom: 8px;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                
                .stat-label {{
                    color: rgba(255, 255, 255, 0.95);
                    font-size: 14px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
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
                    
                    .stats {{
                        grid-template-columns: 1fr;
                    }}
                    
                    table {{
                        font-size: 14px;
                    }}
                    
                    th, td {{
                        padding: 12px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>👨‍🏫 {teacher_name}'s Class</h1>
                    <p class="subtitle">Hello, {user.name}! Welcome to your student dashboard</p>
                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-number">{len(students)}</div>
                            <div class="stat-label">Total Students</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{active_count}</div>
                            <div class="stat-label">Currently Active</div>
                        </div>
                    </div>
                </div>
                
                <div class="content">
                    <h2>
                        <span>📋 Student List</span>
                        <button class="refresh" onclick="location.reload()">🔄 Refresh</button>
                    </h2>
                    <table>
                        <thead>
                            <tr>
                                <th>👤 Student Name</th>
                                <th>📊 Status</th>
                                <th>🕐 Last Activity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {student_rows}
                        </tbody>
                    </table>
                    
                    <div class="nav-links">
                        <a href="/hub/home">← Back to Home</a>
                        <a href="/hub/admin">⚙️ Admin Panel</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        self.finish(html)


def register_handler(c):
    """Register the my students handler"""
    if not hasattr(c.JupyterHub, 'extra_handlers') or c.JupyterHub.extra_handlers is None:
        c.JupyterHub.extra_handlers = []
    
    c.JupyterHub.extra_handlers.append((r'/my-students', MyStudentsHandler))
    print("✓ Teacher dashboard available at: /hub/my-students")


