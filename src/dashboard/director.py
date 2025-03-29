from nicegui import ui
from src.auth.auth_roles import clear_user, get_user

def dashboard_director():
    user = get_user()
    print('[DEBUG] user from storage:', user)  # 🐛 Log user info to console

    if not user or user.get("role") != "director":
        print('[DEBUG] Access denied or no user found. Redirecting...')
        clear_user()
        ui.navigate.to('/')
        return

    ui.label(f"🧑‍⚖️ Director of Works Dashboard - {user['email']}").classes("text-2xl font-bold text-purple-800 mt-4")
    ui.label("You can approve or reject documents and images, and mint NFTs").classes("text-md text-purple-600 mb-6")

    ui.button("Review Submissions", on_click=lambda: ui.navigate.to("/review")).classes("bg-indigo-600 text-white px-4 py-2 rounded-xl")
    ui.button("Mint NFTs", on_click=lambda: ui.navigate.to("/mint")).classes("bg-purple-700 text-white px-4 py-2 rounded-xl ml-2")
