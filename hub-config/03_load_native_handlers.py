"""Load NativeAuthenticator handlers for admin UI"""
from nativeauthenticator.handlers import (
    AuthorizationAreaHandler,
    ToggleAuthorizationHandler,
    EmailAuthorizationHandler,
    ChangePasswordAdminHandler,
    ChangePasswordHandler,
    SignUpHandler,
    LoginHandler,
    DiscardHandler,
)


def register_handlers(c):
    """Register NativeAuthenticator handlers"""
    if not hasattr(c.JupyterHub, 'extra_handlers') or c.JupyterHub.extra_handlers is None:
        c.JupyterHub.extra_handlers = []
    
    c.JupyterHub.extra_handlers.extend([
        (r'/authorize', AuthorizationAreaHandler),
        (r'/authorize/([^/]*)', ToggleAuthorizationHandler),
        (r'/authorize-email/([^/]*)', EmailAuthorizationHandler),
        (r'/change-password', ChangePasswordHandler),
        (r'/signup', SignUpHandler),
        (r'/login', LoginHandler),
        (r'/discard/([^/]*)', DiscardHandler),
        (r'/change-password-admin/([^/]+)', ChangePasswordAdminHandler),
    ])
    
    print("✓ Loaded NativeAuthenticator handlers for admin UI")


