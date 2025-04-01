from nicegui import ui
from datetime import date
from src.auth.auth_roles import require_permission, get_user

@require_permission('dashboard_overview')
def dashboard_engineer():
    user = get_user()

    with ui.column().classes('w-full items-center p-8'):
        ui.label(f'👷 Engineer Dashboard - {user["email"]}').classes('text-2xl font-bold text-blue-800 mb-6')

        # 🔷 Tabs for navigation
        with ui.row().classes('mb-6 gap-4 justify-center'):
            ui.button('📊 Overview', on_click=lambda: ui.navigate.to('/dashboard/engineer')).props('flat').classes('bg-blue-100 text-blue-700')
            ui.button('📤 Upload Document', on_click=lambda: ui.navigate.to('/upload')).props('flat').classes('bg-green-100 text-green-800')
            ui.button('🧐 Validate Document', on_click=lambda: ui.navigate.to('/validate')).props('flat').classes('bg-yellow-100 text-yellow-800')
            ui.button('📨 Submit to Blockchain', on_click=lambda: ui.navigate.to('/submit')).props('flat').classes('bg-indigo-100 text-indigo-800')
            ui.button('🧩 View DWG', on_click=lambda: ui.navigate.to('/viewer')).props('flat').classes('bg-purple-100 text-purple-800')
            ui.button('🏗️ Project Management', on_click=lambda: ui.navigate.to('/projects')).props('flat').classes('bg-pink-100 text-pink-800')
            ui.button('🔒 Logout', on_click=lambda: ui.run_javascript('''
                        localStorage.removeItem('wallet');
                        if (typeof window.ethereum !== 'undefined') {
                            window.ethereum.request({
                                method: 'wallet_requestPermissions',
                                params: [{ eth_accounts: {} }]
                            }).catch(console.warn);
                        }
                        window.location.href = '/';
                    ''')).classes('bg-gray-500 text-white px-4 py-2 rounded-xl')


        # 🔷 Dashboard Stats
        with ui.row().classes('w-full justify-around mb-6'):
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/5'):
                ui.label('Total Projects: 8').classes('text-center text-lg text-blue-800')
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/5'):
                ui.label('Pending Documents: 5').classes('text-center text-lg text-yellow-600')
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/5'):
                ui.label('Approved Documents: 12').classes('text-center text-lg text-green-600')
            with ui.card().classes('bg-white shadow-xl p-6 rounded-xl w-1/5'):
                ui.label('Rejected Documents: 2').classes('text-center text-lg text-red-600')

        ui.date().props('range').classes('mb-4')

        with ui.row().classes('w-full'):
            with ui.card().classes('w-1/2 p-6 bg-white rounded-xl shadow-md'):
                ui.label('📌 Recent Activity').classes('text-xl font-semibold mb-2')
                with ui.table(columns=['Time', 'Action', 'Document'], rows=[
                    {'Time': '10:15 AM', 'Action': 'Uploaded', 'Document': 'Plan_A_v1.dwg'},
                    {'Time': '10:40 AM', 'Action': 'Approved', 'Document': 'Plan_B_v2.dwg'},
                    {'Time': '11:10 AM', 'Action': 'Rejected', 'Document': 'Electrical_A.dwg'},
                ]).classes('w-full'):
                    pass

            with ui.card().classes('w-1/2 p-6 bg-white rounded-xl shadow-md'):
                ui.label('📈 Document Status Summary').classes('text-xl font-semibold mb-2')
                ui.echart({
                    'xAxis': {'type': 'category', 'data': ['Pending', 'Approved', 'Rejected']},
                    'yAxis': {'type': 'value'},
                    'series': [{
                        'data': [5, 12, 2],
                        'type': 'bar',
                        'itemStyle': {'color': '#3b82f6'},
                    }]
                }).classes('h-64 w-full')
