from nicegui import ui, app

ROLES = ['engineer', 'installer', 'director']

PERMISSIONS = {
    'engineer': [
        'dashboard_overview',
        'document_submission',
        'document_upload',
        'document_validation',
        'dwg_viewer',
        'project_management'
    ],
    'installer': ['upload_images', 'edit_images', 'delete_images', 'submit_to_admin'],
    'director': ['approve_docs', 'approve_images', 'mint_nft']
}

def get_user():
    user = app.storage.user
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
        @wraps(func)
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
