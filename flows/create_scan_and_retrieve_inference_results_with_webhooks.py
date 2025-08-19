"""
Learn Flow 2: Webhook-based workflow for scalable cardiac AI integration.

This example teaches you the webhook approach (API Only) for building high-performance,
server-to-server integrations with Encephalon. You'll learn how to eliminate polling
overhead and build systems that scale efficiently.

What you'll learn:
1. How to configure webhook endpoints for real-time notifications
2. How to handle asynchronous AI analysis completion events
3. How to build efficient server-to-server integrations
4. How to process webhook payloads and retrieve full analysis results

This approach is ideal for high-volume processing, server applications, batch systems,
or any integration where you want to minimize API calls and maximize efficiency.

Key advantages: No polling overhead, real-time notifications, better scalability,
reduced server load, and immediate response to analysis completion.
"""

import json
from basic.study import create_study
from basic.dicom import upload_dicom, get_dicoms
from basic.scan import create_scan, get_scan
from basic.reports import get_report
from basic.webhooks import create_webhook, get_webhooks



def setup_webhook(webhook_url):
    """
    Set up webhook endpoint for receiving scan completion notifications.
    
    Args:
        webhook_url: Your server endpoint that will receive webhook POSTs
        
    Returns:
        dict: Webhook configuration including token for signature verification
    """
    print("Setting up webhook...")
    
    # Check if webhook already exists
    existing_webhooks = get_webhooks()
    for webhook in existing_webhooks.get('results', []):
        if webhook['url'] == webhook_url:
            print(f"Webhook already exists: {webhook['uuid']}")
            return webhook
    
    # Create new webhook
    webhook = create_webhook(webhook_url)
    print(f"Created webhook: {webhook['uuid']}")
    print(f"   URL: {webhook['url']}")
    print(f"   Token: {webhook['token']}")
    print("   Store this token securely - you'll need it to verify webhook signatures!")
    
    return webhook


def webhook_workflow_setup(webhook_url="https://your-server.com/webhook-endpoint"):
    """
    Demonstrate the setup phase of webhook workflow.
    """
    print("Webhook-based Encephalon API Workflow")
    print("=" * 50)
    
    try:
        # Step 0: Configure webhook (one-time setup)
        print("\\n0. Configuring webhook endpoint...")
        webhook = setup_webhook(webhook_url)
        
        # Step 1: Create a study
        print("\\n1. Creating study...")
        study = create_study(
            name="Jane Smith",
            age=52,
            height=65,  # inches
            weight=140,  # pounds
            sex="FEMALE"
        )
        study_uuid = study['uuid']
        print(f"Created study: {study_uuid}")
        print(f"   Patient: {study['name']}, Age: {study['age']}")
        
        # Step 2: Upload DICOM file
        print("\\n2. Uploading DICOM file...")
        dicom = upload_dicom(study_uuid, "plax_example.dcm")
        dicom_uuid = dicom['uuid']
        print(f"Uploaded DICOM: {dicom_uuid}")
        print(f"   File: {dicom['name']}")
        
        # Verify DICOM upload
        dicoms = get_dicoms(study_uuid=study_uuid)
        print(f"   Total DICOMs in study: {dicoms['count']}")
        
        # Step 3: Create scan to trigger analysis (no polling!)
        print("\\n3. Creating scan for AI analysis...")
        scan = create_scan(study_uuid)
        scan_uuid = scan['uuid']
        print(f"Created scan: {scan_uuid}")
        print(f"   Product: {scan['product']}")
        print(f"   Status: {scan['status']}")
        
        print("\\n4. Scan submitted successfully!")
        print("   The system will now process the scan asynchronously...")
        print("   When complete, your webhook will receive a notification.")
        print("   No polling required!")
        
        print("\\nWebhook workflow setup completed!")
        print(f"   Study UUID: {study_uuid}")
        print(f"   Scan UUID: {scan_uuid}")
        print(f"   Webhook UUID: {webhook['uuid']}")
        print(f"   Webhook Token: {webhook['token']}")
        
        # Return information for webhook handler
        return {
            'study_uuid': study_uuid,
            'scan_uuid': scan_uuid,
            'webhook_uuid': webhook['uuid'],
            'webhook_token': webhook['token']
        }
        
    except Exception as e:
        print(f"\\nError during workflow setup: {str(e)}")
        raise


