from nicegui import ui
from src.pages.login import login_page
from src.dashboard.installer.installer_dashboard import dashboard_installer
from src.dashboard.installer.list import installer_image_list
from src.dashboard.installer.upload import installer_image_upload
from src.pages.nfts import nfts_page
from src.pages.documents import documents_page
from src.auth.auth_roles import get_user, clear_user
from src.dashboard.engineer.dashboard_overview import dashboard_engineer  
from src.dashboard.engineer.document_upload import document_upload
from src.dashboard.director.director_dashboard import director_dashboard
from src.dashboard.director.director_approval import director_approval
from src.dashboard.director.director_history import director_mint_history


import src.auth.auth 
import secrets
secret = secrets.token_urlsafe(32)

# from src.db.database import init_db
# init_db()

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
    if user and user.get('role') == 'director':
        director_dashboard()
    else:
        ui.notify('Access denied')

@ui.page('/director/approval')
def render_director_approval():
    user = get_user()
    if user and user.get('role') == 'director':
        director_approval()
    else:
        ui.notify('Access denied')

@ui.page('/director/history')
def render_director_history():
    user = get_user()
    if user and user.get('role') == 'director':
        director_mint_history()
    else:
        ui.notify('Access denied')


# --- SHARED OR RESTRICTED PAGES ---

ui.page('/nfts')(nfts_page)
ui.page('/documents')(documents_page)

# --- RUN APP ---

ui.run(
    title='NICGUI Document Manager',
    port=8081,
    storage_secret=secret
)
