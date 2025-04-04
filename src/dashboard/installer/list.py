from nicegui import ui
from datetime import datetime
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import InstallerImage
import base64

PLACEHOLDER_IMAGE = 'https://via.placeholder.com/100x100.png?text=No+Image'

@require_permission('upload_images')
def installer_image_list():
    user = get_user()
    session = SessionLocal()
    uploaded_by = user['email'].lower()

    with ui.column().classes('w-full items-center p-8'):
        ui.label(f'🧰 Installer Image Records - {user["email"]}').classes('text-2xl font-bold text-blue-800 mb-6')

        with ui.row().classes('mb-4 gap-4'):
            ui.button('➕ Add New Record', on_click=lambda: ui.navigate.to('/installer/upload')).classes('bg-green-500 text-white px-4 py-2 rounded')
            ui.button('🔄 Refresh', on_click=lambda: ui.navigate.to('/installer/list')).classes('bg-blue-500 text-white px-4 py-2 rounded')

        images = session.query(InstallerImage).filter_by(uploaded_by=uploaded_by).all()
        print(f"Records for {uploaded_by}: {len(images)}")
        for img in images:
            print(f"{img.site_name}, {img.image_name}, {img.qr_text}, {img.gps_lat}, {img.gps_lng}")

        if images:
            for img in images:
                with ui.row().classes('w-full items-center gap-4 mb-2 bg-white shadow-md p-4 rounded'):
                    # Decode binary image data to base64 and embed as data URI
                    if img.image_data:
                        encoded = base64.b64encode(img.image_data).decode('utf-8')
                        image_url = f"data:image/png;base64,{encoded}"
                    else:
                        image_url = PLACEHOLDER_IMAGE

                    ui.image(image_url).classes('w-24 h-24 rounded shadow')

                    # Info block
                    with ui.column().classes('grow'):
                        ui.label(f"📌 Site: {img.site_name}").classes('text-md font-semibold text-blue-900')
                        ui.label(f"🧾 QR: {img.qr_text} | 📍 GPS: {img.gps_lat}, {img.gps_lng}").classes('text-sm text-gray-700')
                        ui.label(f"📂 Image Name: {img.image_name}").classes('text-sm text-gray-600')
                        ui.label(f"📅 Uploaded: {img.uploaded_at.strftime('%Y-%m-%d %H:%M')}").classes('text-xs text-gray-400')

                    # Status & Actions
                    with ui.column().classes('items-end'):
                        ui.label('✅ Approved' if img.approved else '⏳ Pending').classes('text-sm font-bold')
                        with ui.row().classes('gap-2'):
                            ui.button('Edit', on_click=lambda i=img.id: print(f'Edit {i}')).props('outline dense')
                            ui.button('Delete', on_click=lambda i=img.id: print(f'Delete {i}')).props('outline dense')
                            if not img.approved:
                                ui.button('Send for Approval', on_click=lambda i=img.id: print(f'Send {i}')).props('color=primary outline dense')
        else:
            ui.label('No records found. Click "+" to add new image.').classes('text-gray-500')