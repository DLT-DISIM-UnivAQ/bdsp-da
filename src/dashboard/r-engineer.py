from nicegui import ui
from src.auth.auth_roles import require_permission, get_user

@require_permission('upload_docs')
def dashboard_engineer():
    user = get_user()

    ui.label(f"👷 Engineer Dashboard - {user['email']}").classes("text-2xl font-bold text-blue-800 mt-4")
    ui.label("You can upload, edit, delete, and submit documents").classes("text-md text-blue-600 mb-6")

    ui.button("Upload Documents", on_click=lambda: ui.navigate.to("/upload")).classes("bg-green-500 text-white px-4 py-2 rounded-xl")
    ui.button("View Documents", on_click=lambda: ui.navigate.to("/documents")).classes("bg-blue-500 text-white px-4 py-2 rounded-xl ml-2")
