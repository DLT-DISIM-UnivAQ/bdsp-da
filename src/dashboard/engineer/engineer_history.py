from nicegui import ui
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import NFTMint
from datetime import datetime

@require_permission('dashboard_overview')
def engineer_mint_history():
    user = get_user()
    session = SessionLocal()
    minted = session.query(NFTMint).filter_by(role='engineer', minted_by=user['email']).order_by(NFTMint.minted_at.desc()).all()

    with ui.column().classes('w-full items-center p-8'):
        ui.label(f'🧾 Engineer NFT History - {user["email"]}').classes('text-2xl font-bold text-blue-900 mb-6')
        ui.button('⬅️ Back to Dashboard', on_click=lambda: ui.navigate.to('/dashboard/engineer')).classes('mb-4 bg-gray-200 px-4 py-2 rounded')
        ui.button('🔒 Logout', on_click=lambda: ui.navigate.to('/')).classes('bg-gray-500 text-white px-4 py-2 rounded')

        if not minted:
            ui.label('No NFT minting history found.').classes('text-gray-600')
        else:
            for item in minted:
                metadata_url = item.ipfs_uri.replace("ipfs://", "https://beige-wooden-aardwolf-131.mypinata.cloud/ipfs/")
                with ui.row().classes('w-full gap-4 bg-white shadow-md rounded p-4 mb-3'):
                    ui.label(f"🧾 File: {item.file_name}").classes('text-md font-bold text-blue-900')
                    ui.label(f"📅 Minted: {item.minted_at.strftime('%Y-%m-%d %H:%M')}").classes('text-sm text-gray-600')
                    ui.label(f"📜 Contract: {item.contract_address}").classes('text-sm text-gray-500')
                    ui.link('🔗 View Metadata', metadata_url, new_tab=True).classes('text-blue-600')
