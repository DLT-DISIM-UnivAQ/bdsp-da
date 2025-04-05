from nicegui import ui
from datetime import datetime
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import EngineerDocument

@require_permission('upload_documents')
def engineer_document_list():
    user = get_user()
    session = SessionLocal()
    uploaded_by = user['email'].lower()

    def delete_document(doc_id: int):
        doc = session.query(EngineerDocument).filter_by(id=doc_id, uploaded_by=uploaded_by).first()
        if doc:
            session.delete(doc)
            session.commit()
            ui.notify('🗑️ Document deleted.')
            ui.navigate.to('/engineer/list')

    with ui.column().classes('w-full items-center p-8'):
        ui.label(f'📚 Engineer Documents - {user["email"]}').classes('text-2xl font-bold text-blue-800 mb-6')
        
        with ui.row().classes('mb-4 gap-4'):
            ui.button('➕ Upload New Document', on_click=lambda: ui.navigate.to('/engineer/upload')) \
                .classes('bg-green-600 text-white px-4 py-2 rounded')
            ui.button('🚀 Go to Minting Page', on_click=lambda: ui.navigate.to('/engineer/mint')) \
                .classes('bg-blue-600 text-white px-4 py-2 rounded')
            ui.button('⬅️ Back to Dashboard', on_click=lambda: ui.navigate.to('/dashboard/engineer')).classes('mb-4 bg-gray-200 px-4 py-2 rounded')
            ui.button('🔒 Logout', on_click=lambda: ui.navigate.to('/')).classes('bg-gray-500 text-white px-4 py-2 rounded')

        documents = session.query(EngineerDocument).filter_by(uploaded_by=uploaded_by).order_by(EngineerDocument.uploaded_at.desc()).all()

        if not documents:
            ui.label('No documents uploaded yet.').classes('text-gray-600')
        else:
            for doc in documents:
                with ui.row().classes('w-full bg-white shadow-md rounded p-4 mb-2 items-center'):
                    with ui.column().classes('grow'):
                        ui.label(f'📁 {doc.document_name}').classes('text-lg font-bold text-blue-900')
                        ui.label(f'📅 Uploaded: {doc.uploaded_at.strftime("%Y-%m-%d %H:%M")}').classes('text-sm text-gray-500')
                        ui.label(f'📌 Project: {doc.project_name}').classes('text-sm text-gray-600')
                        ui.label(f'📝 Description: {doc.description}').classes('text-sm text-gray-700')

                    with ui.row().classes('gap-2 items-center'):
                        ui.button('✏️ Edit', on_click=lambda d=doc.id: print(f'Edit doc {d}')) \
                            .props('outline dense').classes('text-yellow-600')
                        ui.button('🗑️ Delete', on_click=lambda d=doc.id: delete_document(d)) \
                            .props('outline dense').classes('text-red-600')
