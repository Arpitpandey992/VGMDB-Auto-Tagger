import io
from PIL import Image


def compress_image_limit_max_width(raw_image_data: bytes, max_width: int = 800) -> bytes:
    image = Image.open(io.BytesIO(raw_image_data))
    image = image.convert("RGB")  # Remove transparency if present
    width, height = image.size

    if width > max_width:
        new_height = int(height * (max_width / width))
        image = image.resize((max_width, new_height), resample=Image.LANCZOS)

    imageData = io.BytesIO()
    image.save(imageData, format="JPEG", quality=70)
    return imageData.getvalue()
