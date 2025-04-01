import uuid
from nicegui import ui

STORAGE_KEY = 'documents'

def get_documents():
    return ui.run_javascript(f"""
        const docs = localStorage.getItem('{STORAGE_KEY}');
        send(docs ? JSON.parse(docs) : []);
    """, respond_to='docs_list')

def save_document(doc_type, name, content):
    return ui.run_javascript(f"""
        const existing = JSON.parse(localStorage.getItem('{STORAGE_KEY}') || '[]');
        existing.push({{
            id: '{str(uuid.uuid4())[:8]}',
            type: '{doc_type}',
            name: '{name}',
            content: `{content}`
        }});
        localStorage.setItem('{STORAGE_KEY}', JSON.stringify(existing));
    """)

def delete_document(doc_id):
    return ui.run_javascript(f"""
        let docs = JSON.parse(localStorage.getItem('{STORAGE_KEY}') || '[]');
        docs = docs.filter(d => d.id !== '{doc_id}');
        localStorage.setItem('{STORAGE_KEY}', JSON.stringify(docs));
    """)
