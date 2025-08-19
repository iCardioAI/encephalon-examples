import os
import httpx
import time
from typing import Optional, Dict, Any


def create_scan(study_uuid: str, product: Optional[str] = None) -> Dict[str, Any]:
    """
    Trigger AI analysis by creating a scan for a study with uploaded DICOMs.
    
    This is the key function that starts the Encephalon AI analysis process.
    The study must already contain DICOM files before calling this function.
    
    Args:
        study_uuid: The UUID of the study containing DICOM files to analyze
        product: One of ECHOMEASURE, CARDIOVISION, ECHOGPT, or MITRALVISION 
                (defaults to ECHOMEASURE if not specified)
    
    Returns:
        Dict containing scan information including UUID, status, and product type
    
    Example:
        # Create a scan to start AI analysis with default product (ECHOMEASURE)
        scan = create_scan("123e4567-e89b-12d3-a456-426614174000")
        print(f"Started analysis with scan UUID: {scan['uuid']}")
        print(f"Product: {scan['product']}")
        print(f"Initial status: {scan['status']}")  # Usually 'PENDING'
        
        # Create a scan with a specific product
        scan = create_scan(
            "123e4567-e89b-12d3-a456-426614174000", 
            product="CARDIOVISION"
        )
        
        # Save the scan UUID for monitoring progress
        scan_uuid = scan['uuid']
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {"study": study_uuid}
    
    # Add product to request data if specified
    if product:
        data["product"] = product
    
    response = httpx.post(
        f"{api_url}/api/v2/scans/",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    return response.json()


def get_scans(
    study_uuid: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve a list of AI analysis scans with optional filtering.
    
    Use this function to monitor multiple scans, check analysis history,
    or find scans for a specific study.
    
    Args:
        study_uuid: Filter to only show scans from this study (optional)
        page: Page number for pagination (optional)
        page_size: Number of scans per page (optional)
    
    Returns:
        Dict with 'results' containing scan data and pagination info
    
    Example:
        # Get all scans for a specific study
        scans = get_scans(study_uuid="123e4567-e89b-12d3-a456-426614174000")
        print(f"Found {scans['count']} scans for this study")
        
        for scan in scans['results']:
            print(f"Scan {scan['uuid']}: {scan['status']}")
            if scan['status'] == 'COMPLETED':
                print(f"  Report available: {scan['report']}")
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
        f"{api_url}/api/v2/scans/",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()


def get_scan(uuid: str) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific AI analysis scan.
    
    Use this function to check the current status of a scan, monitor progress,
    or get analysis results when the scan completes.
    
    Args:
        uuid: The unique identifier of the scan
    
    Returns:
        Dict containing complete scan information including status and results
    
    Example:
        # Check the current status of a scan
        scan = get_scan("456e7890-e89b-12d3-a456-426614174000")
        print(f"Status: {scan['status']}")  # PENDING, STARTED, COMPLETED, FAILED
        print(f"Product: {scan['product']}")
        
        # If completed, access the analysis results
        if scan['status'] == 'COMPLETED':
            print(f"Analysis complete! Report UUID: {scan['report']}")
            print(f"Processing time: {scan['total_inference_time']}")
            print(f"DICOMs analyzed: {scan['number_of_dicoms_scanned']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/scans/{uuid}/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def delete_scan(uuid: str) -> None:
    """
    Permanently delete a scan and its associated analysis results.
    
    Warning: This will delete the scan and its analysis report permanently.
    Use carefully, especially if the analysis results are needed.
    
    Args:
        uuid: The unique identifier of the scan to delete
    
    Returns:
        None (raises exception if deletion fails)
    
    Example:
        # Delete a scan that's no longer needed
        scan_uuid = "456e7890-e89b-12d3-a456-426614174000"
        
        # Optionally check status first
        scan = get_scan(scan_uuid)
        print(f"Deleting scan with status: {scan['status']}")
        
        delete_scan(scan_uuid)
        print("Scan permanently deleted")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = httpx.delete(
        f"{api_url}/api/v2/scans/{uuid}/",
        headers=headers
    )
    response.raise_for_status()


def wait_for_scan_completion(
    scan_uuid: str,
    timeout: int = 300,
    poll_interval: int = 5
) -> Dict[str, Any]:
    """
    Monitor a scan until completion using the polling approach (Flow 1).
    
    This function implements the polling pattern for monitoring AI analysis progress.
    It's ideal for interactive applications where you want to show real-time progress
    to users. For server-to-server integration, consider using webhooks instead.
    
    Args:
        scan_uuid: The unique identifier of the scan to monitor
        timeout: Maximum time to wait in seconds (default: 300 = 5 minutes)
        poll_interval: How often to check status in seconds (default: 5)
    
    Returns:
        Dict containing the final scan status and results
    
    Raises:
        TimeoutError: If scan doesn't complete within timeout period
    
    Example:
        # Wait for analysis to complete with custom timeout
        scan = wait_for_scan_completion(
            "456e7890-e89b-12d3-a456-426614174000",
            timeout=600,  # 10 minutes
            poll_interval=10  # Check every 10 seconds
        )
        
        if scan['status'] == 'COMPLETED':
            print(f"Analysis completed! Report: {scan['report']}")
            print(f"Total time: {scan['total_inference_time']}")
        else:
            print(f"Analysis failed with status: {scan['status']}")
    """
    start_time = time.time()
    
    while True:
        scan = get_scan(scan_uuid)
        status = scan['status']
        
        if status in ['COMPLETED', 'FAILED']:
            return scan
        
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Scan {scan_uuid} did not complete within {timeout} seconds")
        
        time.sleep(poll_interval)


def get_scan_progress(scan_uuid: str) -> Dict[str, Any]:
    """
    Get detailed progress information for monitoring scan analysis.
    
    This function provides the same data as get_scan() but with a focus on
    progress monitoring. Use it to build progress indicators in your UI.
    
    Args:
        scan_uuid: The unique identifier of the scan to check
    
    Returns:
        Dict containing scan progress and performance metrics
    
    Example:
        # Monitor detailed scan progress
        progress = get_scan_progress("456e7890-e89b-12d3-a456-426614174000")
        print(f"Status: {progress['status']}")
        print(f"Available DICOMs: {progress['number_of_available_dicoms']}")
        print(f"Processed DICOMs: {progress['number_of_dicoms_scanned']}")
        
        # Calculate progress percentage
        if progress['number_of_available_dicoms'] > 0:
            percent = (progress['number_of_dicoms_scanned'] / 
                      progress['number_of_available_dicoms']) * 100
            print(f"Progress: {percent:.1f}%")
        
        if progress.get('total_inference_time'):
            print(f"Processing time: {progress['total_inference_time']}")
    """
    return get_scan(scan_uuid)