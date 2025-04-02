from nicegui import ui
from datetime import datetime
import os
import uuid
import json
import requests
from dotenv import load_dotenv

PINATA_JWT = os.getenv('PINATA_JWT')
PINATA_UPLOAD_URL = os.getenv('PINATA_UPLOAD_URL')
PINATA_JSON_URL = os.getenv('PINATA_JSON_URL')
DOCUMENTS_FILE = os.getenv('DOCUMENTS_FILE')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
PLACEHOLDER_IMAGE = os.getenv('PLACEHOLDER_IMAGE')

load_dotenv()

def load_documents():
    if not os.path.exists(DOCUMENTS_FILE):
        return []
    with open(DOCUMENTS_FILE, 'r') as f:
        return json.load(f)


def save_documents(documents):
    with open(DOCUMENTS_FILE, 'w') as f:
        json.dump(documents, f, indent=2)


def upload_file_to_ipfs(file_obj):
    print(PINATA_JWT)
    print(PINATA_JSON_URL)
    print(DOCUMENTS_FILE)
    print(PLACEHOLDER_IMAGE)
    headers = {'Authorization': f'Bearer {PINATA_JWT}'}
    files = {'file': (file_obj.name, file_obj.content.read(), file_obj.type)}
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


def document_upload():
    uploaded_file = {'file': None}
    preview_box = ui.column().classes('w-full')
    document_list = ui.column().classes('w-full')

    with ui.column().classes('w-full items-center p-8'):
        ui.label('📤 Upload Project Document').classes('text-2xl font-bold text-blue-900 mb-4')

        doc = {
            'project_name': ui.input('Project Name').classes('w-full mb-2'),
            'document_name': ui.input('Document Name').classes('w-full mb-2'),
            'tags': ui.input('Tags (comma separated)').classes('w-full mb-2'),
            'description': ui.textarea('Description').classes('w-full mb-4'),
        }

        def on_file_upload(e):
            uploaded_file['file'] = e
            ui.notify(f"Selected file: {e.name}", color='info')

        ui.upload(label='Upload DWG or Engineering File', multiple=False, on_upload=on_file_upload).classes('w-full mb-4')

        def handle_submit():
            file = uploaded_file['file']
            if not file:
                ui.notify('Please upload a file.', color='negative')
                return

            try:
                file.content.seek(0)
                file_ipfs_hash = upload_file_to_ipfs(file)
                file_ipfs_url = f"https://beige-wooden-aardwolf-131.mypinata.cloud/ipfs/{file_ipfs_hash}"
                file_ipfs_uri = f"ipfs://{file_ipfs_hash}"

                metadata = {
                    "name": doc['document_name'].value,
                    "description": doc['description'].value,
                    "external_url": file_ipfs_uri,
                    "image": PLACEHOLDER_IMAGE,
                    "attributes": [
                        {"trait_type": "Project", "value": doc['project_name'].value},
                        {"trait_type": "Tags", "value": doc['tags'].value},
                        {"trait_type": "Uploader", "value": "engineer@example.com"},
                        {"trait_type": "File Name", "value": file.name},
                    ]
                }

                metadata_hash = upload_json_to_ipfs(metadata)
                token_uri = f"ipfs://{metadata_hash}"
                metadata_url = f"https://beige-wooden-aardwolf-131.mypinata.cloud/ipfs/{metadata_hash}"

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
                    'ipfs_url': file_ipfs_url,
                    'token_uri': token_uri,
                    'uploaded_at': datetime.now().isoformat(),
                    'uploaded_by': "engineer@example.com",
                }

                documents = load_documents()
                documents.append(document)
                save_documents(documents)

                preview_box.clear()
                with preview_box:
                    ui.label('🖼️ NFT Preview').classes('text-lg font-bold text-blue-800')
                    ui.markdown(f"""
                        **Name:** {metadata['name']}  
                        **Project:** {doc['project_name'].value}  
                        **Description:** {metadata['description']}  
                        **File:** [Open IPFS File]({file_ipfs_url})  
                        **Metadata:** [View JSON Metadata]({metadata_url})  
                    """)
                    ui.image(metadata['image']).style('max-width: 300px; margin-top: 10px')

                ui.run_javascript(f"mintNFT('{token_uri}')")
                ui.notify('✅ File uploaded, metadata created, NFT minting triggered!', color='positive')

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
                            *[📄 File]({d['ipfs_url']})* | *[🔗 Metadata]({d['token_uri'].replace('ipfs://', 'https://beige-wooden-aardwolf-131.mypinata.cloud/ipfs/')})*
                            """)

            except Exception as e:
                ui.notify(f"❌ Error: {str(e)}", color='negative')

        ui.button('Upload and Mint NFT', on_click=handle_submit).classes('bg-blue-600 text-white px-4 py-2 rounded-xl')

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


document_upload()
