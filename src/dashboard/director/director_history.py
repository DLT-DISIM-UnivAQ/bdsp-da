from nicegui import ui
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import NFTMint
from datetime import datetime

@require_permission('approve_images')
def director_mint_history():
    user = get_user()
    session = SessionLocal()

    minted = session.query(NFTMint).filter_by(role='director', minted_by=user['email']) \
                                   .order_by(NFTMint.minted_at.desc()).all()

    with ui.column().classes('w-full items-center p-8 bg-gray-50'):
        with ui.row().classes('w-full justify-between items-center mb-6'):
            ui.label(f'🧠 Director Mint History - {user["email"]}') \
              .classes('text-2xl font-bold text-blue-900')
            with ui.row().classes('gap-3'):
                ui.button('🎯 Dashboard', on_click=lambda: ui.navigate.to('/dashboard/director')) \
                    .classes('bg-green-100 text-green-800 px-4 py-2 rounded')
                ui.button('🖼️ Review Submissions', on_click=lambda: ui.navigate.to('/director/approval')) \
                    .classes('bg-green-100 text-green-800 px-4 py-2 rounded')
                ui.button('🔒 Logout', on_click=lambda: ui.navigate.to('/')) \
                    .classes('bg-gray-500 text-white px-4 py-2 rounded')

        if not minted:
            ui.label('📭 No NFTs minted yet.').classes('text-gray-600 mt-6')
            return

        for item in minted:
            with ui.row().classes('w-full gap-4 bg-white shadow-md rounded p-4 mb-4'):
                # Image preview
                ipfs_hash = item.ipfs_uri.replace("ipfs://", "") if item.ipfs_uri else None
                img_url = f"https://beige-wooden-aardwolf-131.mypinata.cloud/ipfs/{ipfs_hash}" \
                          if ipfs_hash else "https://via.placeholder.com/100x100.png?text=No+Image"
                ui.image(img_url).classes("w-24 h-24 rounded shadow")

                # Info details
                with ui.column().classes('grow'):
                    ui.label(f"🧾 File: {item.file_name}").classes('text-md font-bold text-blue-900')
                    ui.label(f"📅 Minted: {item.minted_at.strftime('%Y-%m-%d %H:%M')}").classes('text-sm text-gray-600')
                    ui.label(f"🧠 Token ID: {item.token_id or 'N/A'}").classes('text-sm text-gray-600')
                    ui.label(f"📜 Contract: {item.contract_address}").classes('text-sm text-gray-500')

                    if item.ipfs_uri:
                        metadata_url = f"https://beige-wooden-aardwolf-131.mypinata.cloud/ipfs/{ipfs_hash}"
                        ui.link('🔗 View Metadata', metadata_url, new_tab=True).classes('text-blue-600')

        ui.button('⬅️ Back to Approval', on_click=lambda: ui.navigate.to('/director/approval')) \
            .classes('mt-6 bg-gray-600 text-white px-4 py-2 rounded')
