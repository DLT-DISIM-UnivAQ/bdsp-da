from nicegui import ui, app
import uuid

from src.mock.wallet import connect_wallet

def dashboard_page():
    wallet = app.storage.user.get('wallet', 'Not connected')
    email = app.storage.user.get('email', 'Unknown user')

    if wallet != 'Not connected':
        connect_wallet(wallet)

    ui.add_body_html('''
    <style>
        .dashboard-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 40px 16px 60px;
        }
        .dashboard-container {
            width: 100%;
            max-width: 1200px;
            padding-left: 550px;
        }
    </style>
    ''')

    with ui.element('div').classes('dashboard-wrapper'):
        with ui.element('div').classes('dashboard-container'):
            with ui.card().classes('w-full p-6 bg-white shadow-lg rounded-xl'):
                ui.label(f'👋 Welcome, {email}').classes('text-2xl font-bold text-blue-900')
                ui.label(f'🦊 Wallet: {wallet}').classes('text-md text-blue-700 mb-4')

            with ui.card().classes('w-full p-6 bg-white shadow-lg rounded-xl mt-4'):
                ui.label('🏗️ Project Dashboard').classes('text-3xl font-bold text-blue-900 mb-2')
                ui.label('Manage your construction documents and NFT records').classes('text-lg text-blue-700 mb-6')

                with ui.row().classes('gap-4 mb-6 justify-center'):
                    ui.button('📂 View Documents', on_click=lambda: ui.navigate.to('/documents')).classes('bg-blue-500 text-white px-4 py-2 rounded-xl')
                    ui.button('🎨 View Minted NFTs', on_click=lambda: ui.navigate.to('/nfts')).classes('bg-purple-600 text-white px-4 py-2 rounded-xl')
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



            with ui.card().classes('w-full p-6 bg-white shadow-md rounded-xl mt-6'):
                ui.label('📑 Project Metadata & Document Upload').classes('text-2xl font-semibold text-blue-800 mb-4')

                uploaded_files = []

                def handle_upload(e):
                    for file in e.files:
                        content = file['content'].read().decode('latin1')
                        uploaded_files.append({
                            'id': str(uuid.uuid4()),
                            'name': file['name'],
                            'type': file['type'],
                            'content': content
                        })
                        ui.notify(f"Uploaded {file['name']}", color='positive')

                ui.upload(multiple=True, label='Upload Documents', auto_upload=True, on_upload=handle_upload).classes('w-full mb-4')

                metadata = {
                    'file_name': ui.input('File Name').props('outlined dense').classes('w-full'),
                    'file_code': ui.input('File Code').props('outlined dense').classes('w-full'),
                    'building_name': ui.input('Building Name').props('outlined dense').classes('w-full'),
                    'building_address': ui.input('Building Address').props('outlined dense').classes('w-full'),
                    'city': ui.input('City').props('outlined dense').classes('w-full'),
                    'engineer_name': ui.input('Engineer Name').props('outlined dense').classes('w-full'),
                    'start_date': ui.input('Project Start Date').props('outlined dense type=date').classes('w-full'),
                    'end_date': ui.input('Estimated Completion').props('outlined dense type=date').classes('w-full'),
                    'project_type': ui.select(['Residential', 'Commercial', 'Industrial'], label='Project Type').props('outlined dense').classes('w-full'),
                    'status': ui.select(['Approved', 'Pending', 'Rejected'], label='Approval Status').props('outlined dense').classes('w-full')
                }

                def save_all():
                    entry = {key: field.value for key, field in metadata.items()}
                    entry['documents'] = uploaded_files
                    entry['id'] = str(uuid.uuid4())

                    js = f'''
                        let entries = JSON.parse(localStorage.getItem('doc_entries') || '[]');
                        entries.push({entry});
                        localStorage.setItem('doc_entries', JSON.stringify(entries));
                    '''
                    ui.run_javascript(js)
                    ui.notify('Saved to localStorage!', color='green')

                ui.button('💾 Save Metadata & Files', on_click=save_all).classes('mt-4 bg-blue-600 text-white px-6 py-2 rounded-xl')
