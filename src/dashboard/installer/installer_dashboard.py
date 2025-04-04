from nicegui import ui
from datetime import datetime
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import InstallerImage

@require_permission('upload_images')
def dashboard_installer():
    user = get_user()
    session = SessionLocal()
    uploaded_by = user['email'].lower()

    # 📊 Stats
    total = session.query(InstallerImage).filter_by(uploaded_by=uploaded_by).count()
    pending = session.query(InstallerImage).filter_by(uploaded_by=uploaded_by, approved=False).count()
    approved = session.query(InstallerImage).filter_by(uploaded_by=uploaded_by, approved=True).count()

    # State to store date range
    date_range = {'start': None, 'end': None}

    def update_recent_table(container):
        container.clear()
        query = session.query(InstallerImage).filter_by(uploaded_by=uploaded_by)
        if date_range['start'] and date_range['end']:
            query = query.filter(InstallerImage.uploaded_at.between(date_range['start'], date_range['end']))
        recent = query.order_by(InstallerImage.uploaded_at.desc()).limit(5).all()
        with container:
            ui.table(columns=['Date', 'Image', 'Site'], rows=[
                {'Date': img.uploaded_at.strftime('%Y-%m-%d'), 'Image': img.image_name, 'Site': img.site_name}
                for img in recent
            ]).classes('w-full')

    # 📦 Main UI Layout
    with ui.column().classes('w-full items-center p-8 bg-gray-50'):
        ui.label(f'🧰 Installer Dashboard - {user["email"]}').classes('text-2xl font-bold text-blue-900 mb-6')

        with ui.row().classes('mb-6 gap-4 justify-center'):
            ui.button('📦 Inventory', on_click=lambda: ui.navigate.to('/installer/list')).classes('bg-blue-100 text-blue-800 px-4 py-2 rounded')
            ui.button('📸 Upload Image', on_click=lambda: ui.navigate.to('/installer/upload')).classes('bg-green-100 text-green-800 px-4 py-2 rounded')
            ui.button('🔒 Logout', on_click=lambda: ui.run_javascript('''
                localStorage.removeItem('wallet');
                window.location.href = '/';
            ''')).classes('bg-gray-600 text-white px-4 py-2 rounded')

        # 📊 Summary Cards
        with ui.row().classes('w-full justify-around mb-6'):
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/4'):
                ui.label(f'📁 Total Images: {total}').classes('text-center text-lg text-blue-900')
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/4'):
                ui.label(f'⏳ Pending Approval: {pending}').classes('text-center text-lg text-yellow-700')
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/4'):
                ui.label(f'✅ Approved: {approved}').classes('text-center text-lg text-green-700')

        # 🔷 Unified row for chart + recent uploads + date filter
        with ui.row().classes('w-full items-start gap-6 mt-4'):

            # 📈 Upload Summary Chart
            with ui.card().classes('w-1/3 p-6 bg-white rounded-xl shadow-md'):
                ui.label('📈 Upload Summary').classes('text-xl font-semibold mb-4')
                ui.echart({
                    'xAxis': {'type': 'category', 'data': ['Total', 'Pending', 'Approved']},
                    'yAxis': {'type': 'value'},
                    'series': [{
                        'data': [total, pending, approved],
                        'type': 'bar',
                        'itemStyle': {'color': '#3b82f6'},
                    }]
                }).classes('h-64 w-full')

            # 📌 Recent Uploads Table
            # with ui.card().classes('w-1/3 p-6 bg-white rounded-xl shadow-md'):
            #     ui.label('📌 Recent Uploads').classes('text-xl font-semibold mb-4')
            #     table_container = ui.column().classes('w-full')
            #     update_recent_table(table_container)

            # # 📅 Date Filter
            # with ui.card().classes('w-1/3 p-6 bg-white rounded-xl shadow-md'):
            #     ui.label('📅 Filter by Date').classes('text-xl font-semibold mb-4')

            #     def on_date_change(e):
            #         if e.value and isinstance(e.value, list) and len(e.value) == 2:
            #             date_range['start'] = e.value[0]
            #             date_range['end'] = e.value[1]
            #             update_recent_table(table_container)

            #     ui.date().props('range').on('update:model-value', on_date_change).classes('w-full')
