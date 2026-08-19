from PIL import Image, ImageStat
import logging

logger = logging.getLogger(__name__)

def validate_and_preprocess_image(image_path_or_file):
    """
    Validates uploaded image format, dimensions, brightness, and sharpness.
    Returns dict: {'is_valid': bool, 'warning': str, 'processed_image': Image or None}
    """
    try:
        img = Image.open(image_path_or_file)
        img.verify()
        
        # Re-open for actual processing as verify() modifies file pointer state
        if hasattr(image_path_or_file, 'seek'):
            image_path_or_file.seek(0)
        img = Image.open(image_path_or_file)
        
        width, height = img.size
        if width < 80 or height < 80:
            return {
                'is_valid': False,
                'warning': 'Image resolution too low. Please upload a clear photo (at least 200x200 pixels).',
                'processed_image': None
            }

        # Check format
        if img.format.upper() not in ['JPEG', 'JPG', 'PNG', 'WEBP']:
            return {
                'is_valid': False,
                'warning': f'Unsupported format {img.format}. Please use JPG, PNG, or WEBP.',
                'processed_image': None
            }

        # Convert to RGB for lighting & contrast analysis
        rgb_img = img.convert('RGB')
        stat = ImageStat.Stat(rgb_img)

        # Average brightness (mean of R, G, B channels)
        avg_brightness = sum(stat.mean) / 3.0
        if avg_brightness < 25:
            return {
                'is_valid': True,
                'warning': 'Image appears very dark. Results might improve with better lighting.',
                'processed_image': rgb_img
            }
        elif avg_brightness > 245:
            return {
                'is_valid': True,
                'warning': 'Image appears overexposed/too bright.',
                'processed_image': rgb_img
            }

        # Sharpness / variance check for blur detection
        gray_img = img.convert('L')
        gray_stat = ImageStat.Stat(gray_img)
        std_dev = gray_stat.stddev[0]

        warning = None
        if std_dev < 12.0:
            warning = 'Photo appears blurry or lacks detail. A sharper close-up is recommended.'

        return {
            'is_valid': True,
            'warning': warning,
            'processed_image': rgb_img
        }

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return {
            'is_valid': False,
            'warning': 'Could not parse image file. Please upload a valid image.',
            'processed_image': None
        }
