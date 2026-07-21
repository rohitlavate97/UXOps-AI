# Milestone 4: Screenshot Upload & Storage Engine

## Status
- [x] Defined `StorageProvider` abstraction interface with `LocalStorageProvider` and `S3StorageProvider` implementations in `backend/storage/provider.py`
- [x] Implemented binary magic bytes, file size, and minimum/maximum dimension validation in `backend/storage/validator.py`
- [x] Created `backend/storage/schemas.py` and `backend/storage/router.py` FastAPI endpoint routes
- [x] Mounted `storage_router` under `/api/v1` in `backend/main.py`
- [x] Added storage provider, image validation, upload API, and RBAC isolation tests in `backend/tests/test_storage.py`
- [x] Updated CHANGELOG.md and milestone tracking

## Tasks & Deliverables

### 1. Storage Provider Abstraction (`backend/storage/provider.py`)
* **`StorageProvider`**: Abstract base class defining `upload_file`, `get_presigned_upload_url`, `get_presigned_download_url`, `get_file`, and `delete_file`.
* **`LocalStorageProvider`**: Stores uploaded assets in local `/backend/uploads/` directory for development and testing.
* **`S3StorageProvider`**: Direct AWS S3 integration for production environments.

### 2. Image Validation Utility (`backend/storage/validator.py`)
* **Size Enforcement**: Rejects image payloads exceeding 20 MB.
* **Format Inspection**: Validates binary magic byte headers for `image/png`, `image/jpeg`, and `image/webp` (blocks spoofed `.png` text files).
* **Resolution Checking**: Validates image width and height bounds (Min: 320x240, Max: 7680x4320).

### 3. API Router Endpoints (`backend/storage/router.py`)
* `POST /api/v1/workspaces/{workspace_id}/audits/upload`: Uploads screenshot, validates format/dimensions, saves to object storage, and initializes an `Audit` record in `PENDING` state.
* `POST /api/v1/workspaces/{workspace_id}/audits/presigned-url`: Generates a pre-signed S3 upload URL for direct browser uploads.
* `GET /api/v1/workspaces/{workspace_id}/audits/{audit_id}`: Retrieves single audit status and signed screenshot access URL.

### 4. Automated Testing (`backend/tests/test_storage.py`)
* **Storage Provider Unit Tests**: Validated upload, retrieve, and delete file operations.
* **Image Validation Tests**: Verified valid PNG header handling and rejection of malicious/empty file payloads.
* **API Route Integration Tests**: Verified upload endpoint, pre-signed URL generation, and 403 Forbidden enforcement on unauthorized workspace access attempts.
