# Encephalon API Examples

The Encephalon API through hands-on examples.

## Quick Start

1. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API credentials
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Run an example:**
   ```bash
   # Polling-based workflow
   uv run python flows/create_scan_and_retrieve_inference_results.py
   
   # Webhook-based workflow (setup + simulation)
   uv run python flows/create_scan_and_retrieve_inference_results_with_webhooks.py
   ```

## Two Integration Approaches

Encephalon API offers two distinct integration patterns, each suited for different use cases. Understanding when and
how to use each approach is key to building effective integrations:

### 🔄 Flow 1: Frontend + API (Polling)

**Best for:** Interactive applications, real-time UI updates, direct user control

**Process:**

1. Create patient study
2. Upload DICOM files
3. Trigger scan/analysis
4. **Poll** scan status until complete
5. Retrieve and display results

**Example:** [
`flows/create_scan_and_retrieve_inference_results.py`](flows/create_scan_and_retrieve_inference_results.py)

```python
# Key pattern: Active polling
completed_scan = wait_for_scan_completion(
    scan_uuid,
    timeout=600,  # 10 minutes
    poll_interval=10  # Check every 10 seconds
)
```

**Advantages:**

- Direct control over status checking
- Real-time progress updates for users
- Simple error handling and retry logic
- Works well with interactive UIs

**Considerations:**

- Requires multiple API calls
- Constant polling uses bandwidth
- Need to handle timeouts appropriately

---

### 🔔 Flow 2: API Only with Webhook (No Polling)

**Best for:** Server-to-server integration, high-volume processing, asynchronous systems

**Process:**

1. **One-time:** Configure webhook endpoint
2. Create patient study
3. Upload DICOM files
4. Trigger scan/analysis
5. **System processes asynchronously**
6. **Receive webhook notification** when complete
7. Retrieve and process results

**Example:** [
`flows/create_scan_and_retrieve_inference_results_with_webhooks.py`](flows/create_scan_and_retrieve_inference_results_with_webhooks.py)

```python
# Key pattern: Webhook notification
def handle_webhook_notification(payload):
    # Process completion notification
    scan_data = json.loads(payload)
    if scan_data['status'] == 'COMPLETED':
        report = get_report(scan_data['report']['uuid'])
        # Process results immediately
```

**Advantages:**

- No polling overhead - saves API calls
- Real-time notifications when processing completes
- Scales better for high-volume processing
- Lower server load and faster response times

**Considerations:**

- Requires webhook endpoint setup
- Need to handle webhook signature verification
- Requires reliable webhook delivery handling

---

## 📚 API Reference Examples

### Core Resources

| Resource    | File                                   | Description                                |
|-------------|----------------------------------------|--------------------------------------------|
| **Studies** | [`basic/study.py`](basic/study.py)     | Patient study CRUD operations              |
| **DICOMs**  | [`basic/dicom.py`](basic/dicom.py)     | DICOM file upload, download, management    |
| **Scans**   | [`basic/scan.py`](basic/scan.py)       | Scan creation, monitoring, status tracking |
| **Reports** | [`basic/reports.py`](basic/reports.py) | Analysis results and measurements          |

### Advanced Features

| Feature              | File                                           | Description                           |
|----------------------|------------------------------------------------|---------------------------------------|
| **Advanced Studies** | [`basic/all_studies.py`](basic/all_studies.py) | Filtering, metrics, analytics         |
| **Webhooks**         | [`basic/webhooks.py`](basic/webhooks.py)       | Webhook management and configuration  |
| **EchoGPT**          | [`basic/echogpt.py`](basic/echogpt.py)         | AI-powered natural language responses |

### Complete Workflows

| Workflow             | File                                                                                                                                     | Type             | Description                         |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------|------------------|-------------------------------------|
| **Polling Workflow** | [`flows/create_scan_and_retrieve_inference_results.py`](flows/create_scan_and_retrieve_inference_results.py)                             | Frontend + API   | Complete end-to-end with polling    |
| **Webhook Workflow** | [`flows/create_scan_and_retrieve_inference_results_with_webhooks.py`](flows/create_scan_and_retrieve_inference_results_with_webhooks.py) | Server-to-Server | Async processing with notifications |

---

## 🔧 Step-by-Step API Usage Guide

Learn how to use each Encephalon API operation with practical examples. Each section shows you the essential patterns
you'll need in your applications:

### Study Management

Learn how to manage patient studies - the foundation of all Encephalon workflows:

```python
from basic.study import create_study, get_study, update_study

# Step 1: Create a new patient study
study = create_study(
    name="John Doe",
    age=45,
    height=72,  # inches  
    weight=180,  # pounds
    sex="MALE"
)
study_uuid = study['uuid']  # Save this - you'll need it for all other operations

# Step 2: Retrieve study details anytime
study_details = get_study(study_uuid)

# Step 3: Update patient information as needed
updated = update_study(study_uuid, weight=175)
```

### DICOM Operations

Learn how to upload and manage DICOM files for analysis:

