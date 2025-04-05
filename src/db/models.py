# models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base
import datetime
from sqlalchemy import LargeBinary


Base = declarative_base()

# Table for engineers
class EngineerDocument(Base):
    __tablename__ = 'engineer_documents'

    id = Column(Integer, primary_key=True)
    project_name = Column(String)
    document_name = Column(String)
    file_name = Column(String)
    file_type = Column(String)
    file_data = Column(LargeBinary)  # Binary file content
    description = Column(Text)
    tags = Column(String)
    ipfs_url = Column(String, nullable=True)
    token_uri = Column(String, nullable=True)
    uploaded_by = Column(String)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    minted = Column(String, default='No')  # 'Yes' or 'No'


class InstallerImage(Base):
    __tablename__ = 'installer_images'

    id = Column(Integer, primary_key=True)
    site_name = Column(String)
    image_name = Column(String)
    ipfs_url = Column(String, nullable=True)
    uploaded_by = Column(String)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    image_data = Column(LargeBinary, nullable=True)

    # Metadata
    qr_text = Column(String)
    gps_lat = Column(String)
    gps_lng = Column(String)
    notes = Column(Text)

    # Approval Info
    approved = Column(Boolean, default=False)
    approved_by = Column(String, nullable=True)
    approval_time = Column(DateTime, nullable=True)

    # Submission flag
    submitted = Column(Boolean, default=False)


# Optional NFT table (if you want to track all minted items)
class NFTMint(Base):
    __tablename__ = 'nft_mints'
    id = Column(Integer, primary_key=True)
    role = Column(String)  # "engineer" or "director"
    file_name = Column(String)
    ipfs_uri = Column(String)
    token_id = Column(String)
    contract_address = Column(String)
    minted_by = Column(String)
    minted_at = Column(DateTime, default=datetime.datetime.utcnow)
