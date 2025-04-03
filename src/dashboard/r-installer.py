from nicegui import ui
from src.auth.auth_roles import require_permission, get_user

@require_permission('upload_images')
def dashboard_installer():
    user = get_user()

    ui.label(f"🔧 Installer Dashboard - {user['email']}").classes("text-2xl font-bold text-green-800 mt-4")
    ui.label("You can upload, edit, delete images and submit to administrator").classes("text-md text-green-600 mb-6")

    ui.button("Upload Images", on_click=lambda: ui.navigate.to("/upload_images")).classes("bg-green-600 text-white px-4 py-2 rounded-xl")
    ui.button("View Images", on_click=lambda: ui.navigate.to("/images")).classes("bg-blue-500 text-white px-4 py-2 rounded-xl ml-2")
