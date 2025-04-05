from nicegui import ui
from datetime import datetime
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import InstallerImage
import base64, os, uuid, requests, json
from dotenv import load_dotenv
from src.db.models import NFTMint  # make sure this import is at the top


# Load environment variables
load_dotenv()
PINATA_JWT = os.getenv('PINATA_JWT')
PINATA_UPLOAD_URL = os.getenv('PINATA_UPLOAD_URL')
PINATA_JSON_URL = os.getenv('PINATA_JSON_URL')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
PLACEHOLDER_IMAGE = os.getenv('PLACEHOLDER_IMAGE')

# Upload file (image bytes) to IPFS
def upload_file_to_ipfs_bytes(image_bytes, name):
    headers = {'Authorization': f'Bearer {PINATA_JWT}'}
    files = {'file': (name, image_bytes, 'image/jpeg')}
    response = requests.post(PINATA_UPLOAD_URL, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()['IpfsHash']
    else:
        raise Exception(response.text)

# Upload metadata JSON to IPFS
def upload_json_to_ipfs(metadata, original_filename='metadata'):
    headers = {
        'Authorization': f'Bearer {PINATA_JWT}',
        'Content-Type': 'application/json'
    }
    filename = os.path.splitext(original_filename)[0] + 'JSON'
    payload = {
        "pinataMetadata": {"name": filename},
        "pinataContent": metadata
    }
    response = requests.post(PINATA_JSON_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['IpfsHash']
    else:
        raise Exception(response.text)

# 🌐 Director Approval Panel
@require_permission('approve_images')
def director_approval():
    session = SessionLocal()
    submitted_images = session.query(InstallerImage).filter(
        InstallerImage.submitted == True,
        InstallerImage.approved == False
    ).all()

    with ui.column().classes('w-full items-center p-8'):
        ui.label('✅ Approve and Mint Installer Images').classes('text-2xl font-bold text-blue-800 mb-6')

        ui.button('🏠 Back to Dashboard', on_click=lambda: ui.navigate.to('/dashboard/director')).classes('mb-4 bg-gray-700 text-white px-4 py-2 rounded')

        if not submitted_images:
            ui.label('No submissions found.').classes('text-gray-600')
            return

        for img in submitted_images:
            with ui.row().classes('w-full gap-4 bg-white rounded shadow p-4 mb-2'):
                # Image display
                if img.image_data:
                    encoded = base64.b64encode(img.image_data).decode('utf-8')
                    image_url = f"data:image/png;base64,{encoded}"
                else:
                    image_url = PLACEHOLDER_IMAGE
                ui.image(image_url).classes('w-32 h-32 rounded shadow')

                # Info + Action
                with ui.column().classes('grow'):
                    ui.label(f"📍 Site: {img.site_name}").classes('text-md font-bold text-blue-900')
                    ui.label(f"🧾 QR: {img.qr_text} | 🌍 GPS: {img.gps_lat}, {img.gps_lng}").classes('text-sm text-gray-700')
                    ui.label(f"📂 File: {img.image_name}").classes('text-sm text-gray-600')

                    def approve_and_mint(image=img):
                        try:
                            image_bytes = image.image_data
                            ipfs_hash = upload_file_to_ipfs_bytes(image_bytes, image.image_name)
                            ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"

                            metadata = {
                                "name": image.image_name,
                                "description": f"Installation plate at {image.site_name}",
                                "image": f"ipfs://{ipfs_hash}",
                                "attributes": [
                                    {"trait_type": "QR Code", "value": image.qr_text},
                                    {"trait_type": "Location", "value": f"{image.gps_lat}, {image.gps_lng}"},
                                    {"trait_type": "Uploader", "value": image.uploaded_by}
                                ]
                            }

                            metadata_hash = upload_json_to_ipfs(metadata, image.image_name)
                            token_uri = f"ipfs://{metadata_hash}"

                            # Update DB
                            image.ipfs_url = ipfs_url
                            image.token_uri = token_uri
                            image.approved = True
                            image.submitted = False  # Reset submission status
                            image.approved_by = get_user()['email']
                            image.approval_time = datetime.now()
                            
                            mint_record = NFTMint(
                                role="director",
                                file_name=image.image_name,
                                ipfs_uri=token_uri,
                                token_id="",  # Optional: Fill from MetaMask tx if desired
                                contract_address=CONTRACT_ADDRESS,
                                minted_by=image.approved_by,
                                minted_at=datetime.now()
                            )
                            
                            session.add(mint_record)
                            session.commit()
                           
                            ui.run_javascript(f"mintNFT('{token_uri}')")
                            ui.notify(f'✅ NFT Minting initiated for {image.image_name}')

                        except Exception as e:
                            ui.notify(f'❌ Error: {str(e)}', color='negative')

                    ui.button('✅ Approve & Mint', on_click=approve_and_mint).classes('bg-blue-600 text-white px-4 py-2 rounded')

    # Inject JS for MetaMask minting
    ui.add_body_html(f"""
    <script type="module">
    import {{ ethers }} from "https://cdn.jsdelivr.net/npm/ethers@5.7.2/dist/ethers.esm.min.js";
    window.mintNFT = async function(tokenUri) {{
        if (!window.ethereum) {{
            alert("MetaMask is required!");
            return;
        }}
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        await provider.send("eth_requestAccounts", []);
        const signer = provider.getSigner();
        const userAddress = await signer.getAddress();
        const contractAddress = "{CONTRACT_ADDRESS}";
        const abi = [
            {{
                "inputs": [
                    {{ "internalType": "address", "name": "recipient", "type": "address" }},
                    {{ "internalType": "string", "name": "tokenURI", "type": "string" }}
                ],
                "name": "mint",
                "outputs": [
                    {{ "internalType": "uint256", "name": "", "type": "uint256" }}
                ],
                "stateMutability": "nonpayable",
                "type": "function"
            }}
        ];
        const contract = new ethers.Contract(contractAddress, abi, signer);
        try {{
            const tx = await contract.mint(userAddress, tokenUri);
            const receipt = await tx.wait();
            alert("✅ NFT Minted! Tx Hash: " + receipt.transactionHash);
        }} catch (err) {{
            console.error("Mint failed:", err);
            alert("❌ Minting failed: " + err.message);
        }}
    }};
    </script>
    """)
