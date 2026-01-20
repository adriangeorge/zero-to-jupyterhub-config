"""Student enrollment page to select a class once"""
from jupyterhub.handlers import BaseHandler
from jupyterhub import orm
from tornado import web


CLASS_OPTIONS = [
    ("prof-smith-class", "teacher-prof-smith", "Prof. Smith's Class"),
    ("prof-jones-class", "teacher-prof-jones", "Prof. Jones's Class"),
    ("prof-doe-class", "teacher-prof-doe", "Prof. Doe's Class"),
]


class StudentEnrollmentHandler(BaseHandler):
    """Allow students to enroll in exactly one class"""

    @web.authenticated
    async def get(self):
        user = self.current_user
        user_groups = {g.name for g in user.groups}

        if user.admin or "teachers" in user_groups:
            self.redirect("/hub/home")
            return

        enrolled_group = next((g for g in user_groups if g.startswith("teacher-prof-")), None)

        if enrolled_group:
            enrolled_label = enrolled_group.replace("teacher-prof-", "Prof. ").replace("-", " ").title()
            alert_html = f"""
            <div class="alert alert-warning" role="alert" style="margin-top: 15px;">
                You are already enrolled in <strong>{enrolled_label}</strong>.
                Please ask an admin to remove you from this class if you need to switch.
            </div>
            """
            options_html = ""
            submit_html = '<div class="button-row"><a href="/hub/home" class="btn btn-primary">Back to Home</a></div>'
        else:
            alert_html = ""
            options_html = "\n".join(
                f"""
                <div class="form-check" style="margin-bottom: 10px;">
                    <label class="form-check-label">
                        <input class="form-check-input" type="radio" name="class_slug" value="{slug}" required />
                        <strong>{label}</strong> — Enroll once and keep access
                    </label>
                </div>
                """
                for slug, _group, label in CLASS_OPTIONS
            )
            submit_html = """
            <div class="button-row">
                <button type="submit" class="btn btn-primary">Enroll</button>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Choose Your Class</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="/hub/static/css/style.min.css" type="text/css" />
            <style>
                body {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                }}
                .card-panel {{
                    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
                    border-radius: 20px;
                    padding: 32px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.25), 0 0 0 1px rgba(255,255,255,0.1);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                    max-width: 600px;
                    margin: 0 auto;
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
                    min-width: 200px;
                    padding: 14px 28px;
                    font-size: 16px;
                    font-weight: 700;
                    border-radius: 12px;
                    border: none;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #fff;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    cursor: pointer;
                }}
                .button-row .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
                    text-decoration: none;
                    color: #fff;
                }}
                .form-check {{
                    background: rgba(102, 126, 234, 0.05);
                    border: 2px solid #e0e0e0;
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 16px;
                    transition: all 0.3s ease;
                }}
                .form-check:hover {{
                    border-color: #667eea;
                    background: rgba(102, 126, 234, 0.1);
                    transform: translateX(4px);
                }}
                .form-check-label {{
                    font-size: 15px;
                    font-weight: 500;
                    cursor: pointer;
                }}
                .form-check-input {{
                    width: 20px;
                    height: 20px;
                    margin-right: 12px;
                    cursor: pointer;
                }}
                .alert {{
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 20px;
                    font-weight: 600;
                    border: 2px solid;
                }}
                .alert-warning {{
                    background: #fff3cd;
                    border-color: #ffc107;
                    color: #856404;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="page-title">Class Enrollment</h1>
                <p class="page-subtitle">Choose your class for this semester. You can enroll once and keep access throughout the term.</p>
                <div class="card-panel">
                    {alert_html}
                    <form method="post" action="/hub/enroll">
                        <input type="hidden" name="_xsrf" value="{self.xsrf_token.decode('utf-8')}" />
                        <div class="form-group">
                            {options_html}
                        </div>
                        {submit_html}
                    </form>
                </div>
            </div>
        </body>
        </html>
        """
        self.finish(html)

    @web.authenticated
    async def post(self):
        user = self.current_user
        user_groups = {g.name for g in user.groups}

        if user.admin or "teachers" in user_groups:
            self.redirect("/hub/home")
            return
        
        # Check if already enrolled
        if any(g.startswith("teacher-prof-") for g in user_groups):
            self.redirect("/hub/enroll")
            return

        selected_slug = self.get_body_argument("class_slug", default=None)
        if not selected_slug:
            self.set_status(400)
            self.write("<h1>Missing selection</h1><p>Please choose a class.</p>")
            return

        slug_to_group = {slug: group for slug, group, _label in CLASS_OPTIONS}
        target_group = slug_to_group.get(selected_slug)
        if not target_group:
            self.set_status(400)
            self.write("<h1>Invalid selection</h1><p>Please choose a valid class.</p>")
            return

        group = self.db.query(orm.Group).filter_by(name=target_group).first()
        if group:
            group.users.append(user.orm_user)
            self.db.commit()

        self.redirect("/hub/home")


def register_handler(c):
    """Register the student enrollment handler"""
    if not hasattr(c.JupyterHub, "extra_handlers") or c.JupyterHub.extra_handlers is None:
        c.JupyterHub.extra_handlers = []

    c.JupyterHub.extra_handlers.append((r"/enroll", StudentEnrollmentHandler))
    print("✓ Student enrollment available at: /hub/enroll")
