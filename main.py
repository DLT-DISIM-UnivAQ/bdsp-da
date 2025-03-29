from nicegui import ui
from src.pages.login import login_page
from src.dashboard.engineer import dashboard_engineer
from src.dashboard.installer import dashboard_installer
from src.dashboard.director import dashboard_director
from src.pages.upload import upload_page
from src.pages.nfts import nfts_page
from src.pages.documents import documents_page
from src.auth.auth_roles import get_user, clear_user
import src.auth.auth 
import secrets
secret = secrets.token_urlsafe(32)

# --- PUBLIC PAGE ---
ui.page('/')(login_page)

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
ui.page('/upload')(upload_page)
ui.page('/nfts')(nfts_page)
ui.page('/documents')(documents_page)

# --- RUN APP ---
ui.run(
    title='NICGUI Document Manager',
    port=8081,
    storage_secret=secret
)
