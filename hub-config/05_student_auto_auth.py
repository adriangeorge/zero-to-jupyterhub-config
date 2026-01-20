"""Student auto-authorization hook"""
from nativeauthenticator.orm import UserInfo as NativeUserInfo


async def student_post_auth_hook(authenticator, handler, authentication):
    """Auto-authorize students with @stud.acs.pub.ro emails"""
    if authentication is None:
        return None
    
    username = authentication['name']
    
    if username in ['admin', 'prof_smith', 'prof_jones', 'prof_doe']:
        return authentication
    
    user_info = handler.db.query(NativeUserInfo).filter_by(username=username).first()
    
    if user_info and user_info.email:
        if user_info.email.endswith('@stud.acs.pub.ro'):
            if not user_info.is_authorized:
                user_info.is_authorized = True
                handler.db.commit()
                print(f"Auto-authorized student: {username}")
    
    return authentication


def configure_auth_hook(c):
    """Configure the post-authentication hook"""
    c.NativeAuthenticator.post_auth_hook = student_post_auth_hook
    print("✓ Student auto-authorization hook configured")


