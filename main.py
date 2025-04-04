from nicegui import ui
from src.pages.login import login_page
# from src.dashboard.engineer import dashboard_engineer
from src.dashboard.installer.installer_dashboard import dashboard_installer
from src.dashboard.installer.list import installer_image_list
from src.dashboard.installer.upload import installer_image_upload
from src.dashboard.director import dashboard_director
from src.pages.nfts import nfts_page
from src.pages.documents import documents_page
from src.auth.auth_roles import get_user, clear_user
from src.dashboard.engineer.dashboard_overview import dashboard_engineer  
from src.dashboard.engineer.document_upload import document_upload


import src.auth.auth 
import secrets
secret = secrets.token_urlsafe(32)

from src.db.database import init_db
init_db()

# --- PUBLIC PAGE ---
ui.page('/')(login_page)
ui.page('/upload')(document_upload)

# --- ROLE-SPECIFIC DASHBOARDS ---
@ui.page('/dashboard/engineer')
def render_engineer_dashboard():
    user = get_user()
    if user and user.get('role') == 'engineer':
        dashboard_engineer()

    else:
        clear_user()
        ui.navigate.to('/')

@ui.page('/dashboard/installer')
def render_installer_dashboard():
    user = get_user()
    if user and user.get('role') == 'installer':
        dashboard_installer()
    else:
        clear_user()
        ui.navigate.to('/')

@ui.page('/installer/list')
def render_installer_list():
    user = get_user()
    if user and user.get('role') == 'installer':
        installer_image_list()
    else:
        clear_user()
        ui.navigate.to('/')

@ui.page('/installer/upload')
def render_installer_list():
    user = get_user()
    if user and user.get('role') == 'installer':
        installer_image_upload()
    else:
        clear_user()
        ui.navigate.to('/')


@ui.page('/dashboard/director')
def render_director_dashboard():
    user = get_user()
    print('[DEBUG] Visiting /dashboard/director')
    print('[DEBUG] Retrieved user:', user)

    if user and user.get('role') == 'director':
        print('[DEBUG] Access granted to director dashboard.')
        dashboard_director()
    else:
        print('[DEBUG] Access denied or invalid role. Redirecting to login.')
        clear_user()
        ui.navigate.to('/')

# --- SHARED OR RESTRICTED PAGES ---

ui.page('/nfts')(nfts_page)
ui.page('/documents')(documents_page)

# --- RUN APP ---

ui.run(
    title='NICGUI Document Manager',
    port=8081,
    storage_secret=secret
)
