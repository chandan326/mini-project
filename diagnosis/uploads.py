"""Decode before saving; never trust the filename or browser MIME type."""
from io import BytesIO
from uuid import uuid4
import warnings

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageOps
from rest_framework.exceptions import ValidationError


def collect_images(files):
    images = []
    for key, values in files.lists():
        if key not in ('images', 'images[]', 'image') and not key.startswith('image_'):
            raise ValidationError({'images': 'Use the images field for plant photos.'})
        images.extend(values)
    return images


def prepare_images(files):
    if not 1 <= len(files) <= settings.MAX_DIAGNOSIS_IMAGES:
        raise ValidationError({'images': 'Upload between 1 and 5 photos.'})
    if sum(f.size for f in files) > settings.MAX_UPLOAD_BYTES:
        raise ValidationError({'images': 'Combined photos must be below 4 MB. Use the photo picker to optimize them.'})
    prepared = []
    for index, upload in enumerate(files, 1):
        try:
            upload.seek(0)
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(upload) as source:
                    if source.format not in ('JPEG', 'PNG', 'WEBP'):
                        raise ValueError('Use JPG, PNG or WebP photos.')
                    width, height = source.size
                    if min(width, height) < 200:
                        raise ValueError('Photo must be at least 200 × 200 pixels.')
                    if width * height > 30_000_000:
                        raise ValueError('Photo resolution is too large; resize it before uploading.')
                    source.verify()
                upload.seek(0)
                with Image.open(upload) as source:
                    image = ImageOps.exif_transpose(source).convert('RGB')
                    image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                    buf = BytesIO()
                    image.save(buf, format='JPEG', quality=85, optimize=True)
                    image.close()
            prepared.append(SimpleUploadedFile(f'{uuid4().hex}.jpg', buf.getvalue(), 'image/jpeg'))
        except (OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            message = str(exc) if isinstance(exc, ValueError) else 'File is not a readable plant photo.'
            raise ValidationError({'images': f'Photo {index}: {message}'}) from exc
        finally:
            upload.seek(0)
    return prepared
