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

    def submit_for_approval(image_id: int):
        image = session.query(InstallerImage).filter_by(id=image_id, uploaded_by=uploaded_by).first()
        if image:
            image.submitted = True
            image.approved = False
            image.approved_by = None
            image.approval_time = None
            session.commit()
            ui.notify(f'📤 Image {image_id} submitted for approval.', color='info')
            ui.navigate.to('/installer/list')  # Refresh page

    with ui.column().classes('w-full items-center p-8'):
        ui.label(f'🧰 Installer Image Records - {user["email"]}').classes('text-2xl font-bold text-blue-800 mb-6')

        with ui.row().classes('mb-4 gap-4'):
            ui.button('➕ Add New Record', on_click=lambda: ui.navigate.to('/installer/upload')).classes('bg-green-500 text-white px-4 py-2 rounded')
            ui.button('🔄 Refresh', on_click=lambda: ui.navigate.to('/installer/list')).classes('bg-blue-500 text-white px-4 py-2 rounded')
            ui.button('🏠 Back to Dashboard', on_click=lambda: ui.navigate.to('/dashboard/installer')).classes('bg-gray-600 text-white px-4 py-2 rounded')

        images = session.query(InstallerImage).filter_by(uploaded_by=uploaded_by).order_by(InstallerImage.uploaded_at.desc()).all()

        if images:
            for img in images:
                with ui.row().classes('w-full items-center gap-4 mb-2 bg-white shadow-md p-4 rounded'):
                    # 🔹 Image preview
                    if img.image_data:
                        encoded = base64.b64encode(img.image_data).decode('utf-8')
                        image_url = f"data:image/png;base64,{encoded}"
                    else:
                        image_url = PLACEHOLDER_IMAGE
                    ui.image(image_url).classes('w-24 h-24 rounded shadow')

                    # 🔹 Image Details
                    with ui.column().classes('grow'):
                        ui.label(f"📌 Site: {img.site_name}").classes('text-md font-semibold text-blue-900')
                        ui.label(f"🧾 QR: {img.qr_text} | 📍 GPS: {img.gps_lat}, {img.gps_lng}").classes('text-sm text-gray-700')
                        ui.label(f"📂 Image Name: {img.image_name}").classes('text-sm text-gray-600')
                        ui.label(f"📅 Uploaded: {img.uploaded_at.strftime('%Y-%m-%d %H:%M')}").classes('text-xs text-gray-400')

                    # 🔹 Status & Actions
                    with ui.column().classes('items-end'):
                        # Status display
                        if img.approved:
                            ui.label('✅ Approved by Director').classes('text-sm font-bold text-green-600')
                        elif img.submitted:
                            ui.label('📤 Submitted').classes('text-sm font-bold text-blue-600')
                        else:
                            ui.label('⏳ Pending').classes('text-sm font-bold text-yellow-600')

                        # Action buttons
                        with ui.row().classes('gap-2'):
                            disabled = img.submitted or img.approved
                            ui.button('Edit', on_click=lambda i=img.id: print(f'Edit {i}')).props(f'outline dense{" disable" if disabled else ""}')
                            ui.button('Delete', on_click=lambda i=img.id: print(f'Delete {i}')).props(f'outline dense{" disable" if disabled else ""}')

                            if not img.submitted and not img.approved:
                                ui.button('Send for Approval', on_click=lambda i=img.id: submit_for_approval(i)).props('color=primary outline dense')
                            elif img.submitted and not img.approved:
                                ui.button('Waiting...').props('flat dense disable')
        else:
            ui.label('No records found. Click "+" to add new image.').classes('text-gray-500')
