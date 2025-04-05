from nicegui import ui
from datetime import datetime
import os, base64, requests, json
from dotenv import load_dotenv
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import InstallerImage, NFTMint

load_dotenv()

# Configuration
PINATA_JWT = os.getenv('PINATA_JWT')
PINATA_UPLOAD_URL = os.getenv('PINATA_UPLOAD_URL')
PINATA_JSON_URL = os.getenv('PINATA_JSON_URL')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
CUSTOM_GATEWAY = 'https://beige-wooden-aardwolf-131.mypinata.cloud/ipfs'
PLACEHOLDER_IMAGE = 'https://via.placeholder.com/300x300.png?text=NFT'

def upload_file_to_ipfs_bytes(image_bytes, name):
    headers = {'Authorization': f'Bearer {PINATA_JWT}'}
    files = {'file': (name, image_bytes, 'image/jpeg')}
    res = requests.post(PINATA_UPLOAD_URL, headers=headers, files=files)
    if res.status_code == 200:
        return res.json()['IpfsHash']
    raise Exception(f"❌ IPFS Upload Failed: {res.text}")

def upload_json_to_ipfs(metadata, original_filename='metadata'):
    headers = {'Authorization': f'Bearer {PINATA_JWT}', 'Content-Type': 'application/json'}
    payload = {
        "pinataMetadata": {"name": os.path.splitext(original_filename)[0]},
        "pinataContent": metadata
    }
    res = requests.post(PINATA_JSON_URL, headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()['IpfsHash']
    raise Exception(f"❌ Metadata Upload Failed: {res.text}")

@require_permission('approve_images')
def director_approval():
    user = get_user()
    session = SessionLocal()
    images = session.query(InstallerImage).filter_by(submitted=True, approved=False).all()

    with ui.column().classes('w-full items-center p-8'):
        ui.label(f'📷 Mint Installer Image NFTs - {user["email"]}').classes('text-2xl font-bold text-blue-800 mb-6')
        ui.button('🏠 Back to Dashboard', on_click=lambda: ui.navigate.to('/dashboard/director')).classes('mb-4 bg-gray-700 text-white px-4 py-2 rounded')

        if not images:
            ui.label('No submissions available for approval.').classes('text-gray-600')
            return

        for img in images:
            with ui.row().classes('w-full gap-4 bg-white rounded shadow p-4 mb-4'):
                encoded = base64.b64encode(img.image_data).decode('utf-8') if img.image_data else ""
                image_preview = f"data:image/png;base64,{encoded}" if encoded else PLACEHOLDER_IMAGE
                ui.image(image_preview).classes('w-32 h-32 rounded shadow')

                with ui.column().classes('grow'):
                    ui.label(f"📍 Site: {img.site_name}").classes('text-md font-bold text-blue-900')
                    ui.label(f"📌 QR: {img.qr_text}").classes('text-sm text-gray-700')
                    ui.label(f"📡 GPS: {img.gps_lat}, {img.gps_lng}").classes('text-sm text-gray-600')
                    ui.label(f"📂 File: {img.image_name}").classes('text-sm text-gray-600')

                def approve_and_mint(image=img):
                    try:
                        ipfs_image_hash = upload_file_to_ipfs_bytes(image.image_data, image.image_name)
                        ipfs_image_uri = f"ipfs://{ipfs_image_hash}"
                        ipfs_image_url = f"{CUSTOM_GATEWAY}/{ipfs_image_hash}"

                        metadata = {
                            "name": image.image_name,
                            "description": f"Installation photo from site {image.site_name}",
                            "image": ipfs_image_uri,
                            "attributes": [
                                {"trait_type": "Site", "value": image.site_name},
                                {"trait_type": "QR Code", "value": image.qr_text},
                                {"trait_type": "GPS", "value": f"{image.gps_lat}, {image.gps_lng}"},
                                {"trait_type": "Uploaded By", "value": image.uploaded_by}
                            ]
                        }

                        metadata_hash = upload_json_to_ipfs(metadata, image.image_name)
                        token_uri = f"ipfs://{metadata_hash}"
                        metadata_url = f"{CUSTOM_GATEWAY}/{metadata_hash}"

                        # Update DB
                        image.ipfs_url = ipfs_image_url
                        image.token_uri = token_uri
                        image.approved = True
                        image.submitted = False
                        image.approved_by = user['email']
                        image.approval_time = datetime.now()

                        session.add(NFTMint(
                            role="director",
                            file_name=image.image_name,
                            ipfs_uri=token_uri,
                            token_id="",
                            contract_address=CONTRACT_ADDRESS,
                            minted_by=image.approved_by,
                            minted_at=datetime.now()
                        ))
                        session.commit()

                        ui.run_javascript(f"mintNFT('{token_uri}', 'Director Approval')")
                        ui.notify(f"✅ NFT minting initiated for {image.image_name}")
                    except Exception as e:
                        ui.notify(f"❌ Error: {str(e)}", color='negative')

                ui.button('✅ Approve & Mint', on_click=approve_and_mint).classes('bg-blue-600 text-white px-4 py-2 rounded')

        # Inject Minting Script
        ui.add_body_html(f"""
        <script type="module">
        import {{ ethers }} from "https://cdn.jsdelivr.net/npm/ethers@5.7.2/dist/ethers.esm.min.js";
        window.mintNFT = async function(tokenUri, purpose) {{
            if (!window.ethereum) {{
                alert("❌ MetaMask is required."); return;
            }}

            const provider = new ethers.providers.Web3Provider(window.ethereum);
            await provider.send("eth_requestAccounts", []);
            const signer = provider.getSigner();

            const abi = [
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
            ];

            const contract = new ethers.Contract("{CONTRACT_ADDRESS}", abi, signer);
            const address = await signer.getAddress();

            try {{
                const gasEstimate = await contract.estimateGas.mint(address, tokenUri, purpose);
                const tx = await contract.mint(address, tokenUri, purpose, {{
                    gasLimit: gasEstimate.mul(120).div(100)
                }});
                const receipt = await tx.wait();
                alert("✅ NFT Minted! Tx Hash: " + receipt.transactionHash);
            }} catch (err) {{
                console.error(err);
                alert("❌ Minting Failed: " + err.message);
            }}
        }};
        </script>
        """)
