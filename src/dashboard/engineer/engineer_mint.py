from nicegui import ui
from datetime import datetime
import os, requests, json
from dotenv import load_dotenv
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import EngineerDocument, NFTMint

load_dotenv()

PINATA_JWT = os.getenv('PINATA_JWT')
PINATA_UPLOAD_URL = os.getenv('PINATA_UPLOAD_URL')
PINATA_JSON_URL = os.getenv('PINATA_JSON_URL')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
PLACEHOLDER_IMAGE = 'https://via.placeholder.com/300x300.png?text=Engineering+NFT'
CUSTOM_GATEWAY = 'https://beige-wooden-aardwolf-131.mypinata.cloud/ipfs'

def upload_file_to_ipfs_bytes(file_bytes, name):
    headers = {'Authorization': f'Bearer {PINATA_JWT}'}
    files = {'file': (name, file_bytes, 'application/pdf')}
    res = requests.post(PINATA_UPLOAD_URL, headers=headers, files=files)
    if res.status_code == 200:
        return res.json()['IpfsHash']
    raise Exception(f"❌ File upload failed: {res.text}")

def upload_json_to_ipfs(metadata, original_filename='metadata'):
    headers = {'Authorization': f'Bearer {PINATA_JWT}', 'Content-Type': 'application/json'}
    filename = os.path.splitext(original_filename)[0] + 'JSON'
    payload = {
        "pinataMetadata": {"name": filename},
        "pinataContent": metadata
    }
    res = requests.post(PINATA_JSON_URL, headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()['IpfsHash']
    raise Exception(f"❌ Metadata upload failed: {res.text}")

@require_permission('mint_documents')
def engineer_mint_documents():
    user = get_user()
    session = SessionLocal()
    engineer_email = user['email'].lower()

    documents = session.query(EngineerDocument).filter_by(
        uploaded_by=engineer_email,
        token_uri=None
    ).all()

    with ui.column().classes('w-full items-center p-8'):
        ui.label(f'🧪 Mint Engineering Documents - {engineer_email}').classes('text-2xl font-bold text-blue-800 mb-6')
        ui.button('⬅️ Dashboard', on_click=lambda: ui.navigate.to('/dashboard/engineer')).classes('mb-4 bg-gray-200 px-4 py-2 rounded')
        ui.button('📄 Document List', on_click=lambda: ui.navigate.to('/engineer/list')).classes('bg-green-100 text-green-800 px-4 py-2 rounded')

        if not documents:
            ui.label('📂 No documents available for minting. Please upload first.').classes('text-gray-600')
            return

        for doc in documents:
            with ui.row().classes('w-full bg-white p-4 rounded shadow-md mb-4 items-center gap-6'):
                with ui.column().classes('grow'):
                    ui.label(f"📄 {doc.document_name}").classes('text-md font-semibold text-blue-900')
                    ui.label(f"📁 Project: {doc.project_name}").classes('text-sm text-gray-700')
                    ui.label(f"📅 Uploaded: {doc.uploaded_at.strftime('%Y-%m-%d')}").classes('text-xs text-gray-500')
                    ui.label(f"📝 {doc.description or 'No description provided'}").classes('text-sm text-gray-600')

                    if doc.ipfs_url:
                        ipfs_hash = doc.ipfs_url.split("/")[-1]
                        file_url = f"{CUSTOM_GATEWAY}/{ipfs_hash}"
                        if doc.document_name.lower().endswith('.pdf'):
                            ui.link('📄 View PDF', file_url, new_tab=True).classes('text-blue-600')
                            ui.html(f'<iframe src="{file_url}" width="100%" height="300px" style="border:1px solid #ccc;"></iframe>')
                        else:
                            ui.link('📎 Download File', file_url, new_tab=True).classes('text-blue-600')

                def mint_this_document(doc_to_mint=doc):
                    try:
                        ipfs_hash = doc_to_mint.ipfs_url.split("/")[-1]
                        download_url = f"{CUSTOM_GATEWAY}/{ipfs_hash}"
                        file_bytes = requests.get(download_url).content
                        file_ipfs_hash = upload_file_to_ipfs_bytes(file_bytes, doc_to_mint.document_name)
                        file_ipfs_uri = f"ipfs://{file_ipfs_hash}"
                        gateway_url = f"{CUSTOM_GATEWAY}/{file_ipfs_hash}"

                        # 🎨 Determine image preview based on file type
                        extension = doc_to_mint.document_name.lower().split('.')[-1]
                       # Determine preview image
                        if extension == 'pdf':
                            image_preview_hash = 'bafkreigmgygyhdct2zf6qbgy2rbburbf4tgwmxyotwsrazv7ookawojm5u'
                        elif extension == 'dwg':
                            image_preview_hash = 'bafkreiclofpyxzeiv4wh3df5atuwr23exwojjs6dcwle24kbi4yzraa3cm'
                        elif extension == 'tcl':
                            image_preview_hash = 'bafkreidambn4nta2gkivozc4y2g6w65hsygufnlynf4z4fvj75d63sei2q'
                        else:
                            image_preview_hash = None  # fallback to placeholder

                        # IPFS URIs
                        # https://beige-wooden-aardwolf-131.mypinata.cloud/ipfs/bafkreiclofpyxzeiv4wh3df5atuwr23exwojjs6dcwle24kbi4yzraa3cm
                        image_preview_ipfs_uri = f"{CUSTOM_GATEWAY}/ipfs/{image_preview_hash}" if image_preview_hash else PLACEHOLDER_IMAGE


                        metadata = {
                            "name":  f"📘Raiano - Building Files: {doc_to_mint.document_name}\n\n",
                            "description": (
                                f"📘 Engineering document for project: {doc_to_mint.project_name}\n\n"
                                f"📘 {doc_to_mint.description}\n\n"
                                f"🔗 View: {gateway_url}"
                            ),
                            "image": image_preview_ipfs_uri,
                            "animation_url": gateway_url,
                            "attributes": [
                                {"trait_type": "Project", "value": doc_to_mint.project_name},
                                {"trait_type": "Type", "value": extension.upper()},
                                {"trait_type": "Uploader", "value": "Engineer of Building Document Dossier"},
                                {"trait_type": "Upload Date", "value": doc_to_mint.uploaded_at.strftime('%Y-%m-%d')}
                            ]
                        }

                        metadata_hash = upload_json_to_ipfs(metadata, doc_to_mint.document_name)
                        token_uri = f"ipfs://{metadata_hash}"

                        doc_to_mint.token_uri = token_uri
                        session.add(doc_to_mint)
                        session.add(NFTMint(
                            role='engineer',
                            file_name=doc_to_mint.document_name,
                            ipfs_uri=token_uri,
                            token_id="",
                            contract_address=CONTRACT_ADDRESS,
                            minted_by=doc_to_mint.uploaded_by,
                            minted_at=datetime.now()
                        ))
                        session.commit()

                        ui.run_javascript(f"mintNFT('{token_uri}', 'Engineering Documentation')")
                        ui.notify(f"✅ NFT Minting started for {doc_to_mint.document_name}")

                    except Exception as e:
                        ui.notify(f"❌ Error: {str(e)}", color='negative')


                ui.button('🎯 Mint NFT', on_click=mint_this_document).classes('bg-blue-600 text-white px-3 py-1 rounded')

        # JavaScript for MetaMask minting (with purpose string)
        ui.add_body_html(f"""
        <script type="module">
        import {{ ethers }} from "https://cdn.jsdelivr.net/npm/ethers@5.7.2/dist/ethers.esm.min.js";
        window.mintNFT = async function(tokenUri, purpose) {{
            if (!window.ethereum) {{
                alert("❌ MetaMask is required!");
                return;
            }}
            const provider = new ethers.providers.Web3Provider(window.ethereum);
            await provider.send("eth_requestAccounts", []);
            const signer = provider.getSigner();
            const contract = new ethers.Contract("{CONTRACT_ADDRESS}", [
                {{
                    "inputs": [
                        {{"internalType": "address", "name": "recipient", "type": "address"}},
                        {{"internalType": "string", "name": "tokenURI", "type": "string"}},
                        {{"internalType": "string", "name": "purpose", "type": "string"}}
                    ],
                    "name": "mint",
                    "outputs": [{{"internalType": "uint256", "name": "", "type": "uint256"}}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }}
            ], signer);

            const userAddress = await signer.getAddress();
            const tx = await contract.mint(userAddress, tokenUri, purpose);
            const receipt = await tx.wait();
            alert("✅ NFT Minted! Tx Hash: " + receipt.transactionHash);
        }};
        </script>
        """)
