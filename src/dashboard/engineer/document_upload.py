from nicegui import ui
from src.auth.auth_roles import require_permission, get_user
import uuid
import json
import requests
from datetime import datetime
import os

PINATA_JWT = '.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIwN2QzZTM1NS1hMWE2LTQwMDktOWFhOC02NmEzODk0ZmQ2ZDQiLCJlbWFpbCI6ImFzaWZzYWVlZC5jc3BAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjQ0ZDQ2NTMzN2NhMDY1MjRkMjE5Iiwic2NvcGVkS2V5U2VjcmV0IjoiNzdiOWY5ZDgwMTQ1MzJhNjUzZTJmNjAzYThkZTAxYjc2NGJkMzhkYjhlNTFlY2IzNmJlYjFkOTQ0MmVlMDNkNCIsImV4cCI6MTc3NTA2NDYxOH0.JQXAqSzpQP2N9MaFjJhGmAqE7koaaVlugYcRFE-knFk'
PINATA_UPLOAD_URL = 'https://api.pinata.cloud/pinning/pinFileToIPFS'
PINATA_JSON_URL = 'https://api.pinata.cloud/pinning/pinJSONToIPFS'
DOCUMENTS_FILE = 'uploaded_documents.json'
CONTRACT_ADDRESS = ''

def load_documents():
    if not os.path.exists(DOCUMENTS_FILE):
        return []
    with open(DOCUMENTS_FILE, 'r') as f:
        return json.load(f)

def save_documents(documents):
    with open(DOCUMENTS_FILE, 'w') as f:
        json.dump(documents, f, indent=2)

def upload_file_to_ipfs(file_obj):
    headers = {
        'Authorization': f'Bearer {PINATA_JWT}',
    }
    files = {
        'file': (file_obj.name, file_obj.content.read(), file_obj.type),
    }
    response = requests.post(PINATA_UPLOAD_URL, headers=headers, files=files)
    if response.status_code == 200:
        return response.json()['IpfsHash']
    else:
        raise Exception(f"Failed to upload file to IPFS: {response.text}")

def upload_json_to_ipfs(metadata):
    headers = {
        'Authorization': f'Bearer {PINATA_JWT}',
        'Content-Type': 'application/json',
    }
    response = requests.post(PINATA_JSON_URL, headers=headers, json=metadata)
    if response.status_code == 200:
        return response.json()['IpfsHash']
    else:
        raise Exception(f"Failed to upload metadata to IPFS: {response.text}")

@require_permission('document_upload')
def document_upload():
    user = get_user()
    uploaded_file = {'file': None}
    document_list = ui.column().classes('w-full')
    preview_box = ui.column().classes('w-full')

    with ui.column().classes('w-full items-center p-8'):
        ui.label('📤 Upload Project Document').classes('text-2xl font-bold text-blue-900 mb-4')
        ui.label(f"Logged in as: {user['email']}").classes("text-sm text-blue-600 mb-4")

        doc = {
            'project_name': ui.input('Project Name').classes('w-full mb-2'),
            'document_name': ui.input('Document Name').classes('w-full mb-2'),
            'tags': ui.input('Tags (comma separated)').classes('w-full mb-2'),
            'description': ui.textarea('Description').classes('w-full mb-4'),
        }

        def on_file_upload(e):
            uploaded_file['file'] = e
            ui.notify(f"Selected file: {e.name}", color='info')

        ui.upload(
            label='Upload DWG File',
            multiple=False,
            on_upload=on_file_upload
        ).classes('w-full mb-4')

        def handle_submit():
            file = uploaded_file['file']
            if not file:
                ui.notify('Please upload a file.', color='negative')
                return

            try:
                ipfs_hash = upload_file_to_ipfs(file)
                file_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"

                metadata = {
                    "name": doc['document_name'].value,
                    "description": doc['description'].value,
                    "tags": doc['tags'].value,
                    "project": doc['project_name'].value,
                    "file": file_url,
                    "image": "https://via.placeholder.com/350x200.png?text=Document+Preview",  # Optional placeholder
                    "attributes": [
                        {"trait_type": "Uploader", "value": user['email']},
                        {"trait_type": "Size", "value": len(file.content.read())}
                    ]
                }

                metadata_hash = upload_json_to_ipfs(metadata)
                token_uri = f"ipfs://{metadata_hash}"

                file.content.seek(0)
                doc_id = str(uuid.uuid4())
                document = {
                    'id': doc_id,
                    'project_name': doc['project_name'].value,
                    'document_name': doc['document_name'].value,
                    'tags': doc['tags'].value,
                    'description': doc['description'].value,
                    'filename': file.name,
                    'size': len(file.content.read()),
                    'ipfs_hash': ipfs_hash,
                    'ipfs_url': file_url,
                    'token_uri': token_uri,
                    'uploaded_at': datetime.now().isoformat(),
                    'uploaded_by': user['email'],
                }

                documents = load_documents()
                documents.append(document)
                save_documents(documents)

                ui.notify('✅ Uploaded to IPFS! Now minting NFT via MetaMask...', color='positive')
                ui.run_javascript(f"mintNFT('{token_uri}')")

                preview_box.clear()
                with preview_box:
                    ui.label('🖼️ Preview Metadata').classes('text-lg font-bold text-blue-800')
                    ui.markdown(f"""
                        **Name:** {metadata['name']}  
                        **Description:** {metadata['description']}  
                        **Tags:** {metadata['tags']}  
                        **File:** [Open File]({file_url})  
                        **Metadata:** [View Metadata](https://gateway.pinata.cloud/ipfs/{metadata_hash})  
                    """)
                    ui.image(metadata['image']).style('max-width: 300px; margin-top: 10px')

                document_list.clear()
                with document_list:
                    ui.label('📚 Document NFT Gallery').classes('text-xl font-bold mt-8 text-blue-900')
                    for d in reversed(load_documents()):
                        with ui.card().classes('w-full'):
                            ui.markdown(f"""
                            **{d['document_name']}**  
                            *Project:* {d['project_name']}  
                            *Uploaded by:* {d['uploaded_by']}  
                            *Date:* {d['uploaded_at'].split('T')[0]}  
                            *[📄 View File]({d['ipfs_url']})* | *[🔗 Metadata]({d['token_uri'].replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')})*
                            """)

            except Exception as e:
                ui.notify(f"❌ Error: {str(e)}", color='negative')

        ui.button('Upload and Mint NFT', on_click=handle_submit).classes('bg-blue-600 text-white px-4 py-2 rounded-xl')

    # Inject the script once
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