def handle_webhook_notification(webhook_payload):
    """
    Handle incoming webhook notification when scan is completed.
    
    This function would typically be called by your web server when it receives
    a POST request to your webhook endpoint.
    
    Args:
        webhook_payload: Raw JSON payload from webhook (as bytes)
        
    Example webhook payload:
    {
        "scan_id": "scan-uuid-here",
        "status": "COMPLETED",
        "report": {
            "uuid": "report-uuid-here",
            "measurements": [...],
            "pathologies": [...],
            "conclusions": [...],
            "quality_scores": [...],
            "best_dicoms": [...]
        }
    }
    """
    print("\\nReceived webhook notification!")
    print("=" * 40)
    
    # Step 1: Parse webhook payload
    print("\\n1. Parsing webhook payload...")
    try:
        payload = json.loads(webhook_payload.decode('utf-8'))
        scan_uuid = payload['scan_id']
        status = payload['status']
        
        print(f"   Scan UUID: {scan_uuid}")
        print(f"   Status: {status}")
        
        if status == 'COMPLETED':
            report_info = payload.get('report', {})
            report_uuid = report_info.get('uuid')
            print(f"   Report UUID: {report_uuid}")
            
            # Step 2: Retrieve full report details
            if report_uuid:
                print("\\n2. Retrieving full report...")
                report = get_report(report_uuid)
                
                print(f"✅ Retrieved complete report: {report['uuid']}")
                print(f"   Report version: {report['version']}")
                print(f"   Study: {report['study']['name']}")
                
                # Display key findings from webhook payload
                if report_info.get('measurements'):
                    print(f"\\n📏 Measurements found: {len(report_info['measurements'])} items")
                
                if report_info.get('pathologies'):
                    print(f"🔬 Pathologies found: {len(report_info['pathologies'])} items")
                
                if report_info.get('conclusions'):
                    print(f"📋 Conclusions found: {len(report_info['conclusions'])} items")
                
                # Display full report details (same as polling example)
                display_report_details(report)
                
                return {
                    'scan_uuid': scan_uuid,
                    'report_uuid': report_uuid,
                    'status': 'SUCCESS'
                }
            else:
                print("⚠️ No report UUID in webhook payload")
                return {'scan_uuid': scan_uuid, 'status': 'NO_REPORT'}
                
        elif status == 'FAILED':
            print("❌ Scan failed to complete")
            # Get additional error details from scan status
            scan_details = get_scan(scan_uuid)
            if scan_details.get('state'):
                print(f"   Error details: {scan_details['state']}")
            
            return {'scan_uuid': scan_uuid, 'status': 'FAILED'}
        
        else:
            print(f"⏳ Unexpected status: {status}")
            return {'scan_uuid': scan_uuid, 'status': status}
            
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse webhook payload: {e}")
        raise
    except KeyError as e:
        print(f"❌ Missing required field in webhook payload: {e}")
        raise


def display_report_details(report):
    """Display detailed report information (similar to polling example)."""
    
    # Display conclusions
    if report.get('conclusions'):
        print("\\nClinical Conclusions:")
        print(f"   {report['conclusions']}")
    
    # Display enumerated conclusions
    if report.get('enumerated_conclusions'):
        print("\\nDetailed Findings:")
        for conclusion in sorted(report['enumerated_conclusions'], key=lambda x: x['order']):
            print(f"   {conclusion['order']}. {conclusion['text']}")
    
    # Display diameter measurements
    if report.get('diameter_measurements'):
        print("\\nDiameter Measurements:")
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
        print("\\nSegmentation Measurements:")
        for measurement in report['segmentation_measurements']:
            metric = measurement['measurement']
            value = measurement.get('value')
            flag = measurement.get('flag')
            
            if value is not None:
                flag_symbol = "!" if flag else "*"
                print(f"   {flag_symbol} {metric['acronym']}: {value} {metric['units']}")


def simulate_webhook_delivery():
    """
    Simulate receiving a webhook notification.
    This shows what your webhook handler should expect.
    """
    print("\\nSimulating webhook delivery...")
    print("=" * 40)
    
    # Example webhook payload (what your server would receive)
    example_payload = {
        "scan_id": "example-scan-uuid-12345",
        "status": "COMPLETED",
        "report": {
            "uuid": "example-report-uuid-67890",
            "measurements": [
                {"type": "diameter", "name": "LVEF", "value": 55, "units": "%"},
                {"type": "volume", "name": "LVSV", "value": 70, "units": "ml"}
            ],
            "pathologies": [
                {"name": "mitral_regurgitation", "severity": "mild", "confidence": 0.85}
            ],
            "conclusions": [
                "Normal left ventricular function",
                "Mild mitral regurgitation noted"
            ],
            "quality_scores": {"overall": 0.92, "image_quality": 0.88},
            "best_dicoms": ["dicom-uuid-1", "dicom-uuid-2"]
        }
    }
    
    # Convert to bytes (as your server would receive)
    payload_bytes = json.dumps(example_payload).encode('utf-8')
    
    print("Webhook would be received as:")
    print("POST /webhook-endpoint")
    print("Headers:")
    print("  Content-Type: application/json")
    print("Body:")
    print(f"  {json.dumps(example_payload, indent=2)}")
    
    return payload_bytes


if __name__ == "__main__":
    # Demonstrate webhook workflow setup
    print("=== WEBHOOK WORKFLOW DEMO ===\\n")
    
    # Part 1: Setup the workflow
    try:
        workflow_info = webhook_workflow_setup("https://your-server.com/encephalon-webhook")
    except Exception as e:
        print(f"Setup failed: {e}")
        exit(1)
    
    print("\\n" + "="*60)
    
    # Part 2: Simulate webhook notification
    print("\\n=== SIMULATING WEBHOOK NOTIFICATION ===")
    payload_bytes = simulate_webhook_delivery()
    
    print("\\n=== HANDLING WEBHOOK ===")
    try:
        result = handle_webhook_notification(payload_bytes)
        print(f"\\n✅ Webhook handled successfully: {result}")
    except Exception as e:
        print(f"\\n❌ Webhook handling failed: {e}")
    
    print("\\n=== WEBHOOK WORKFLOW COMPLETE ===")
    print("\\nKey advantages of webhook approach:")
    print("• No polling required - saves API calls")
    print("• Real-time notifications when scans complete")
    print("• Reduced server load and faster response times")
    print("• Better user experience with immediate updates")
    print("• Scalable for high-volume processing")