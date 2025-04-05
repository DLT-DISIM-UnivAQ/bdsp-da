
from nicegui import ui
from datetime import datetime
import base64, os, requests, json
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import EngineerDocument, NFTMint
from dotenv import load_dotenv


# ✅ Hardcoded for now
PINATA_JWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIwN2QzZTM1NS1hMWE2LTQwMDktOWFhOC02NmEzODk0ZmQ2ZDQiLCJlbWFpbCI6ImFzaWZzYWVlZC5jc3BAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjQ0ZDQ2NTMzN2NhMDY1MjRkMjE5Iiwic2NvcGVkS2V5U2VjcmV0IjoiNzdiOWY5ZDgwMTQ1MzJhNjUzZTJmNjAzYThkZTAxYjc2NGJkMzhkYjhlNTFlY2IzNmJlYjFkOTQ0MmVlMDNkNCIsImV4cCI6MTc3NTA2NDYxOH0.JQXAqSzpQP2N9MaFjJhGmAqE7koaaVlugYcRFE-knFk'
PINATA_UPLOAD_URL = 'https://api.pinata.cloud/pinning/pinFileToIPFS'
PINATA_JSON_URL = 'https://api.pinata.cloud/pinning/pinJSONToIPFS'
PLACEHOLDER_IMAGE = 'https://via.placeholder.com/300x300.png?text=Document'
CONTRACT_ADDRESS = '0x9238945EeEE12F466a7045d547303D90D5150831'
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
    payload = {
        "pinataMetadata": {"name": os.path.splitext(original_filename)[0]},
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

    documents = session.query(EngineerDocument)\
        .filter_by(uploaded_by=engineer_email)\
        .filter(EngineerDocument.token_uri == None).all()

    with ui.column().classes('w-full items-center p-8'):
        ui.label(f'🧪 Mint Engineering Documents - {user["email"]}').classes('text-2xl font-bold text-blue-800 mb-6')
        ui.label(f'📚 Engineer Documents - {user["email"]}').classes('text-2xl font-bold text-blue-800 mb-6')
        ui.button('⬅️ Back to Dashboard', on_click=lambda: ui.navigate.to('/dashboard/engineer')).classes('mb-4 bg-gray-200 px-4 py-2 rounded')
        ui.button('📄 Upload Document', on_click=lambda: ui.navigate.to('/engineer/upload')).classes('bg-green-100 text-green-800 px-4 py-2 rounded')
        ui.button('🔒 Logout', on_click=lambda: ui.navigate.to('/')).classes('bg-gray-500 text-white px-4 py-2 rounded')

        if not documents:
            ui.label('📂 No documents available for minting. Please upload first.').classes('text-gray-600')
            return

        for doc in documents:
            with ui.row().classes('w-full bg-white p-4 rounded shadow-md mb-4 items-center gap-6'):
                with ui.column().classes('grow'):
                    ui.label(f"📄 {doc.document_name}").classes('text-md font-semibold text-blue-900')
                    ui.label(f"📁 Project: {doc.project_name}").classes('text-sm text-gray-700')
                    ui.label(f"📝 {doc.description or 'No description provided'}").classes('text-sm text-gray-600')
                    ui.label(f"📅 Uploaded: {doc.uploaded_at.strftime('%Y-%m-%d')}").classes('text-xs text-gray-500')

                def mint_this_document(doc_to_mint=doc):
                    try:
                        # Extract IPFS hash and build custom gateway URL
                        if not doc_to_mint.ipfs_url or "ipfs/" not in doc_to_mint.ipfs_url:
                            ui.notify(f"❌ Document '{doc_to_mint.document_name}' has invalid IPFS URL.", color='negative')
                            return

                        ipfs_hash = doc_to_mint.ipfs_url.split("/")[-1]
                        fixed_url = f"{CUSTOM_GATEWAY}/{ipfs_hash}"

                        file_bytes = requests.get(fixed_url).content
                        file_ipfs_hash = upload_file_to_ipfs_bytes(file_bytes, doc_to_mint.document_name)
                        file_ipfs_uri = f"ipfs://{file_ipfs_hash}"

                        metadata = {
                            "name": doc_to_mint.document_name,
                            "description": doc_to_mint.description or "Engineer submitted file",
                            "external_url": file_ipfs_uri,
                            "image": PLACEHOLDER_IMAGE,
                            "attributes": [
                                {"trait_type": "Project", "value": doc_to_mint.project_name},
                                {"trait_type": "Uploader", "value": doc_to_mint.uploaded_by},
                                {"trait_type": "File", "value": doc_to_mint.document_name},
                            ]
                        }

                        metadata_hash = upload_json_to_ipfs(metadata, doc_to_mint.document_name)
                        token_uri = f"ipfs://{metadata_hash}"

                        # Update DB
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

                        ui.run_javascript(f"mintNFT('{token_uri}')")
                        ui.notify(f"✅ NFT Minting started for {doc_to_mint.document_name}", color='positive')

                    except Exception as e:
                        ui.notify(f"❌ Error: {str(e)}", color='negative')

                ui.button('🎯 Mint NFT', on_click=mint_this_document).classes('bg-blue-600 text-white px-3 py-1 rounded')

        # Inject MetaMask minting script
        ui.add_body_html(f"""
        <script type="module">
        import {{ ethers }} from "https://cdn.jsdelivr.net/npm/ethers@5.7.2/dist/ethers.esm.min.js";
        window.mintNFT = async function(tokenUri) {{
            if (!window.ethereum) {{
                alert("❌ MetaMask is required!"); return;
            }}
            const provider = new ethers.providers.Web3Provider(window.ethereum);
            await provider.send("eth_requestAccounts", []);
            const signer = provider.getSigner();
            const contract = new ethers.Contract("{CONTRACT_ADDRESS}", [
                {{
                    "inputs": [
                        {{ "internalType": "address", "name": "recipient", "type": "address" }},
                        {{ "internalType": "string", "name": "tokenURI", "type": "string" }}
                    ],
                    "name": "mint",
                    "outputs": [{{ "internalType": "uint256", "name": "", "type": "uint256" }}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }}
            ], signer);
            try {{
                const tx = await contract.mint(await signer.getAddress(), tokenUri);
                const receipt = await tx.wait();
                alert("✅ NFT Minted! Tx Hash: " + receipt.transactionHash);
            }} catch (err) {{
                alert("❌ Minting failed: " + err.message);
            }}
        }};
        </script>
        """)
