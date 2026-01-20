#!/usr/bin/env python3
"""
Setup script for static users (admin and teachers)
Creates accounts in NativeAuthenticator database
MUST BE RUN INSIDE THE HUB POD
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from nativeauthenticator.orm import UserInfo
from jupyterhub import orm
import bcrypt
import os

# Static user credentials
STATIC_USERS = {
    'admin': {
        'email': 'admin@acs.pub.ro',
        'password': 'admin123',
        'is_admin': True
    },
    'prof_smith': {
        'email': 'smith@teacher.acs.pub.ro',
        'password': 'teacher123',
        'is_admin': False
    },
    'prof_jones': {
        'email': 'jones@teacher.acs.pub.ro',
        'password': 'teacher123',
        'is_admin': False
    },
    'prof_doe': {
        'email': 'doe@teacher.acs.pub.ro',
        'password': 'teacher123',
        'is_admin': False
    }
}

db_url = os.environ.get('JUPYTERHUB_DATABASE_URL', 'sqlite:////srv/jupyterhub/jupyterhub.sqlite')
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 60)
print("Setting up static users (admin and teachers)")
print("=" * 60)
print()

for username, info in STATIC_USERS.items():
    # 1. Create/Update JupyterHub user
    jh_user = session.query(orm.User).filter_by(name=username).first()
    if not jh_user:
        jh_user = orm.User(name=username, admin=info['is_admin'])
        session.add(jh_user)
        print(f"✓ Created JupyterHub user '{username}'")
    else:
        jh_user.admin = info['is_admin']
        print(f"✓ Updated JupyterHub user '{username}'")
    
    # 2. Create/Update NativeAuthenticator credentials
    user_info = session.query(UserInfo).filter_by(username=username).first()
    
    if user_info:
        print(f"  → NativeAuth credentials exist")
        user_info.is_authorized = True
    else:
        # Hash password using bcrypt (NativeAuthenticator's method)
        password_bytes = bcrypt.hashpw(info['password'].encode('utf-8'), bcrypt.gensalt())
        
        user_info = UserInfo(
            username=username,
            email=info['email'],
            password=password_bytes,
            is_authorized=True
        )
        session.add(user_info)
        print(f"  → Created NativeAuth credentials")
        print(f"     Email: {info['email']}")
        print(f"     Password: {info['password']}")
    
    session.commit()

print()
print("=" * 60)
print("Static users setup complete!")
print("=" * 60)
print()
print("Login credentials:")
print("-" * 60)
for username, info in STATIC_USERS.items():
    role = "Admin" if info['is_admin'] else "Teacher"
    print(f"{role:10} | Username: {username:15} | Password: {info['password']}")
print()
print("⚠️  IMPORTANT: Change these passwords in production!")
print()

session.close()



