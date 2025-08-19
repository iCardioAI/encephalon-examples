import os
import httpx
from typing import Optional, Dict, Any
from pathlib import Path


def upload_dicom(study_uuid: str, file_path: str) -> Dict[str, Any]:
    """
    Upload a DICOM file to an existing study to prepare for AI analysis.
    
    This function demonstrates how to attach medical imaging files to a patient study.
    The DICOM file will be processed by the Encephalon API for cardiac analysis once
    you create a scan for this study.
    
    Args:
        study_uuid: The UUID of the study to upload the DICOM to
        file_path: Path to the DICOM file on your local system
    
    Returns:
        Dict containing the uploaded DICOM's metadata including UUID, name, and study info
    
    Example:
        # Upload a DICOM file to an existing study
        dicom = upload_dicom(
            "123e4567-e89b-12d3-a456-426614174000",
            "plax_example.dcm"
        )
        print(f"Uploaded DICOM with UUID: {dicom['uuid']}")
        print(f"File name: {dicom['name']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(file_path, 'rb') as f:
        files = {
            'file': (Path(file_path).name, f, 'application/dicom'),
            'study': (None, study_uuid)
        }
        
        response = httpx.post(
            f"{api_url}/api/v2/dicoms/",
            headers=headers,
            files=files
        )
    
    response.raise_for_status()
    return response.json()


def get_dicoms(
    study_uuid: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve a list of DICOM files, optionally filtered by study.
    
    This function helps you explore and manage the DICOM files in your system.
    Use it to verify uploads, check file counts, or list all DICOMs for a specific study.
    
    Args:
        study_uuid: Filter to only show DICOMs from this study (optional)
        page: Page number for pagination (optional)
        page_size: Number of items per page (optional)
    
    Returns:
        Dict with 'results' containing DICOM metadata and 'count' showing total files
    
    Example:
        # Get all DICOMs for a specific study
        dicoms = get_dicoms(study_uuid="123e4567-e89b-12d3-a456-426614174000")
        print(f"Study has {dicoms['count']} DICOM files")
        
        for dicom in dicoms['results']:
            print(f"DICOM: {dicom['name']} (UUID: {dicom['uuid']})")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {}
    if study_uuid:
        params["study"] = study_uuid
    if page:
        params["page"] = page
    if page_size:
        params["page_size"] = page_size
    
    response = httpx.get(
        f"{api_url}/api/v2/dicoms/",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()


def get_dicom(uuid: str) -> Dict[str, Any]:
    """
    Retrieve detailed metadata for a specific DICOM file.
    
    Use this function when you need detailed information about a particular DICOM file,
    including its properties, upload status, and associated study information.
    
    Args:
        uuid: The unique identifier of the DICOM file
    
    Returns:
        Dict containing complete DICOM metadata including name, size, and study details
    
    Example:
        # Get detailed information about a specific DICOM
        dicom = get_dicom("456e7890-e89b-12d3-a456-426614174000")
        print(f"DICOM name: {dicom['name']}")
        print(f"File size: {dicom.get('file_size', 'Unknown')}")
        print(f"Study: {dicom['study']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/dicoms/{uuid}/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def download_dicom_file(uuid: str, filename: str, output_path: str) -> str:
    """
    Download the actual DICOM file data to your local filesystem.
    
    This function retrieves the binary DICOM file content, which is useful for
    local analysis, backup, or integration with other medical imaging tools.
    
    Args:
        uuid: The unique identifier of the DICOM file
        filename: The desired filename for the downloaded file
        output_path: Directory where the file should be saved
    
    Returns:
        String path to the downloaded file
    
    Example:
        # Download a DICOM file for local processing
        file_path = download_dicom_file(
            "456e7890-e89b-12d3-a456-426614174000",
            "patient_echo.dcm",
            "/local/dicom/storage/"
        )
        print(f"Downloaded to: {file_path}")
        
        # Now you can process the file locally if needed
        with open(file_path, 'rb') as f:
            dicom_data = f.read()
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/dicoms/file/{uuid}/{filename}/",
        headers=headers,
        follow_redirects=True
    )
    response.raise_for_status()
    
    output_file = Path(output_path) / filename
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'wb') as f:
        f.write(response.content)
    
    return str(output_file)


def delete_dicom(uuid: str) -> None:
    """
    Permanently delete a DICOM file from the system.
    
    Use this function carefully to remove DICOM files that are no longer needed.
    Note that this action cannot be undone, so ensure you have backups if necessary.
    
    Args:
        uuid: The unique identifier of the DICOM file to delete
    
    Returns:
        None (raises exception if deletion fails)
    
    Example:
        # Delete a DICOM file that's no longer needed
        delete_dicom("456e7890-e89b-12d3-a456-426614174000")
        print("DICOM file successfully deleted")
        
        # Verify deletion by trying to retrieve it (should raise an error)
        try:
            get_dicom("456e7890-e89b-12d3-a456-426614174000")
        except httpx.HTTPStatusError:
            print("Confirmed: DICOM no longer exists")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = httpx.delete(
        f"{api_url}/api/v2/dicoms/{uuid}/",
        headers=headers
    )
    response.raise_for_status()


def idempotent_dicom_upload(file_path: str) -> Dict[str, Any]:
    """
    Upload a DICOM file with automatic study creation if needed.
    
    This is a convenient "one-shot" upload that will automatically create a patient study
    if the DICOM file doesn't already belong to one. This is useful for quick uploads
    where you want the system to handle study management automatically.
    
    Args:
        file_path: Path to the DICOM file on your local system
    
    Returns:
        Dict containing both the created study and DICOM information
    
    Example:
        # Quick upload that handles study creation automatically
        result = idempotent_dicom_upload("plax_example.dcm")
        print(f"Study UUID: {result['study']}")
        print(f"DICOM UUID: {result['uuid']}")
        
        # The result contains everything you need to proceed
        study_uuid = result['study']
        dicom_uuid = result['uuid']
        
        # Now you can create a scan using the auto-created study
        from basic.scan import create_scan
        scan = create_scan(study_uuid)
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(file_path, 'rb') as f:
        files = {
            'file': (Path(file_path).name, f, 'application/dicom')
        }
        
        response = httpx.post(
            f"{api_url}/api/v2/idempotent_dicom/",
            headers=headers,
            files=files
        )
    
    response.raise_for_status()
    return response.json()