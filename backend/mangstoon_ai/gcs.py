"""GCS upload utility for panel images."""

from google.cloud import storage

BUCKET_NAME = "mangstoon-panels"
_client: storage.Client | None = None


def _get_client() -> storage.Client:
    global _client
    if _client is None:
        _client = storage.Client()
    return _client


def upload_panel(session_id: str, filename: str, data: bytes) -> str:
    """Upload panel image to GCS and return public URL.

    Args:
        session_id: Session identifier (used as folder prefix).
        filename: e.g. "panel_01.png"
        data: Raw PNG bytes.

    Returns:
        Public URL like https://storage.googleapis.com/mangstoon-panels/abc123/panel_01.png
    """
    client = _get_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{session_id}/{filename}")
    blob.upload_from_string(data, content_type="image/png")
    return blob.public_url
