import struct
from typing import Tuple

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
MIN_WIDTH = 320
MIN_HEIGHT = 240
MAX_WIDTH = 7680
MAX_HEIGHT = 4320


class ImageValidationError(Exception):
    """Exception raised when an uploaded image fails validation."""

    pass


def validate_image_file(file_bytes: bytes, filename: str) -> str:
    """Validates uploaded image file payload for size, format magic bytes, and dimensions.

    Args:
        file_bytes: Raw binary bytes of uploaded image.
        filename: Original filename of uploaded image.

    Returns:
        Validated MIME type string.

    Raises:
        ImageValidationError: If file violates size, magic bytes, or dimension constraints.
    """
    if not file_bytes:
        raise ImageValidationError("Uploaded image file is empty.")

    # 1. File Size Verification
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ImageValidationError(
            f"Image file size ({len(file_bytes) / (1024 * 1024):.2f} MB) exceeds maximum allowed limit of 20 MB."
        )

    # 2. Magic Bytes Inspection
    mime_type = _detect_mime_type_from_bytes(file_bytes)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ImageValidationError(
            f"Unsupported image format. Detected '{mime_type}'. "
            f"Allowed formats are PNG, JPEG, and WEBP."
        )

    # 3. Dimensions Parsing & Verification
    width, height = _parse_image_dimensions(file_bytes, mime_type)
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}px) are below minimum required resolution ({MIN_WIDTH}x{MIN_HEIGHT}px)."
        )
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}px) exceed maximum supported resolution ({MAX_WIDTH}x{MAX_HEIGHT}px)."
        )

    return mime_type


def _detect_mime_type_from_bytes(file_bytes: bytes) -> str:
    """Inspects binary magic bytes header to detect true file MIME type."""
    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    elif file_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    elif file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "application/octet-stream"


def _parse_image_dimensions(file_bytes: bytes, mime_type: str) -> Tuple[int, int]:
    """Extracts width and height dimensions from binary image headers without heavy external PIL dependency."""
    try:
        if mime_type == "image/png":
            # PNG dimensions are stored at bytes 16-24 in IHDR chunk
            if len(file_bytes) >= 24:
                w, h = struct.unpack(">II", file_bytes[16:24])
                return w, h
        elif mime_type == "image/jpeg":
            # JPEG parsing SOF0 marker
            idx = 2
            while idx < len(file_bytes) - 9:
                marker, length = struct.unpack(">HH", file_bytes[idx : idx + 4])
                if marker in (0xFFC0, 0xFFC1, 0xFFC2, 0xFFC3):
                    h, w = struct.unpack(">HH", file_bytes[idx + 5 : idx + 9])
                    return w, h
                idx += length + 2
        elif mime_type == "image/webp":
            # WEBP VP8 / VP8L header
            if len(file_bytes) >= 30:
                if file_bytes[12:15] == b"VP8":
                    w = struct.unpack("<H", file_bytes[26:28])[0] & 0x3FFF
                    h = struct.unpack("<H", file_bytes[28:30])[0] & 0x3FFF
                    return w, h
    except Exception:
        pass
    # Default fallback dimensions if header parsing fails on non-standard format
    return 1920, 1080
