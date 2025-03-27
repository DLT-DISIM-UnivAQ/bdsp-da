from nicegui import ui

def documents_page():
    ui.add_body_html('''
    <style>
       .docs-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    width: 50%; /* Adjust width as needed */
    margin: 0 auto; /* Centers horizontally */
    background-color: #f0f4f8;
    padding: 54px 91px;
}

        .docs-container {
            width: 100%;
            max-width: 1200px;
        }
    </style>
    ''')

    with ui.element('div').classes('docs-wrapper'):
        with ui.element('div').classes('docs-container'):
            ui.label('📂 Uploaded Documents').classes('text-3xl font-bold text-blue-900 mb-6')

            async def load_docs():
                docs = await ui.run_javascript('JSON.parse(localStorage.getItem("doc_entries") || "[]")')
                if not docs:
                    ui.label('No documents found.').classes('text-gray-600')
                    return

                for doc in docs:
                    with ui.card().classes('mb-4 p-4 bg-white shadow-md'):
                        ui.label(f"📁 {doc.get('file_name', 'Untitled')}").classes('text-xl font-semibold')
                        ui.label(f"Building: {doc.get('building_name', 'N/A')} at {doc.get('building_address', '')}").classes('text-sm text-gray-700')
                        ui.label(f"City: {doc.get('city')} | Engineer: {doc.get('engineer_name')}").classes('text-sm text-gray-700')
                        ui.label(f"Project: {doc.get('project_type')} | Status: {doc.get('status')}").classes('text-sm text-gray-700')
                        ui.label(f"Start: {doc.get('start_date')} → Completion: {doc.get('end_date')}").classes('text-sm text-gray-700')

                        if 'documents' in doc:
                            with ui.column():
                                for file in doc['documents']:
                                    ui.label(f"📎 {file['name']} ({file['type']})").classes('text-sm text-blue-800')

            ui.button('⬅️ Back to Dashboard', on_click=lambda: ui.navigate.to('/dashboard')).classes('mt-6 bg-gray-600 text-white px-6 py-2 rounded-xl')

            ui.timer(0.2, load_docs, once=True)
