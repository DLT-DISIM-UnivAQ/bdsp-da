from nicegui import ui
from datetime import datetime
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import InstallerImage
from PIL import Image, ExifTags
from pyzbar.pyzbar import decode
from io import BytesIO

@require_permission('upload_images')
def installer_image_upload():
    user = get_user()
    session = SessionLocal()
    uploads = []
    upload_grid = ui.column().classes('w-full max-w-4xl mb-4 gap-6')

    ui.label('➕ Upload New Plate Records').classes('text-2xl font-bold text-blue-800 mb-6')
    ui.button('🔄 List', on_click=lambda: ui.navigate.to('/installer/list')).classes('bg-blue-500 text-white px-4 py-2 rounded')
    ui.button('🏠 Back to Dashboard', on_click=lambda: ui.navigate.to('/dashboard/installer')).classes('bg-gray-600 text-white px-4 py-2 rounded')

    def get_exif_data(image):
        try:
            exif_data = image._getexif()
            if not exif_data:
                return {}
            return {ExifTags.TAGS.get(k): v for k, v in exif_data.items() if k in ExifTags.TAGS}
        except Exception as e:
            print("EXIF Error:", e)
            return {}

    def convert_dms(dms, ref):
        try:
            # Handles both rational tuples and floats
            def rational_to_float(r):
                if isinstance(r, tuple):
                    return r[0] / r[1]
                elif hasattr(r, 'numerator') and hasattr(r, 'denominator'):
                    return float(r.numerator) / float(r.denominator)
                else:
                    return float(r)

            d = rational_to_float(dms[0])
            m = rational_to_float(dms[1])
            s = rational_to_float(dms[2])

            decimal = d + (m / 60.0) + (s / 3600.0)
            if ref in ['S', 'W']:
                decimal = -decimal
            return round(decimal, 6)
        except Exception as e:
            print(f"⚠️ DMS conversion failed: {e}")
            return None

    def extract_gps(file_bytes):
        try:
            image = Image.open(BytesIO(file_bytes))
            exif = get_exif_data(image)
            gps_info = exif.get("GPSInfo")
            if not gps_info:
                return None, None

            gps_data = {}
            for key, val in gps_info.items():
                decoded = ExifTags.GPSTAGS.get(key, key)
                gps_data[decoded] = val

            lat = convert_dms(gps_data.get("GPSLatitude"), gps_data.get("GPSLatitudeRef"))
            lon = convert_dms(gps_data.get("GPSLongitude"), gps_data.get("GPSLongitudeRef"))
            return str(lat) if lat else None, str(lon) if lon else None
        except Exception as e:
            print("EXIF GPS parse error:", e)
            return None, None

    def extract_qr(file_bytes):
        try:
            image = Image.open(BytesIO(file_bytes))
            decoded = decode(image)
            if decoded:
                return decoded[0].data.decode('utf-8')
        except Exception as e:
            print("QR error:", e)
        return ""

    def add_image_row():
        image_data = {'file': None, 'bytes': None}
        fields = {
            'site_name': ui.input('Site Name').classes('w-full'),
            'qr_text': ui.input('QR Text').classes('w-full'),
            'gps_lat': ui.input('GPS Latitude').classes('w-full'),
            'gps_lng': ui.input('GPS Longitude').classes('w-full'),
            'notes': ui.textarea('Notes').classes('w-full'),
        }

        def on_upload(e):
            image_data['file'] = e
            image_bytes = e.content.read()
            image_data['bytes'] = image_bytes

            gps_lat, gps_lng = extract_gps(image_bytes)
            qr_text = extract_qr(image_bytes)

            if gps_lat:
                fields['gps_lat'].value = gps_lat
            if gps_lng:
                fields['gps_lng'].value = gps_lng
            if qr_text:
                fields['qr_text'].value = qr_text

            ui.notify(f"📸 Uploaded: {e.name}", color='info')

        ui.upload(on_upload=on_upload, label='Select Image').classes('w-full')

        def queue_upload():
            if not image_data['file'] or not image_data['bytes']:
                ui.notify('Please select a valid image.', color='negative')
                return
            uploads.append({
                'image_name': image_data['file'].name,
                'image_data': image_data['bytes'],
                'site_name': fields['site_name'].value,
                'qr_text': fields['qr_text'].value,
                'gps_lat': fields['gps_lat'].value,
                'gps_lng': fields['gps_lng'].value,
                'notes': fields['notes'].value,
            })
            ui.notify(f"✅ Queued: {image_data['file'].name}", color='positive')
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
