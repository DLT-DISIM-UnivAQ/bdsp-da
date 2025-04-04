# from nicegui import ui
# from datetime import datetime
# from src.auth.auth_roles import require_permission, get_user
# from src.db.database import SessionLocal
# from src.db.models import InstallerImage

# @require_permission('upload_images')
# def installer_image_upload():
#     user = get_user()
#     session = SessionLocal()
#     print("Current user:", user['email'])
#     print("Total images in DB:", session.query(InstallerImage).count())

#     uploads = []
#     upload_grid = ui.column().classes('w-full max-w-4xl mb-4 gap-6')

#     with ui.column().classes('w-full items-center p-8'):
#         ui.label('➕ Upload New Plate Records').classes('text-2xl font-bold text-blue-800 mb-6')

#         def add_image_row():
#             image_data = {'file': None}
#             fields = {
#                 'site_name': ui.input('Site Name').classes('w-full'),
#                 'qr_text': ui.input('QR Text').classes('w-full'),
#                 'gps_lat': ui.input('GPS Latitude').classes('w-full'),
#                 'gps_lng': ui.input('GPS Longitude').classes('w-full'),
#                 'notes': ui.textarea('Notes').classes('w-full'),
#             }

#             row = ui.row().classes('w-full gap-4')

#             def on_upload(e):
#                 image_data['file'] = e
#                 ui.notify(f"File selected: {e.name}", color='primary')

#             ui.upload(on_upload=on_upload, label='Select Image').classes('w-full')

#             def queue_upload():
#                 if not image_data['file']:
#                     ui.notify('Please select an image.', color='negative')
#                     return
#                 uploads.append({
#                     'image_name': image_data['file'].name,
#                     'file': image_data['file'],
#                     'site_name': fields['site_name'].value,
#                     'qr_text': fields['qr_text'].value,
#                     'gps_lat': fields['gps_lat'].value,
#                     'gps_lng': fields['gps_lng'].value,
#                     'notes': fields['notes'].value
#                 })
#                 ui.notify(f"Added {image_data['file'].name} to queue.", color='positive')
#                 upload_grid.clear()

#             ui.button('Add to Queue', on_click=queue_upload).classes('bg-blue-600 text-white px-3 py-1 rounded')

#         ui.button('➕ Add New Image Row', on_click=add_image_row).classes('bg-indigo-500 text-white px-4 py-2 rounded mb-4')

#         def submit_all():
#             if not uploads:
#                 ui.notify('No images queued.', color='warning')
#                 return
#             for item in uploads:
#                 image = InstallerImage(
#                     site_name=item['site_name'],
#                     image_name=item['image_name'],
#                     ipfs_url=None,
#                     uploaded_by=user['email'].lower(),
#                     uploaded_at=datetime.now(),
#                     qr_text=item['qr_text'],
#                     gps_lat=item['gps_lat'],
#                     gps_lng=item['gps_lng'],
#                     notes=item['notes'],
#                     approved=False,
#                 )
#                 session.add(image)
#             session.commit()
#             uploads.clear()
#             ui.notify('✅ All images saved. Redirecting to list...', color='positive')
#             ui.navigate.to('/installer/list')

#         ui.button('Save All & Submit for Approval', on_click=submit_all).classes('bg-green-600 text-white px-6 py-2 rounded')

#         ui.separator().classes('my-4')
#         ui.label('🖼️ Queued Images:').classes('text-blue-700 font-semibold')
#         with upload_grid:
#             pass

from nicegui import ui
from datetime import datetime
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import InstallerImage

@require_permission('upload_images')
def installer_image_upload():
    user = get_user()
    session = SessionLocal()
    print("Current user:", user['email'])
    print("Total images in DB:", session.query(InstallerImage).count())

    uploads = []
    upload_grid = ui.column().classes('w-full max-w-4xl mb-4 gap-6')

    with ui.column().classes('w-full items-center p-8'):
        ui.label('➕ Upload New Plate Records').classes('text-2xl font-bold text-blue-800 mb-6')

        def add_image_row():
            image_data = {'file': None}
            fields = {
                'site_name': ui.input('Site Name').classes('w-full'),
                'qr_text': ui.input('QR Text').classes('w-full'),
                'gps_lat': ui.input('GPS Latitude').classes('w-full'),
                'gps_lng': ui.input('GPS Longitude').classes('w-full'),
                'notes': ui.textarea('Notes').classes('w-full'),
            }

            row = ui.row().classes('w-full gap-4')

            def on_upload(e):
                image_data['file'] = e
                ui.notify(f"File selected: {e.name}", color='primary')

            ui.upload(on_upload=on_upload, label='Select Image').classes('w-full')

            def queue_upload():
                if not image_data['file']:
                    ui.notify('Please select an image.', color='negative')
                    return
                image_bytes = image_data['file'].content.read()
                uploads.append({
                    'image_name': image_data['file'].name,
                    'image_data': image_bytes,
                    'site_name': fields['site_name'].value,
                    'qr_text': fields['qr_text'].value,
                    'gps_lat': fields['gps_lat'].value,
                    'gps_lng': fields['gps_lng'].value,
                    'notes': fields['notes'].value
                })
                ui.notify(f"Added {image_data['file'].name} to queue.", color='positive')
                upload_grid.clear()

            ui.button('Add to Queue', on_click=queue_upload).classes('bg-blue-600 text-white px-3 py-1 rounded')

        ui.button('➕ Add New Image Row', on_click=add_image_row).classes('bg-indigo-500 text-white px-4 py-2 rounded mb-4')

        def submit_all():
            if not uploads:
                ui.notify('No images queued.', color='warning')
                return
            for item in uploads:
                image = InstallerImage(
                    site_name=item['site_name'],
                    image_name=item['image_name'],
                    image_data=item['image_data'],
                    ipfs_url=None,
                    uploaded_by=user['email'].lower(),
                    uploaded_at=datetime.now(),
                    qr_text=item['qr_text'],
                    gps_lat=item['gps_lat'],
                    gps_lng=item['gps_lng'],
                    notes=item['notes'],
                    approved=False,
                )
                session.add(image)
            session.commit()
            uploads.clear()
            ui.notify('✅ All images saved. Redirecting to list...', color='positive')
            ui.navigate.to('/installer/list')

        ui.button('Save All & Submit for Approval', on_click=submit_all).classes('bg-green-600 text-white px-6 py-2 rounded')

        ui.separator().classes('my-4')
        ui.label('🖼️ Queued Images:').classes('text-blue-700 font-semibold')
        with upload_grid:
            pass