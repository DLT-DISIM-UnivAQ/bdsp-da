import json, uuid, time
from nicegui import ui
from src.mock.wallet import get_wallet

NFT_KEY = 'nfts'

def get_all_nfts():
    return ui.run_javascript(f"""
        const nfts = localStorage.getItem('{NFT_KEY}');
        send(nfts ? JSON.parse(nfts) : []);
    """, respond_to='nft_list')

def save_nfts(nfts):
    ui.run_javascript(f"localStorage.setItem('{NFT_KEY}', JSON.stringify({json.dumps(nfts)}))")

def mint_nft(document, title, desc):
    nfts = get_all_nfts()
    nft = {
        "id": str(uuid.uuid4())[:8],
        "owner": get_wallet(),
        "doc": document,
        "metadata": {"title": title, "desc": desc},
        "timestamp": time.time()
    }
    nfts.append(nft)
    save_nfts(nfts)

def transfer_nft(nft_id, new_owner):
    nfts = get_all_nfts()
    for nft in nfts:
        if nft['id'] == nft_id:
            nft['owner'] = new_owner
    save_nfts(nfts)
