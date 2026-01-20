"""Install NativeAuthenticator package at hub startup"""
import subprocess
import sys

try:
    import nativeauthenticator
    print("NativeAuthenticator already installed")
except ImportError:
    print("Installing jupyterhub-nativeauthenticator...")
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', 
        'jupyterhub-nativeauthenticator==1.2.0'
    ])
    print("NativeAuthenticator installed successfully")


