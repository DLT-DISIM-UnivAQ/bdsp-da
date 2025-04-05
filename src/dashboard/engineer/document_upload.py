from nicegui import ui
from datetime import datetime
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import EngineerDocument
import os, uuid, requests
from sqlalchemy.exc import SQLAlchemyError

# IPFS Config (can be moved to .env)
PINATA_JWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIwN2QzZTM1NS1hMWE2LTQwMDktOWFhOC02NmEzODk0ZmQ2ZDQiLCJlbWFpbCI6ImFzaWZzYWVlZC5jc3BAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjQ0ZDQ2NTMzN2NhMDY1MjRkMjE5Iiwic2NvcGVkS2V5U2VjcmV0IjoiNzdiOWY5ZDgwMTQ1MzJhNjUzZTJmNjAzYThkZTAxYjc2NGJkMzhkYjhlNTFlY2IzNmJlYjFkOTQ0MmVlMDNkNCIsImV4cCI6MTc3NTA2NDYxOH0.JQXAqSzpQP2N9MaFjJhGmAqE7koaaVlugYcRFE-knFk'
PINATA_UPLOAD_URL = 'https://api.pinata.cloud/pinning/pinFileToIPFS'

def upload_file_to_ipfs_bytes(file_bytes, name):
    headers = {'Authorization': f'Bearer {PINATA_JWT}'}
    files = {'file': (name, file_bytes, 'application/octet-stream')}
    response = requests.post(PINATA_UPLOAD_URL, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()['IpfsHash']
    else:
        raise Exception(f"Failed IPFS upload: {response.text}")

@require_permission('upload_documents')
def engineer_document_upload():
    user = get_user()
    session = SessionLocal()
    uploads = []
    upload_grid = ui.column().classes('w-full max-w-4xl mb-4 gap-6')

    with ui.column().classes('w-full items-center p-8'):
        ui.label('📤 Upload Engineering Documents').classes('text-2xl font-bold text-blue-800 mb-6')
        ui.button('⬅️ Back to Dashboard', on_click=lambda: ui.navigate.to('/dashboard/engineer')).classes('mb-4 bg-gray-200 px-4 py-2 rounded')
        def add_upload_row():
            file_data = {'file': None}
            fields = {
                'project_name': ui.input('Project Name').classes('w-full'),
                'document_name': ui.input('Document Name').classes('w-full'),
                'description': ui.textarea('Description').classes('w-full'),
            }

            ui.upload(label='📎 Choose File', on_upload=lambda e: file_data.update({'file': e})).classes('w-full')

            def add_to_queue():
                if not file_data['file']:
                    ui.notify('Please select a file.', color='negative')
                    return
                uploads.append({
                    'file': file_data['file'],
                    'project_name': fields['project_name'].value,
                    'document_name': fields['document_name'].value,
                    'description': fields['description'].value,
                })
                ui.notify(f"✅ Added {file_data['file'].name} to queue.", color='positive')
                upload_grid.clear()

            ui.button('Add to Queue', on_click=add_to_queue).classes('bg-blue-500 text-white px-4 py-2 rounded')

        ui.button('➕ Add New Upload Field', on_click=add_upload_row).classes('bg-green-600 text-white px-4 py-2 rounded mb-4')

        def submit_all():
            if not uploads:
                ui.notify('❗ No files in the queue.', color='warning')
                return
            try:
                for item in uploads:
                    file = item['file']
                    file.content.seek(0)
                    ipfs_hash = upload_file_to_ipfs_bytes(file.content.read(), file.name)
                    ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"

                    new_doc = EngineerDocument(
                        project_name=item['project_name'],
                        document_name=item['document_name'],
                        description=item['description'],
                        ipfs_url=ipfs_url,
                        token_uri=None,
                        uploaded_by=user['email'],
                        uploaded_at=datetime.utcnow(),
                    )
                    session.add(new_doc)
                session.commit()
                uploads.clear()
                ui.notify('✅ Documents uploaded to DB & IPFS successfully.', color='positive')
                ui.navigate.to('/engineer/list')
            except SQLAlchemyError as e:
                session.rollback()
                ui.notify(f'❌ DB Error: {str(e)}', color='negative')
            except Exception as e:
                ui.notify(f'❌ IPFS Error: {str(e)}', color='negative')

        ui.button('💾 Save All Documents', on_click=submit_all).classes('bg-green-700 text-white px-6 py-2 rounded')
        with upload_grid:
            pass
