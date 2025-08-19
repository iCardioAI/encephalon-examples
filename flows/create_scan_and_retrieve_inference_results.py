"""
Learn Flow 1: Complete polling-based workflow for cardiac AI analysis.

This example teaches you the polling approach (Frontend + API) for integrating
with Encephalon. You'll learn how to build interactive applications that provide
real-time progress updates to users.

What you'll learn:
1. How to create patient studies with demographic information
2. How to upload DICOM files for AI analysis
3. How to trigger cardiac analysis with scan creation
4. How to monitor analysis progress using polling
5. How to retrieve and interpret comprehensive analysis results

This approach is ideal for web applications, mobile apps, or any system where
users need immediate feedback and progress updates.
"""

from basic.study import create_study
from basic.dicom import upload_dicom, get_dicoms
from basic.scan import create_scan, wait_for_scan_completion
from basic.reports import get_report


def main():
    print("Encephalon API Workflow Example")
    print("=" * 50)

    try:
        # Step 1: Create a study
        print("\n1. Creating study...")
        study = create_study(
            name="John Doe",
            age=45,
            height=72,  # inches
            weight=180,  # pounds
            sex="MALE"
        )
        study_uuid = study['uuid']
        print(f"Created study: {study_uuid}")
        print(f"   Patient: {study['name']}, Age: {study['age']}")
        
        # Step 2: Upload DICOM file
        print("\n2. Uploading DICOM file...")
        dicom = upload_dicom(study_uuid, "plax_example.dcm")
        dicom_uuid = dicom['uuid']
        print(f"Uploaded DICOM: {dicom_uuid}")
        print(f"   File: {dicom['name']}")
        
        # Verify DICOM upload
        dicoms = get_dicoms(study_uuid=study_uuid)
        print(f"   Total DICOMs in study: {dicoms['count']}")
        
        # Step 3: Create scan to trigger analysis
        print("\n3. Creating scan for AI analysis...")
        scan = create_scan(study_uuid)
        scan_uuid = scan['uuid']
        print(f"Created scan: {scan_uuid}")
        print(f"   Product: {scan['product']}")
        print(f"   Status: {scan['status']}")
        
        # Step 4: Monitor scan progress
        print("\n4. Monitoring scan progress...")
        print("   Waiting for analysis to complete...")
        
        # Poll every 10 seconds for up to 10 minutes
        completed_scan = wait_for_scan_completion(
            scan_uuid, 
            timeout=600,  # 10 minutes
            poll_interval=10
        )
        
        print(f"Scan completed with status: {completed_scan['status']}")
        
        if completed_scan['status'] == 'COMPLETED':
            print(f"   Report UUID: {completed_scan['report']}")
            print(f"   Inference time: {completed_scan['total_inference_time']}")
            print(f"   DICOMs processed: {completed_scan['number_of_dicoms_scanned']}")
            
            # Step 5: Retrieve and display results
            print("\n5. Retrieving analysis results...")
            report = get_report(completed_scan['report'])
            
            print(f"Retrieved report: {report['uuid']}")
            print(f"   Report version: {report['version']}")
            print(f"   Study: {report['study']['name']}")
            
            # Display conclusions
            if report.get('conclusions'):
                print("\nClinical Conclusions:")
                print(f"   {report['conclusions']}")
            
            # Display enumerated conclusions
            if report.get('enumerated_conclusions'):
                print("\nDetailed Findings:")
                for conclusion in sorted(report['enumerated_conclusions'], key=lambda x: x['order']):
                    print(f"   {conclusion['order']}. {conclusion['text']}")
            
            # Display diameter measurements
            if report.get('diameter_measurements'):
                print("\nDiameter Measurements:")
                for measurement in report['diameter_measurements']:
                    metric = measurement['measurement']
                    value = measurement.get('value')
                    flag = measurement.get('flag')
                    
                    if value is not None:
                        flag_symbol = "!" if flag else "*"
                        print(f"   {flag_symbol} {metric['acronym']}: {value} {metric['units']}")
                        print(f"      {metric['key']} (Range: {metric['low_range']}-{metric['high_range']} {metric['units']})")
            
            # Display segmentation measurements
            if report.get('segmentation_measurements'):
                print("\nSegmentation Measurements:")
                for measurement in report['segmentation_measurements']:
                    metric = measurement['measurement']
                    value = measurement.get('value')
                    flag = measurement.get('flag')
                    
                    if value is not None:
                        flag_symbol = "!" if flag else "*"
                        print(f"   {flag_symbol} {metric['acronym']}: {value} {metric['units']}")
            
            # Display pathology conclusions
            if report.get('pathology_conclusions'):
                print("\nPathology Analysis:")
                for pathology in report['pathology_conclusions']:
                    feature = pathology['pathology']['feature']['value']
                    output = pathology.get('pathology_output', 'N/A')
                    score = pathology.get('score')
                    
                    if score is not None:
                        print(f"   {feature}: {output} (Score: {score:.2f})")
                    else:
                        print(f"   {feature}: {output}")
            
            # Display warnings if any
            if report.get('warnings'):
                warnings = report['warnings']
                if any([warnings.get('low_quality'), warnings.get('viewport_not_found'), 
                       warnings.get('diameter_outside_range'), warnings.get('other')]):
                    print("\nWarnings:")
                    
                    for low_quality in warnings.get('low_quality', []):
                        print(f"   * Low quality DICOM: {low_quality['message']}")
                    
                    for viewport_error in warnings.get('viewport_not_found', []):
                        print(f"   * Viewport not found: {viewport_error['message']}")
                    
                    for diameter_error in warnings.get('diameter_outside_range', []):
                        print(f"   * Diameter out of range: {diameter_error['message']}")
                    
                    for other_error in warnings.get('other', []):
                        print(f"   * {other_error['message']}")
            
        elif completed_scan['status'] == 'FAILED':
            print("Scan failed to complete")
            if completed_scan.get('state'):
                print(f"   Error details: {completed_scan['state']}")
        
        print("\nWorkflow completed successfully!")
        print(f"   Study UUID: {study_uuid}")
        print(f"   Scan UUID: {scan_uuid}")
        if completed_scan['status'] == 'COMPLETED':
            print(f"   Report UUID: {completed_scan['report']}")
        
    except Exception as e:
        print(f"\nError during workflow: {str(e)}")
        raise


if __name__ == "__main__":
    main()