import os
import httpx
from typing import Optional, Dict, Any, List


def get_reports(
    study_uuid: Optional[str] = None,
    scan_uuid: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve a list of AI analysis reports with optional filtering.
    
    Use this function to explore analysis results across multiple studies or scans.
    Reports contain the detailed findings from Encephalon's AI analysis.
    
    Args:
        study_uuid: Filter to only show reports from this study (optional)
        scan_uuid: Filter to only show reports from this scan (optional)
        page: Page number for pagination (optional)
        page_size: Number of reports per page (optional)
    
    Returns:
        Dict with 'results' containing report data and pagination info
    
    Example:
        # Get all reports for a specific study
        reports = get_reports(study_uuid="123e4567-e89b-12d3-a456-426614174000")
        print(f"Found {reports['count']} reports for this study")
        
        for report in reports['results']:
            print(f"Report {report['uuid']}: {report['state']}")
            print(f"  Study: {report['study']['name']}")
            print(f"  Version: {report['version']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    params = {}
    if study_uuid:
        params["study"] = study_uuid
    if scan_uuid:
        params["scan"] = scan_uuid
    if page:
        params["page"] = page
    if page_size:
        params["page_size"] = page_size
    
    response = httpx.get(
        f"{api_url}/api/v2/reports/",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()


def get_report(uuid: str) -> Dict[str, Any]:
    """
    Retrieve complete AI analysis results with measurements and clinical findings.
    
    This is the primary function for accessing Encephalon's AI analysis results.
    The report contains clinical conclusions, quantitative measurements, pathology
    findings, and quality assessments.
    
    Args:
        uuid: The unique identifier of the analysis report
    
    Returns:
        Dict containing comprehensive analysis results and clinical data
    
    Example:
        # Get complete analysis results
        report = get_report("789e0123-e89b-12d3-a456-426614174000")
        print(f"Analysis state: {report['state']}")
        print(f"Patient: {report['study']['name']}")
        print(f"Clinical conclusions: {report['conclusions']}")
        
        # Access diameter measurements (heart chamber sizes)
        for measurement in report['diameter_measurements']:
            metric = measurement['measurement']
            value = measurement.get('value')
            if value:
                print(f"{metric['acronym']}: {value} {metric['units']}")
        
        # Access volume measurements (ejection fraction, etc.)
        for measurement in report['segmentation_measurements']:
            metric = measurement['measurement']
            value = measurement.get('value')
            if value:
                print(f"{metric['acronym']}: {value} {metric['units']}")
        
        # Access pathology findings
        for pathology in report.get('pathology_conclusions', []):
            feature = pathology['pathology']['feature']['value']
            output = pathology.get('pathology_output')
            print(f"Pathology: {feature} - {output}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/reports/{uuid}/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def get_report_html(report_uuid: str) -> List[Dict[str, Any]]:
    """
    Retrieve formatted HTML representation of an analysis report.
    
    This function provides a web-ready HTML version of the analysis report,
    suitable for embedding in web applications or generating PDF documents.
    
    Args:
        report_uuid: The unique identifier of the analysis report
    
    Returns:
        List containing HTML elements and formatting data
    
    Example:
        # Get HTML-formatted report for web display
        html_data = get_report_html("789e0123-e89b-12d3-a456-426614174000")
        print(f"HTML sections available: {len(html_data)}")
        
        # Process HTML elements for web display
        for section in html_data:
            if 'html' in section:
                print(f"HTML content: {section['html'][:100]}...")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/reports/{report_uuid}/html/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def get_echogpt_responses() -> List[Dict[str, Any]]:
    """
    Get EchoGPT AI responses.
    
    Example:
        responses = get_echogpt_responses()
        for response in responses:
            print(f"EchoGPT response for scan {response['scan']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/echogpt/report/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def get_echogpt_response(uuid: str) -> Dict[str, Any]:
    """
    Get a specific EchoGPT response.
    
    Example:
        response = get_echogpt_response("abc123-def456-789")
        print(f"AI Response: {response['response']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/echogpt/report/{uuid}/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def create_user_measurement(
    dicom_uuid: str,
    measurement_key: str,
    measurement_type: str,
    keyframe_type: str,
    measurement_metadata: List[Dict[str, Any]],
    frame_index: Optional[int] = None,
    value: Optional[float] = None,
    unit: Optional[str] = None,
    extra_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Record manual measurements made by clinical users on DICOM images.
    
    This function allows you to store user-defined measurements that can supplement
    or validate AI-generated measurements. It's useful for clinical workflow
    integration where manual review is required.
    
    Args:
        dicom_uuid: The DICOM image where the measurement was made
        measurement_key: Standardized key for the measurement type (e.g., "lvsv")
        measurement_type: Category of measurement ("DIAMETER", "VOLUME", etc.)
        keyframe_type: Cardiac phase ("SYSTOLIC", "DIASTOLIC", etc.)
        measurement_metadata: Coordinates and measurement details
        frame_index: Specific frame number in the DICOM (optional)
        value: Calculated measurement value (optional)
        unit: Measurement units ("mm", "ml", "%", etc.) (optional)
        extra_metadata: Additional measurement context (optional)
    
    Returns:
        Dict containing the recorded measurement with UUID and validation info
    
    Example:
        # Record a manual left ventricular measurement
        measurement = create_user_measurement(
            dicom_uuid="456e7890-e89b-12d3-a456-426614174000",
            measurement_key="lvsv",  # Left ventricular stroke volume
            measurement_type="VOLUME",
            keyframe_type="SYSTOLIC",
            measurement_metadata=[
                {
                    "type": "DIAMETER",
                    "point_1_coordinate_x": 100.0,
                    "point_1_coordinate_y": 150.0,
                    "point_2_coordinate_x": 200.0,
                    "point_2_coordinate_y": 150.0
                }
            ],
            value=65.5,
            unit="ml",
            frame_index=15
        )
        print(f"Recorded manual measurement: {measurement['uuid']}")
        print(f"Value: {measurement['value']} {measurement['unit']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    data = {
        "dicom_uuid": dicom_uuid,
        "measurement_key": measurement_key,
        "measurement_type": measurement_type,
        "keyframe_type": keyframe_type,
        "measurement_metadata": measurement_metadata
    }
    
    if frame_index is not None:
        data["frame_index"] = frame_index
    if value is not None:
        data["value"] = value
    if unit is not None:
        data["unit"] = unit
    if extra_metadata is not None:
        data["extra_metadata"] = extra_metadata
    
    response = httpx.post(
        f"{api_url}/api/v2/measurements/",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    return response.json()


def get_api_version() -> Dict[str, str]:
    """
    Retrieve current Encephalon API version and compatibility information.
    
    Use this function to verify API compatibility and track which version
    of the analysis algorithms your application is using.
    
    Returns:
        Dict containing version string and API metadata
    
    Example:
        # Check API version for compatibility
        version_info = get_api_version()
        print(f"Encephalon API Version: {version_info['version']}")
        
        # Log version for debugging and support
        print(f"Using API version: {version_info['version']}")
        
        # You can store this for troubleshooting
        api_version = version_info['version']
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/version",
        headers=headers
    )
    response.raise_for_status()
    return response.json()