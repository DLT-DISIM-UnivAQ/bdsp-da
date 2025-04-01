from nicegui import ui
from src.services.storage import save_document, get_documents, delete_document

def upload_page():
    def refresh():
        ui.navigate.refresh()

    def handle_upload(e):
        doc_type = type_select.value
        uploaded_file = e.content.read()
        save_document(doc_type, e.name, uploaded_file.decode('latin1'))
        ui.notify('Document uploaded successfully', color='positive')
        refresh()

    def remove_doc(doc_id):
        delete_document(doc_id)
        ui.notify('Document deleted', color='warning')
        refresh()

    with ui.column().classes('p-8 bg-blue-50 min-h-screen'):
        ui.label('📄 Upload Project Document').classes('text-2xl font-bold mb-4 text-blue-900')

        with ui.row().classes('mb-4 items-center gap-4'):
            type_select = ui.select(
                ['Permissions', 'Architectural', 'Structural', 'Electrical'],
                label='Document Type',
                value='Permissions'
            ).classes('w-64')
            ui.upload(label='Choose File', auto_upload=True, on_upload=handle_upload).classes('w-64')

        ui.label('📚 Uploaded Documents').classes('text-xl font-semibold mt-6 mb-2 text-blue-800')
        documents = get_documents()
        if not documents:
            ui.label('No documents uploaded yet.').classes('text-gray-600')
        else:
            for doc in documents:
                with ui.card().classes('mb-4 p-4 shadow-md bg-white'):
                    ui.label(f"📁 {doc['name']}").classes('text-md font-semibold')
                    ui.label(f"Type: {doc['type']}").classes('text-sm text-gray-700')
                    ui.button('🗑️ Delete', on_click=lambda d=doc['id']: remove_doc(d)).classes('bg-red-500 text-white mt-2')
