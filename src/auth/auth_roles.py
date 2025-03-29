# src/auth/roles_auth.py
from nicegui import ui, app

PERMISSIONS = {
    'engineer': ['upload_docs', 'edit_docs', 'delete_docs', 'submit_to_admin'],
    'installer': ['upload_images', 'edit_images', 'delete_images', 'submit_to_admin'],
    'director': ['approve_docs', 'approve_images', 'mint_nft']
}

ROLES = ['engineer', 'installer', 'director']

def get_user():
    user = app.storage.user
    print('[DEBUG:get_user] Raw storage content:', user)

    if isinstance(user, dict) and user.get('role') in ROLES:
        return user
    return None


def clear_user():
    app.storage.user.clear()

def has_permission(permission):
    user = get_user()
    if not user:
        return False
    return permission in PERMISSIONS.get(user.get('role'), [])

from functools import wraps

def require_permission(permission):
    def decorator(func):
        @wraps(func)  # ✅ Preserve metadata and function signature
        def wrapper(*args, **kwargs):
            user = get_user()
            if not user or permission not in PERMISSIONS.get(user.get('role'), []):
                clear_user()
                ui.notify('Access denied: insufficient permission', color='negative')
                ui.navigate.to('/')
                return
            return func(*args, **kwargs)
        return wrapper
    return decorator
