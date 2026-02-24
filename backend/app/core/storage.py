import os
import uuid
from pathlib import Path

from app.config import settings


class LocalStorage:
    def __init__(self):
        self.base_path = Path(settings.STORAGE_LOCAL_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, data: bytes, filename: str, folder: str = "") -> str:
        ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{ext}"
        target_dir = self.base_path / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / unique_name
        file_path.write_bytes(data)
        return str(file_path.relative_to(self.base_path))

    async def get(self, path: str) -> bytes | None:
        file_path = self.base_path / path
        if file_path.exists():
            return file_path.read_bytes()
        return None

    async def delete(self, path: str) -> bool:
        file_path = self.base_path / path
        if file_path.exists():
            os.remove(file_path)
            return True
        return False


storage = LocalStorage()
