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
            
            status = "Active" if is_active else "Offline"
            status_badge = f'<span style="color: #38ef7d; font-weight: 600;">{status}</span>' if is_active else f'<span style="color: #95a5a6; font-weight: 600;">{status}</span>'
            
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
            
            # Add connect button
            connect_btn = f'<a href="/user/{student.name}/" target="_blank" class="btn btn-xs" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 6px 14px; border-radius: 8px; text-decoration: none; font-weight: 600;">Connect</a>'
            
            student_rows += f"""
            <tr>
                <td>{student.name}</td>
                <td>{status_badge}</td>
                <td>{activity_str}</td>
                <td>{connect_btn}</td>
            </tr>
            """
        
        if not students:
            student_rows = '<tr><td colspan="4" style="text-align: center; color: #999;">No students in your class yet</td></tr>'
        
        teacher_name = teacher_group_name.replace('teacher-prof-', 'Prof. ').replace('-', ' ').title()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>My Students - {teacher_name}</title>
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
                    letter-spacing: -0.5px;
                }}
                .page-subtitle {{
                    text-align: center;
                    margin-bottom: 32px;
                    color: rgba(255, 255, 255, 0.92);
                    font-size: 1.15em;
                    font-weight: 400;
                    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
                }}
                .button-row {{
                    text-align: center;
                    margin-top: 24px;
                }}
                .button-row .btn {{
                    margin: 8px;
                    min-width: 180px;
                    padding: 14px 28px;
                    font-size: 15px;
                    font-weight: 600;
                    border-radius: 12px;
                    border: none;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #fff;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    cursor: pointer;
                }}
                .button-row .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
                    text-decoration: none;
                    color: #fff;
                }}
                .card-panel {{
                    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
                    border-radius: 20px;
                    padding: 32px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.25), 0 0 0 1px rgba(255,255,255,0.1);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                }}
                .stats-bar {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 16px;
                    margin-bottom: 24px;
                    text-align: center;
                    font-size: 16px;
                    font-weight: 700;
                    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
                }}
                .stats-bar strong {{
                    font-size: 20px;
                    margin: 0 4px;
                }}
                .table {{
                    margin-bottom: 0;
                }}
                .table th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    font-size: 13px;
                    padding: 14px 12px;
                    border: none;
                }}
                .table th:first-child {{
                    border-top-left-radius: 12px;
                }}
                .table th:last-child {{
                    border-top-right-radius: 12px;
                }}
                .table td {{
                    vertical-align: middle;
                    padding: 16px 12px;
                    font-size: 14px;
                    border-bottom: 1px solid #e9ecef;
                }}
                .table tbody tr {{
                    transition: all 0.2s ease;
                }}
                .table tbody tr:hover {{
                    background: rgba(102, 126, 234, 0.05);
                    transform: scale(1.01);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="page-title">{teacher_name}'s Class</h1>
                <p class="page-subtitle">Hello, {user.name}! Here's your student roster.</p>

                <div class="card-panel">
                    <div class="stats-bar">
                        Total Students: <strong>{len(students)}</strong> &nbsp; • &nbsp; Active Now: <strong>{active_count}</strong>
                    </div>

                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Student Name</th>
                                <th>Status</th>
                                <th>Last Activity</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {student_rows}
                        </tbody>
                    </table>
                </div>

                <div class="button-row">
                    <a class="btn" href="/hub/home">Back to Home</a>
                    <button class="btn" onclick="location.reload()">Refresh</button>
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


