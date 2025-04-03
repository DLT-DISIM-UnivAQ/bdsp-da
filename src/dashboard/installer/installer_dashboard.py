from nicegui import ui
from datetime import date
from src.auth.auth_roles import require_permission, get_user

@require_permission('upload_images')
def dashboard_installer():
    user = get_user()

    with ui.column().classes('w-full items-center p-8'):
        ui.label(f'🧰 Installer Dashboard - {user["email"]}').classes('text-2xl font-bold text-blue-800 mb-6')

        # 🔷 Navigation Tabs
        with ui.row().classes('mb-6 gap-4 justify-center'):
            ui.button('📸 Upload Image', on_click=lambda: ui.navigate.to('/installer/upload')).props('flat').classes('bg-green-100 text-green-800')
            ui.button('🧾 Site Notes', on_click=lambda: ui.navigate.to('/installer/notes')).props('flat').classes('bg-yellow-100 text-yellow-800')
            ui.button('📦 Inventory Check', on_click=lambda: ui.navigate.to('/installer/inventory')).props('flat').classes('bg-blue-100 text-blue-700')
            ui.button('📍 Assign Task', on_click=lambda: ui.navigate.to('/installer/tasks')).props('flat').classes('bg-purple-100 text-purple-800')
            ui.button('🔒 Logout', on_click=lambda: ui.run_javascript('''
                localStorage.removeItem('wallet');
                window.location.href = '/';
            ''')).classes('bg-gray-500 text-white px-4 py-2 rounded-xl')

        # 🔷 Dashboard Stats
        with ui.row().classes('w-full justify-around mb-6'):
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/4'):
                ui.label('Total Sites: 15').classes('text-center text-lg text-blue-800')
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/4'):
                ui.label('Images Uploaded: 38').classes('text-center text-lg text-green-600')
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/4'):
                ui.label('Pending Issues: 4').classes('text-center text-lg text-red-600')

        ui.date().props('range').classes('mb-4')

        with ui.row().classes('w-full'):
            with ui.card().classes('w-1/2 p-6 bg-white rounded-xl shadow-md'):
                ui.label('📌 Recent Uploads').classes('text-xl font-semibold mb-2')
                with ui.table(columns=['Time', 'Image', 'Site'], rows=[
                    {'Time': '09:30 AM', 'Image': 'panel_1.jpg', 'Site': 'Site_A'},
                    {'Time': '11:00 AM', 'Image': 'cabling.jpg', 'Site': 'Site_B'},
                    {'Time': '12:15 PM', 'Image': 'roof_install.jpg', 'Site': 'Site_C'},
                ]).classes('w-full'):
                    pass

            with ui.card().classes('w-1/2 p-6 bg-white rounded-xl shadow-md'):
                ui.label('📊 Upload Summary').classes('text-xl font-semibold mb-2')
                ui.echart({
                    'xAxis': {'type': 'category', 'data': ['Today', 'This Week', 'This Month']},
                    'yAxis': {'type': 'value'},
                    'series': [{
                        'data': [3, 14, 38],
                        'type': 'bar',
                        'itemStyle': {'color': '#10b981'},
                    }]
                }).classes('h-64 w-full')
