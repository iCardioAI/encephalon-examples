import os
import httpx
from typing import Optional, Dict, Any


def get_all_studies_with_measurements(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    q: Optional[str] = None,
    name: Optional[str] = None,
    uuid: Optional[str] = None,
    created_at__gte: Optional[str] = None,
    created_at__lte: Optional[str] = None,
    scan_product: Optional[str] = None,
    scan_status: Optional[str] = None,
    user_email: Optional[str] = None,
    view_types: Optional[str] = None,
    diseases: Optional[str] = None,
    measurements: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search and filter studies with embedded measurement data for analytics.
    
    **IMPORTANT: This endpoint requires staff or superadmin permissions.**
    
    This advanced function combines study information with measurement results,
    enabling powerful filtering and analysis across your entire dataset.
    Perfect for research, quality assurance, and clinical analytics.
    
    Args:
        page: Page number for pagination (optional)
        page_size: Number of studies per page (optional)
        q: General search query across study fields (optional)
        name: Filter by patient name (optional)
        uuid: Filter by specific study UUID (optional)
        created_at__gte: Studies created after this date (YYYY-MM-DD) (optional)
        created_at__lte: Studies created before this date (YYYY-MM-DD) (optional)
        scan_product: Filter by analysis product ("ECHOMEASURE", etc.) (optional)
        scan_status: Filter by scan status ("COMPLETED", "FAILED", etc.) (optional)
        user_email: Filter by user who created the study (optional)
        view_types: Filter by DICOM view types (optional)
        diseases: Filter by detected pathologies (optional)
        measurements: Filter by specific measurement types (optional)
    
    Returns:
        Dict with filtered study results including embedded measurements
    
    Example:
        # Find all completed cardiac analyses from 2024
        studies = get_all_studies_with_measurements(
            scan_product="ECHOMEASURE",
            scan_status="COMPLETED", 
            created_at__gte="2024-01-01",
            page_size=50
        )
        
        print(f"Found {studies['count']} completed studies")
        
        for study in studies['results']:
            print(f"\nPatient: {study['name']}")
            print(f"Age: {study['age']} years")
            print(f"Analysis date: {study['created_at']}")
            
            # Access embedded measurements directly
            for measurement in study.get('measurements', []):
                metric = measurement['measurement']
                value = measurement.get('value')
                if value:
                    print(f"  {metric['acronym']}: {value} {metric['units']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    params = {}
    if page:
        params["page"] = page
    if page_size:
        params["page_size"] = page_size
    if q:
        params["q"] = q
    if name:
        params["name"] = name
    if uuid:
        params["uuid"] = uuid
    if created_at__gte:
        params["created_at__gte"] = created_at__gte
    if created_at__lte:
        params["created_at__lte"] = created_at__lte
    if scan_product:
        params["scan_product"] = scan_product
    if scan_status:
        params["scan_status"] = scan_status
    if user_email:
        params["user_email"] = user_email
    if view_types:
        params["view_types"] = view_types
    if diseases:
        params["diseases"] = diseases
    if measurements:
        params["measurements"] = measurements
    
    response = httpx.get(
        f"{api_url}/api/v2/all_studies/",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()


def get_study_with_measurements(uuid: str) -> Dict[str, Any]:
    """
    Retrieve comprehensive study data with embedded measurement results.
    
    **IMPORTANT: This endpoint requires staff or superadmin permissions.**
    
    This function provides a complete view of a study including patient demographics,
    analysis results, and all measurements in a single response - ideal for
    detailed analysis or comprehensive reporting.
    
    Args:
        uuid: The unique identifier of the study
    
    Returns:
        Dict containing complete study information with embedded measurements
    
    Example:
        # Get comprehensive study data with all measurements
        study = get_study_with_measurements("123e4567-e89b-12d3-a456-426614174000")
        print(f"Patient: {study['name']}, Age: {study['age']}")
        print(f"Study created: {study['created_at']}")
        
        # Access all measurements directly
        measurements = study.get('measurements', [])
        print(f"\nFound {len(measurements)} measurements:")
        
        for measurement in measurements:
            metric = measurement['measurement']
            value = measurement.get('value')
            flag = measurement.get('flag')
            
            if value is not None:
                status = "⚠️ Abnormal" if flag else "✓ Normal"
                print(f"  {metric['acronym']}: {value} {metric['units']} ({status})")
                print(f"    {metric['key']} - Range: {metric['low_range']}-{metric['high_range']}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/all_studies/{uuid}/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def get_study_metrics() -> Dict[str, Any]:
    """
    Retrieve analytics and usage statistics across your entire study database.
    
    **IMPORTANT: This endpoint requires staff or superadmin permissions.**
    
    This function provides valuable insights for administrators, researchers,
    and quality assurance teams by aggregating data across all studies and analyses.
    
    Returns:
        Dict containing comprehensive usage metrics and statistics
    
    Example:
        # Get system-wide analytics
        metrics = get_study_metrics()
        print(f"Database Statistics:")
        print(f"  Total studies: {metrics['total_studies']:,}")
        print(f"  Unique users: {metrics['unique_users']:,}")
        print(f"  Last activity: {metrics['last_upload']}")
        
        # Analyze product usage
        print(f"\nAnalysis Product Distribution:")
        for product, count in metrics['product_distribution'].items():
            percentage = (count / metrics['total_studies']) * 100
            print(f"  {product}: {count:,} ({percentage:.1f}%)")
        
        # Use metrics for capacity planning and reporting
        total_analyses = sum(metrics['product_distribution'].values())
        print(f"\nTotal AI analyses performed: {total_analyses:,}")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/all_studies/metrics/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


def get_filter_metadata() -> Dict[str, Any]:
    """
    Discover available filtering options for building dynamic search interfaces.
    
    **IMPORTANT: This endpoint requires staff or superadmin permissions.**
    
    This function helps you understand what filter values are available in your
    dataset, perfect for building search UIs, analytics dashboards, or
    understanding your data structure.
    
    Returns:
        Dict containing all available filter options and their metadata
    
    Example:
        # Discover available filters for building search UI
        metadata = get_filter_metadata()
        print("Available Search Filters:")
        
        for filter_name, options in metadata['filters'].items():
            print(f"\n{filter_name.title()}:")
            for option in options:
                print(f"  • {option['label']} (value: '{option['value']}')")
                if 'description' in option:
                    print(f"    {option['description']}")
        
        # Use metadata to build dynamic search forms
        product_options = metadata['filters'].get('scan_product', [])
        status_options = metadata['filters'].get('scan_status', [])
        
        print(f"\nFound {len(product_options)} analysis products")
        print(f"Found {len(status_options)} status options")
    """
    api_url = os.getenv("API")
    token = os.getenv("API_TOKEN")
    
    headers = {
        "Authorization": f"Token {token}",  # Use 'Token' format for API_TOKEN authentication
        "Content-Type": "application/json"
    }
    
    response = httpx.get(
        f"{api_url}/api/v2/all_studies/filters/metadata/",
        headers=headers
    )
    response.raise_for_status()
    return response.json()