```python
from basic.dicom import upload_dicom, get_dicoms, download_dicom_file

# Step 1: Upload DICOM files to your study
dicom = upload_dicom(study_uuid, "plax_example.dcm")  # Uses the study_uuid from above
dicom_uuid = dicom['uuid']

# Step 2: List all DICOMs in a study
dicoms = get_dicoms(study_uuid=study_uuid)
print(f"Study has {dicoms['count']} DICOM files")

# Step 3: Download DICOM files when needed
file_path = download_dicom_file(dicom_uuid, "image.dcm", "/output/path")
```

### Scan Processing

Learn how to trigger AI analysis and monitor progress:

```python
from basic.scan import create_scan, wait_for_scan_completion, get_scan

# Step 1: Trigger AI analysis on your study
# Default product is ECHOMEASURE
scan = create_scan(study_uuid)  # Uses the study_uuid from above
scan_uuid = scan['uuid']

# Or specify a different product:
# Available products: ECHOMEASURE, CARDIOVISION, ECHOGPT, MITRALVISION
scan = create_scan(study_uuid, product="CARDIOVISION")

# Step 2: Option 1 - Wait for completion (polling approach)
completed_scan = wait_for_scan_completion(scan_uuid, timeout=600)

# Step 2: Option 2 - Check status manually (for custom polling)
current_scan = get_scan(scan_uuid)
print(f"Status: {current_scan['status']}")  # PENDING, STARTED, COMPLETED, FAILED
```

### Report Analysis

Learn how to retrieve and interpret AI analysis results:

```python
from basic.reports import get_report

# Step 1: Get detailed analysis results (from completed scan)
report_uuid = completed_scan['report']  # From the scan above
report = get_report(report_uuid)

# Step 2: Access diameter measurements
for measurement in report['diameter_measurements']:
    metric = measurement['measurement']
    value = measurement.get('value')
    print(f"{metric['acronym']}: {value} {metric['units']}")

# Step 3: Access pathology findings
for pathology in report['pathology_conclusions']:
    feature = pathology['pathology']['feature']['value']
    output = pathology.get('pathology_output')
    print(f"{feature}: {output}")
```

#### How the Report System Works

Understanding how Encephalon generates and manages reports is crucial for building effective integrations. Here's a comprehensive overview of the automated report generation process:

##### 1. Report Generation Flow

The report system follows an automated pipeline that transforms raw DICOM data into professional medical reports:

```
Scan Created → AI Processing → Generate Conclusions → Create PDF → Store Report
```

**Detailed Process:**
1. **Scan Creation**: When you create a scan, a Report is automatically generated and linked to it (one-to-one relationship)
2. **AI Processing**: DICOM files are analyzed by specialized AI pipelines for each product
3. **Post-processing**: AI results are aggregated into structured medical conclusions
4. **PDF Generation**: Professional medical reports are created using HTML templates and converted to PDF
5. **Completion**: Scan is marked complete and webhooks are triggered with report details

##### 2. Report Types by Product

Different Encephalon products generate specialized reports tailored to specific cardiac conditions:

```python
from basic.scan import create_scan

# ECHOMEASURE: Comprehensive cardiac assessment
scan = create_scan(study_uuid, product="ECHOMEASURE")
# → Full cardiac function analysis with EF, volumes, chamber dimensions

# CARDIOVISION: Aortic stenosis focused analysis  
scan = create_scan(study_uuid, product="CARDIOVISION")
# → Detailed aortic valve assessment and stenosis classification

# ECHOGPT: AI-generated narrative reports
scan = create_scan(study_uuid, product="ECHOGPT") 
# → Natural language descriptions and clinical insights

# MITRALVISION: Mitral valve specialized analysis
scan = create_scan(study_uuid, product="MITRALVISION")
# → Mitral valve regurgitation and pathology assessment
```

##### 3. Report Contents

Reports contain comprehensive cardiac analysis data structured for clinical use:

```python
from basic.reports import get_report

report = get_report(report_uuid)

# Measurements: Quantitative cardiac metrics
measurements = report['diameter_measurements']
for measurement in measurements:
    metric = measurement['measurement']
    value = measurement.get('value')
    confidence = measurement.get('confidence_score')
    print(f"{metric['acronym']}: {value} {metric['units']} (confidence: {confidence})")

# Pathology Findings: Clinical classifications
pathologies = report['pathology_conclusions'] 
for pathology in pathologies:
    feature = pathology['pathology']['feature']['value']
    classification = pathology.get('pathology_output')
    severity = pathology.get('severity')
    print(f"{feature}: {classification} - {severity}")

# Quality Metrics: DICOM and analysis quality scores
quality_scores = report.get('quality_metrics', {})
dicom_quality = quality_scores.get('dicom_quality_score')
viewport_confidence = quality_scores.get('viewport_confidence')

# Visual Elements: Best frames for each cardiac view
best_frames = report.get('best_frames', [])
for frame in best_frames:
    view = frame['cardiac_view']
    dicom_uuid = frame['dicom_uuid']
    frame_number = frame['frame_number']
    print(f"Best {view} view: DICOM {dicom_uuid}, frame {frame_number}")
```

##### 4. PDF Report Access

