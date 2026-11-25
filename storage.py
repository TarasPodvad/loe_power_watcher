"""Tiny key/value state: Azure Blob when running in Azure, local files otherwise."""
import os

from config import DATA_DIR, IN_AZURE

CONTAINER = "loe-state"
_conn = os.getenv("AzureWebJobsStorage", "")
_USE_BLOB = _conn.startswith("DefaultEndpointsProtocol") or "AccountName=" in _conn
if IN_AZURE and not _USE_BLOB:
    # in Azure, temp-file state would silently reset -> refuse to run
    raise RuntimeError("AzureWebJobsStorage must be a connection string in Azure")


def _blob(name):
    from azure.storage.blob import BlobServiceClient

    svc = BlobServiceClient.from_connection_string(_conn)
    cont = svc.get_container_client(CONTAINER)
    if not cont.exists():
        cont.create_container()
    return cont.get_blob_client(name)


def get_text(name: str) -> str | None:
    if _USE_BLOB:
        b = _blob(name)
        return b.download_blob().readall().decode() if b.exists() else None
    p = DATA_DIR / name
    return p.read_text() if p.exists() else None


def put_text(name: str, value: str) -> None:
    if _USE_BLOB:
        _blob(name).upload_blob(value.encode(), overwrite=True)
    else:
        (DATA_DIR / name).write_text(value)
