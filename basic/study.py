import os
import httpx
from typing import Optional, Dict, Any


def get_studies(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    name: Optional[str] = None,
    uuid: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve a list of patient studies with optional filtering and pagination.
    
    This function helps you explore and manage patient studies in your system.
    Use pagination for large datasets and filters to find specific studies.
    
    Args:
        page: Page number for pagination (optional)
        page_size: Number of studies per page (optional) 
        name: Filter by patient name (optional)
        uuid: Filter by specific study UUID (optional)
    
    Returns:
        Dict with 'results' containing study data and pagination info
    
    Example:
        # Get the first 10 studies
        studies = get_studies(page_size=10)
        print(f"Found {studies['count']} total studies")
        
        for study in studies['results']:
            print(f"Patient: {study['name']}, Age: {study['age']}")
            print(f"  Study UUID: {study['uuid']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {}
    if page:
        params["page"] = page
    if page_size:
        params["page_size"] = page_size
    if name:
        params["name"] = name
    if uuid:
        params["uuid"] = uuid
    
    response = httpx.get(
        f"{api_url}/api/v2/studies/",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()


def create_study(
    age: int,
    name: Optional[str] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    sex: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new patient study to organize DICOMs and analysis results.
    
    A study represents a patient and serves as the container for DICOM files,
    scans, and analysis reports. This is the first step in any Encephalon workflow.
    
    Args:
        age: Patient age in years (required)
        name: Patient name or identifier (optional but recommended)
        height: Patient height in inches (optional)
        weight: Patient weight in pounds (optional)  
        sex: Patient sex - "MALE" or "FEMALE" (optional)
    
    Returns:
        Dict containing the created study with UUID and patient information
    
    Example:
        # Create a comprehensive patient study
        study = create_study(
            name="John Doe",
            age=45,
            height=72,  # inches
            weight=180,  # pounds
            sex="MALE"
        )
        print(f"Created study with UUID: {study['uuid']}")
        
        # Save the UUID - you'll need it for uploading DICOMs
        study_uuid = study['uuid']
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {"age": age}
    if name:
        data["name"] = name
    if height:
        data["height"] = height
    if weight:
        data["weight"] = weight
    if sex:
        data["sex"] = sex
    
    response = httpx.post(
        f"{api_url}/api/v2/studies/",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    return response.json()


def get_study(uuid: str) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific patient study.
    
    Use this function to get complete study details including patient demographics,
    creation timestamps, and associated metadata.
    
    Args:
        uuid: The unique identifier of the study
    
    Returns:
        Dict containing complete study information and patient data
    
    Example:
        # Get comprehensive study details
        study = get_study("123e4567-e89b-12d3-a456-426614174000")
        print(f"Patient: {study['name']}")
        print(f"Age: {study['age']} years")
        print(f"Created: {study['created_at']}")
        print(f"Study UUID: {study['uuid']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/studies/{uuid}/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def update_study(uuid: str, **updates) -> Dict[str, Any]:
    """
    Update patient information in an existing study.
    
    Use this function to modify patient demographics or correct information
    after a study has been created. Only provide the fields you want to update.
    
    Args:
        uuid: The unique identifier of the study to update
        **updates: Keyword arguments for fields to update (name, age, height, weight, sex)
    
    Returns:
        Dict containing the updated study information
    
    Example:
        # Update specific patient information
        updated = update_study(
            "123e4567-e89b-12d3-a456-426614174000",
            name="Jane Doe",  # Corrected name
            weight=175        # Updated weight
        )
        print(f"Updated patient: {updated['name']}")
        print(f"New weight: {updated['weight']} lbs")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = httpx.patch(
        f"{api_url}/api/v2/studies/{uuid}/",
        headers=headers,
        json=updates
    )
    response.raise_for_status()
    return response.json()


def delete_study(uuid: str) -> None:
    """
    Permanently delete a patient study and all associated data.
    
    Warning: This action cannot be undone and will delete all DICOMs, scans,
    and reports associated with this study. Use with extreme caution.
    
    Args:
        uuid: The unique identifier of the study to delete
    
    Returns:
        None (raises exception if deletion fails)
    
    Example:
        # Only delete if you're absolutely sure
        study_uuid = "123e4567-e89b-12d3-a456-426614174000"
        
        # Optionally, get study details first to confirm
        study = get_study(study_uuid)
        print(f"About to delete study for {study['name']}")
        
        # Proceed with deletion
        delete_study(study_uuid)
        print("Study permanently deleted")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = httpx.delete(
        f"{api_url}/api/v2/studies/{uuid}/",
        headers=headers
    )
    response.raise_for_status()


