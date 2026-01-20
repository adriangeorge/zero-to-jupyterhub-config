"""Custom admin panel override"""
from jupyterhub.handlers import BaseHandler
from jupyterhub import orm
from tornado import web


class CustomAdminPanelHandler(BaseHandler):
    """Custom admin panel with styled interface"""
    
    @web.authenticated
    async def get(self):
        """Show custom admin panel"""
        user = self.current_user
        
        if not user.admin:
            self.set_status(403)
            self.write("<h1>Access Denied</h1><p>This page is for administrators only.</p>")
            return
        
        # Get statistics
        all_users = self.db.query(orm.User).all()
        total_users = len(all_users)
        
        # Count active servers
        active_servers = 0
        for u in all_users:
            spawners = self.db.query(orm.Spawner).filter_by(user_id=u.id).all()
            if any(s.server is not None for s in spawners):
                active_servers += 1
        
        # Get all groups
        all_groups = self.db.query(orm.Group).all()
        
        # Build detailed group list HTML with member names
        group_rows = ""
        teacher_names = {'admin', 'prof_smith', 'prof_jones', 'prof_doe'}
        
        for group in all_groups:
            if group.name in ['admins', 'teachers'] or group.name.startswith('teacher-prof-'):
                member_count = len(group.users)
                student_count = sum(1 for u in group.users if u.name not in teacher_names)
                group_display = group.name.replace('teacher-prof-', 'Prof. ').replace('-', ' ').title()
                
                # List all members
                member_list = ', '.join([u.name for u in group.users[:10]])
                if len(group.users) > 10:
                    member_list += f' and {len(group.users) - 10} more'
                if not member_list:
                    member_list = '<em style="color: #999;">No members</em>'
                
                # Group type badge
                if group.name == 'admins':
                    badge = '<span style="background: #dc3545; color: white; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;">ADMIN</span>'
                elif group.name == 'teachers':
                    badge = '<span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;">TEACHER</span>'
                else:
                    badge = '<span style="background: #17a2b8; color: white; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;">CLASS</span>'
                
                group_rows += f"""
                <tr>
                    <td>
                        <strong>{group_display}</strong><br/>
                        <small style="color: #666;">{group.name}</small>
                    </td>
                    <td>{badge}</td>
                    <td style="text-align: center;">{member_count}</td>
                    <td style="text-align: center;">{student_count}</td>
                    <td style="font-size: 13px; color: #555;">{member_list}</td>
                    <td style="text-align: center;">
                        <a href="/hub/admin#/groups/{group.name}" class="btn-xs">View Details</a>
                    </td>
                </tr>
                """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Panel</title>
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
                .card-panel {{
                    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
                    border-radius: 20px;
                    padding: 32px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.25), 0 0 0 1px rgba(255,255,255,0.1);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                    margin-bottom: 24px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 32px;
                }}
                .stat-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 24px;
                    border-radius: 16px;
                    text-align: center;
                    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
                }}
                .stat-number {{
                    font-size: 2.5em;
                    font-weight: 800;
                    margin: 8px 0;
                }}
                .stat-label {{
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    opacity: 0.9;
                }}
                .quick-links {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 16px;
                    margin-top: 24px;
                }}
                .quick-link {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 15px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                }}
                .quick-link:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
                    text-decoration: none;
                    color: white;
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
                }}
                .btn-xs {{
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 600;
                    border-radius: 8px;
                    border: none;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #fff;
                    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                    transition: all 0.3s ease;
                    text-transform: uppercase;
                    letter-spacing: 0.3px;
                    text-decoration: none;
                    display: inline-block;
                }}
                .btn-xs:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                    text-decoration: none;
                    color: #fff;
                }}
                .button-row {{
                    text-align: center;
                    margin-top: 24px;
                }}
                .btn {{
                    min-width: 180px;
                    padding: 14px 28px;
                    font-size: 15px;
                    font-weight: 600;
                    border-radius: 12px;
                    border: none;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #fff;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                    transition: all 0.3s ease;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    cursor: pointer;
                }}
                .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
                    text-decoration: none;
                    color: #fff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="page-title">Admin Panel</h1>
                <p class="page-subtitle">System Overview and Management</p>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Total Users</div>
                        <div class="stat-number">{total_users}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Active Servers</div>
                        <div class="stat-number">{active_servers}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Groups</div>
                        <div class="stat-number">{len([g for g in all_groups if g.name in ['admins', 'teachers'] or g.name.startswith('teacher-prof-')])}</div>
                    </div>
                </div>

                <div class="card-panel">
                    <h3 style="margin-top: 0; color: #667eea; font-size: 1.3em; font-weight: 700;">Quick Actions</h3>
                    <div class="quick-links">
                        <a href="/hub/authorize" class="quick-link">Manage Users</a>
                        <a href="/hub/manage-groups" class="quick-link">Manage Groups</a>
                        <a href="/hub/token" class="quick-link">API Tokens</a>
                        <a href="/hub/admin" class="quick-link">Default Admin Panel</a>
                    </div>
                </div>

                <div class="card-panel">
                    <h3 style="margin-top: 0; color: #667eea; font-size: 1.3em; font-weight: 700;">Groups Management</h3>
                    <p style="color: #666; margin-bottom: 20px;">View and manage user groups. Click "View Details" to add/remove members in the default admin panel.</p>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Group Name</th>
                                <th>Type</th>
                                <th style="text-align: center;">Total Members</th>
                                <th style="text-align: center;">Students</th>
                                <th>Member List</th>
                                <th style="text-align: center;">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {group_rows}
                        </tbody>
                    </table>
                </div>

                <div class="button-row">
                    <a class="btn" href="/hub/home">Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        self.finish(html)


def register_handler(c):
    """Register the custom admin panel handler"""
    if not hasattr(c.JupyterHub, 'extra_handlers') or c.JupyterHub.extra_handlers is None:
        c.JupyterHub.extra_handlers = []
    
    # Override /hub/admin with custom panel
    c.JupyterHub.extra_handlers.append((r'/admin-panel', CustomAdminPanelHandler))
    print("✓ Custom admin panel available at: /hub/admin-panel")
