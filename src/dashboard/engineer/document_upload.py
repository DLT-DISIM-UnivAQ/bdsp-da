from nicegui import ui
from src.auth.auth_roles import require_permission, get_user
import uuid
import json
from datetime import datetime

STORAGE_KEY = 'uploaded_documents'

def load_documents():
    try:
        raw = ui.storage.local.get(STORAGE_KEY) or '[]'
        return json.loads(raw)
    except Exception:
        return []

def save_documents(documents):
    ui.storage.local[STORAGE_KEY] = json.dumps(documents)

@require_permission('document_upload')
def document_upload():
    user = get_user()

    with ui.column().classes('w-full items-center p-8'):
        ui.label('📤 Upload Project Document').classes('text-2xl font-bold text-blue-900 mb-4')
        ui.label(f"Logged in as: {user['email']}").classes("text-sm text-blue-600 mb-4")

        doc = {
            'project_name': ui.input('Project Name').classes('w-full mb-2'),
            'document_name': ui.input('Document Name').classes('w-full mb-2'),
            'tags': ui.input('Tags (comma separated)').classes('w-full mb-2'),
            'description': ui.textarea('Description').classes('w-full mb-4'),
        }

        file_input = ui.upload(
            label='Upload DWG File',
            multiple=False,
            on_upload=lambda e: ui.notify(f"Selected file: {e.name}", color='info')
        ).classes('w-full mb-4')

        def handle_submit():
            if not file_input.value:
                ui.notify('Please upload a file.', color='negative')
                return

            file = file_input.value[0]
            doc_id = str(uuid.uuid4())

            document = {
                'id': doc_id,
                'project_name': doc['project_name'].value,
                'document_name': doc['document_name'].value,
                'tags': doc['tags'].value,
                'description': doc['description'].value,
                'filename': file.name,
                'size': file.size,
                'uploaded_at': datetime.now().isoformat(),
                'uploaded_by': user['email'],
            }

            documents = load_documents()
            documents.append(document)
            save_documents(documents)

            ui.notify('Document uploaded and saved locally!', color='positive')
            ui.navigate.to('/documents')

        with ui.row().classes('justify-center gap-4'):
            ui.button('Upload', on_click=handle_submit).classes('bg-blue-600 text-white px-4 py-2 rounded-xl')
            ui.button('Cancel', on_click=lambda: ui.navigate.to('/dashboard/engineer')).classes('bg-gray-400 text-white px-4 py-2 rounded-xl')