Reports are automatically converted to professional PDF format for clinical use:

```python
from basic.reports import get_report
import requests

# Get report with PDF URL
report = get_report(report_uuid)
pdf_url = report.get('pdf_url')

if pdf_url:
    # Download PDF report
    response = requests.get(pdf_url)
    with open(f"report_{report_uuid}.pdf", "wb") as f:
        f.write(response.content)
    print("PDF report downloaded successfully")

# PDF reports include:
# - Patient demographics and study information
# - Quantitative measurements with reference ranges
# - Pathology findings with clinical classifications  
# - Visual cardiac views with annotations
# - Quality assessment metrics
# - Professional medical formatting
```

##### 5. Report Storage and Security

Reports are securely stored and accessed through the API:

- **Storage Location**: `media/Reports/{report_uuid}/{scan_uuid}.pdf`
- **Cloud Integration**: Automatic backup to cloud storage (GCP)
- **Signed URLs**: Time-limited secure access to PDF files
- **Access Control**: Report access tied to user permissions and study ownership

##### 6. Integration Patterns

**Polling Pattern** (Frontend + API):
```python
# Wait for scan completion, then get report
completed_scan = wait_for_scan_completion(scan_uuid)
report_uuid = completed_scan['report']
report = get_report(report_uuid)
# Process report data immediately
```

**Webhook Pattern** (Server-to-Server):
```python
def handle_webhook_notification(payload):
    scan_data = json.loads(payload)
    if scan_data['status'] == 'COMPLETED':
        report_uuid = scan_data['report']['uuid']
        report = get_report(report_uuid)
        # Process report asynchronously
```

The report system is fully automated - once you create a scan, the entire pipeline runs asynchronously, processing DICOMs, running AI inference, generating conclusions, and producing professional medical PDF reports ready for clinical use.

### Webhook Configuration

Learn how to set up webhooks for real-time notifications:

```python
from basic.webhooks import create_webhook, get_webhooks

# Step 1: Set up webhook endpoint (one-time setup)
webhook = create_webhook("https://your-server.com/webhook")
print(f"Webhook token: {webhook['token']}")  # Store securely for signature verification!

# Step 2: List existing webhooks
webhooks = get_webhooks()
for webhook in webhooks['results']:
    print(f"Webhook: {webhook['url']}")
```

---

## 🧪 Learning Through Testing

The test suite demonstrates how to test API integrations and serves as additional learning material:

```bash
# Run all tests to see mocking patterns
uv run pytest tests/ -v

# Study individual test modules to learn testing approaches
uv run pytest tests/test_study.py -v    # Learn study operation testing
uv run pytest tests/test_dicom.py -v    # Learn DICOM operation testing  
uv run pytest tests/test_scan.py -v     # Learn scan operation testing
```

The tests use mocking to avoid actual API calls during development, showing you how to build reliable tests for your own
applications.

---

## 🏗️ Understanding the Project Structure

This repository is organized to help you learn progressively - from basic operations to complete workflows:

```
encephalon-examples/
├── basic/                  # 📖 Start here: Individual API operations
│   ├── study.py           # Learn patient study management
│   ├── dicom.py           # Learn DICOM file handling
│   ├── scan.py            # Learn scan creation & monitoring
│   ├── reports.py         # Learn result analysis
│   ├── all_studies.py     # Learn advanced filtering & metrics
│   ├── webhooks.py        # Learn webhook configuration
│   └── echogpt.py         # Learn AI response handling
├── flows/                  # 🚀 Then try these: Complete workflows
│   ├── create_scan_and_retrieve_inference_results.py               # Polling workflow
│   └── create_scan_and_retrieve_inference_results_with_webhooks.py # Webhook workflow
├── tests/                  # 🧪 Study these: Testing patterns
│   ├── test_study.py      # See how to test study operations
│   ├── test_dicom.py      # See how to test DICOM operations
│   └── test_scan.py       # See how to test scan operations
├── plax_example.dcm       # 📄 Sample DICOM file for learning
├── env.example            # ⚙️ Environment template
└── README.md              # 📚 This documentation
```

---

## 🔐 Setting Up Authentication

All examples use bearer token authentication. Here's how to configure it:

```bash
# Required environment variables - add these to your .env file
API=https://api-mock.icardio.ai           # Encephalon API base URL
API_TOKEN=your-api-token-here             # Your API authentication token
```

**Important:** Replace `your-api-token-here` with your actual API token from the Encephalon dashboard. The examples will
automatically use these environment variables for authentication.

---

## 📖 Additional Resources

- **OpenAPI Specification**: Complete API documentation with all endpoints, parameters, and response schemas
- **Test Suite**: Comprehensive examples of mocking and testing API integrations

---

## 🤝 Contributing

This repository demonstrates best practices for Encephalon API integration:

- **TDD Approach**: All functionality is test-driven
- **Clean Code**: Linted with Ruff, well-documented
- **Real Examples**: Uses actual DICOM files and realistic workflows
- **Production Ready**: Includes error handling, authentication, and security best practices

For questions or issues, please refer to the Encephalon API documentation or contact support.