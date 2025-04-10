from nicegui import ui
from datetime import datetime
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import EngineerDocument

@require_permission('dashboard_overview')
def dashboard_engineer():
    user = get_user()
    session = SessionLocal()

    # Fetch statistics
    uploaded_by = user['email']
    total = session.query(EngineerDocument).filter_by(uploaded_by=uploaded_by).count()
    pending = session.query(EngineerDocument).filter_by(uploaded_by=uploaded_by, token_uri=None).count()
    approved = session.query(EngineerDocument).filter(EngineerDocument.uploaded_by == uploaded_by, EngineerDocument.token_uri != None).count()
    rejected = 0  # If you plan to add rejection flag later

    with ui.column().classes('w-full items-center p-8 bg-gray-50'):
        ui.label(f'👷 Engineer Dashboard - {uploaded_by}').classes('text-2xl font-bold text-blue-900 mb-6')

        with ui.row().classes('gap-4 mb-6'):
            ui.button('📄 Upload Document', on_click=lambda: ui.navigate.to('/engineer/upload')).classes('bg-green-100 text-green-800 px-4 py-2 rounded')
            ui.button('📁 Document List', on_click=lambda: ui.navigate.to('/engineer/list')).classes('bg-blue-100 text-blue-700 px-4 py-2 rounded')
            ui.button('🔒 Logout', on_click=lambda: ui.navigate.to('/')).classes('bg-gray-500 text-white px-4 py-2 rounded')
            ui.button('🔓 Decrypt URL', on_click=lambda: ui.navigate.to('/decrypt_gateway_url')).props('flat').classes('ml-4')

        with ui.row().classes('w-full justify-around'):
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/5'):
                ui.label(f'Total Documents: {total}').classes('text-center text-lg text-blue-800')
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/5'):
                ui.label(f'Pending Documents: {pending}').classes('text-center text-lg text-yellow-600')
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/5'):
                ui.label(f'Minted Documents: {approved}').classes('text-center text-lg text-green-600')
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/5'):
                ui.label(f'Rejected Documents: {rejected}').classes('text-center text-lg text-red-600')

        with ui.card().classes('w-full mt-6 p-6 bg-white rounded-xl shadow-md'):
            ui.label('📈 Document Status Summary').classes('text-xl font-semibold mb-4')
            ui.echart({
                'xAxis': {'type': 'category', 'data': ['Pending', 'Minted', 'Rejected']},
                'yAxis': {'type': 'value'},
                'series': [{
                    'data': [pending, approved, rejected],
                    'type': 'bar',
                    'itemStyle': {'color': '#3b82f6'},
                }]
            }).classes('h-64 w-full')
