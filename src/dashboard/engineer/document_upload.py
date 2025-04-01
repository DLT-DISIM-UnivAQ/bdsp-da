from nicegui import ui
from src.auth.auth_roles import require_permission, get_user
import uuid
import json
import requests
from datetime import datetime
import os

STORAGE_KEY = 'uploaded_documents'
PINATA_JWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIwN2QzZTM1NS1hMWE2LTQwMDktOWFhOC02NmEzODk0ZmQ2ZDQiLCJlbWFpbCI6ImFzaWZzYWVlZC5jc3BAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6ImM5NjZlNGE3ZWI2NGYwOThiNDQwIiwic2NvcGVkS2V5U2VjcmV0IjoiZjE1MjU0NjFiYTQ1YjA1NTRhNDk0NmQ2NWRiYWRmYzgxNTEyNzk5ODhhNjUwNzhhYWQzNWNmZDMyOTg0YThhZCIsImV4cCI6MTc3NDk1NTA0MX0.0_e_eVPL_TPiiXrd4wyF0rQ0fUvllMezbaLPREuLwXw'  # Replace with full JWT
PINATA_UPLOAD_URL = 'https://api.pinata.cloud/pinning/pinFileToIPFS'

DOCUMENTS_FILE = 'uploaded_documents.json'

def load_documents():
    if not os.path.exists(DOCUMENTS_FILE):
        return []
    with open(DOCUMENTS_FILE, 'r') as f:
        return json.load(f)

def save_documents(documents):
    with open(DOCUMENTS_FILE, 'w') as f:
        json.dump(documents, f, indent=2)

def upload_to_ipfs(file_obj):
    headers = {
        'Authorization': f'Bearer {PINATA_JWT}',
    }

    files = {
        'file': (file_obj.name, file_obj.content.read(), file_obj.type),
    }

    response = requests.post(PINATA_UPLOAD_URL, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()['IpfsHash']
    else:
        raise Exception(f"Failed to upload to IPFS: {response.text}")

@require_permission('document_upload')
def document_upload():
    user = get_user()
    uploaded_file = {'file': None}  # Wrapper to allow modification from inner scope

    with ui.column().classes('w-full items-center p-8'):
        ui.label('📤 Upload Project Document').classes('text-2xl font-bold text-blue-900 mb-4')
        ui.label(f"Logged in as: {user['email']}").classes("text-sm text-blue-600 mb-4")

        doc = {
            'project_name': ui.input('Project Name').classes('w-full mb-2'),
            'document_name': ui.input('Document Name').classes('w-full mb-2'),
            'tags': ui.input('Tags (comma separated)').classes('w-full mb-2'),
            'description': ui.textarea('Description').classes('w-full mb-4'),
        }

        def on_file_upload(e):
            uploaded_file['file'] = e
            ui.notify(f"Selected file: {e.name}", color='info')

        ui.upload(
            label='Upload DWG File',
            multiple=False,
            on_upload=on_file_upload
        ).classes('w-full mb-4')

        def handle_submit():
            file = uploaded_file['file']
            if not file:
                ui.notify('Please upload a file.', color='negative')
                return

            try:
                ipfs_hash = upload_to_ipfs(file)
            except Exception as e:
                ui.notify(f"IPFS upload failed: {e}", color='negative')
                return

            file_size = len(file.content.read())
            file.content.seek(0)

            doc_id = str(uuid.uuid4())
            document = {
                'id': doc_id,
                'project_name': doc['project_name'].value,
                'document_name': doc['document_name'].value,
                'tags': doc['tags'].value,
                'description': doc['description'].value,
                'filename': file.name,
                'size': file_size,
                'ipfs_hash': ipfs_hash,
                'ipfs_url': f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}",
                'uploaded_at': datetime.now().isoformat(),
                'uploaded_by': user['email'],
            }

            documents = load_documents()
            documents.append(document)
            save_documents(documents)

            ui.notify('✅ File uploaded to IPFS and saved locally!', color='positive')
            ui.navigate.to('/documents')

        with ui.row().classes('justify-center gap-4'):
            ui.button('Upload', on_click=handle_submit).classes('bg-blue-600 text-white px-4 py-2 rounded-xl')
            ui.button('Cancel', on_click=lambda: ui.navigate.to('/dashboard/engineer')).classes('bg-gray-400 text-white px-4 py-2 rounded-xl')
