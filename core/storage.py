import os
import requests
import cloudinary.uploader
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.base import ContentFile


class BoundedCloudinaryStorage(MediaCloudinaryStorage):
    """Avoid unbounded HTTP waits during upload and report generation."""
    def _open(self, name, mode='rb'):
        with requests.get(self.url(name), timeout=(3, 8), stream=True) as response:
            response.raise_for_status()
            chunks, size = [], 0
            for chunk in response.iter_content(65536):
                size += len(chunk)
                if size > 8 * 1024 * 1024:
                    raise OSError('Stored image exceeds download limit')
                chunks.append(chunk)
        return ContentFile(b''.join(chunks), name=name)

    def _upload(self, name, content):
        return cloudinary.uploader.upload(content, use_filename=True, resource_type='image',
                                          folder=os.path.dirname(name), tags=self.TAG, timeout=12)
