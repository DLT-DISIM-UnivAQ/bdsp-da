from nicegui import ui
from src.services.nft import get_all_nfts, transfer_nft
from src.mock.wallet import get_wallet

def nfts_page():
    nfts = get_all_nfts()

    def handle_transfer(nft_id, new_owner):
        transfer_nft(nft_id, new_owner)
        ui.notify(f'NFT {nft_id} transferred!', color='positive')
        ui.navigate.refresh()

    with ui.column().classes('p-8 bg-blue-50 min-h-screen'):
        ui.label('🎨 Minted NFTs').classes('text-2xl font-bold mb-4 text-blue-900')

        if not nfts:
            ui.label('No NFTs minted yet.').classes('text-gray-600')
        else:
            for nft in nfts:
                with ui.card().classes('mb-4 p-4 bg-white shadow-md'):
                    ui.label(f"NFT ID: {nft['id']}").classes('font-semibold')
                    ui.label(f"Title: {nft['metadata']['title']}")
                    ui.label(f"Description: {nft['metadata']['desc']}")
                    ui.label(f"Owner: {nft['owner']}")
                    ui.label(f"Doc: {nft['doc']['name']} ({nft['doc']['type']})")

                    with ui.row():
                        new_owner = ui.input('Transfer to wallet')
                        ui.button('Transfer', on_click=lambda nid=nft['id'], ow=new_owner: handle_transfer(nid, ow.value))
