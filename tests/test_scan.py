import pytest
from unittest.mock import Mock, patch

from basic.scan import (
    create_scan,
    get_scans,
    get_scan,
    delete_scan,
    wait_for_scan_completion,
    get_scan_progress
)


class TestScanFunctions:
    @pytest.fixture
    def mock_env(self):
        with patch.dict('os.environ', {
            'API': 'https://api.example.com',
            'API_TOKEN': 'test-token'
        }):
            yield

    @pytest.fixture
    def sample_scan(self):
        return {
            "uuid": "456e7890-e89b-12d3-a456-426614174000",
            "created_at": "2024-01-01T00:00:00Z",
            "study": "123e4567-e89b-12d3-a456-426614174000",
            "product": "ECHOMEASURE",
            "status": "PENDING",
            "report": None,
            "number_of_available_dicoms": 10,
            "number_of_dicoms_scanned": 0,
            "total_inference_time": None
        }

    @patch('httpx.post')
    def test_create_scan(self, mock_post, mock_env, sample_scan):
        mock_response = Mock()
        mock_response.json.return_value = sample_scan
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = create_scan("123e4567-e89b-12d3-a456-426614174000")
        
        assert result["uuid"] == "456e7890-e89b-12d3-a456-426614174000"
        assert result["status"] == "PENDING"
        
        mock_post.assert_called_once_with(
            "https://api.example.com/api/v2/scans/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            },
            json={"study": "123e4567-e89b-12d3-a456-426614174000"}
        )

    @patch('httpx.post')
    def test_create_scan_with_product(self, mock_post, mock_env, sample_scan):
        mock_response = Mock()
        mock_response.json.return_value = sample_scan
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = create_scan("123e4567-e89b-12d3-a456-426614174000", product="CARDIOVISION")
        
        assert result["uuid"] == "456e7890-e89b-12d3-a456-426614174000"
        assert result["status"] == "PENDING"
        
        mock_post.assert_called_once_with(
            "https://api.example.com/api/v2/scans/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            },
            json={
                "study": "123e4567-e89b-12d3-a456-426614174000",
                "product": "CARDIOVISION"
            }
        )

    @patch('httpx.get')
    def test_get_scans(self, mock_get, mock_env, sample_scan):
        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 1,
            "results": [sample_scan]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_scans(study_uuid="123e4567-e89b-12d3-a456-426614174000")
        
        assert result["count"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["product"] == "ECHOMEASURE"
        
        mock_get.assert_called_once_with(
            "https://api.example.com/api/v2/scans/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            },
            params={"study": "123e4567-e89b-12d3-a456-426614174000"}
        )

    @patch('httpx.get')
    def test_get_scan(self, mock_get, mock_env, sample_scan):
        mock_response = Mock()
        mock_response.json.return_value = sample_scan
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_scan("456e7890-e89b-12d3-a456-426614174000")
        
        assert result["uuid"] == "456e7890-e89b-12d3-a456-426614174000"
        assert result["status"] == "PENDING"
        
        mock_get.assert_called_once_with(
            "https://api.example.com/api/v2/scans/456e7890-e89b-12d3-a456-426614174000/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            }
        )

    @patch('httpx.delete')
    def test_delete_scan(self, mock_delete, mock_env):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        delete_scan("456e7890-e89b-12d3-a456-426614174000")
        
        mock_delete.assert_called_once_with(
            "https://api.example.com/api/v2/scans/456e7890-e89b-12d3-a456-426614174000/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            }
        )

    @patch('basic.scan.get_scan')
    @patch('time.sleep')
    def test_wait_for_scan_completion_success(self, mock_sleep, mock_get_scan, mock_env, sample_scan):
        completed_scan = {**sample_scan, "status": "COMPLETED", "report": "report-uuid"}
        mock_get_scan.side_effect = [
            sample_scan,  # First call: PENDING
            {**sample_scan, "status": "STARTED"},  # Second call: STARTED
            completed_scan  # Third call: COMPLETED
        ]

        result = wait_for_scan_completion("456e7890-e89b-12d3-a456-426614174000")
        
        assert result["status"] == "COMPLETED"
        assert result["report"] == "report-uuid"
        assert mock_get_scan.call_count == 3

    @patch('basic.scan.get_scan')
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_for_scan_completion_timeout(self, mock_time, mock_sleep, mock_get_scan, mock_env, sample_scan):
        mock_time.side_effect = [0, 350]  # Start time, then timeout
        mock_get_scan.return_value = sample_scan  # Always return PENDING

        with pytest.raises(TimeoutError):
            wait_for_scan_completion("456e7890-e89b-12d3-a456-426614174000", timeout=300)

    @patch('basic.scan.get_scan')
    def test_get_scan_progress(self, mock_get_scan, mock_env, sample_scan):
        progress_scan = {
            **sample_scan,
            "status": "STARTED",
            "number_of_dicoms_scanned": 5
        }
        mock_get_scan.return_value = progress_scan

        result = get_scan_progress("456e7890-e89b-12d3-a456-426614174000")
        
        assert result["status"] == "STARTED"
        assert result["number_of_dicoms_scanned"] == 5
        mock_get_scan.assert_called_once_with("456e7890-e89b-12d3-a456-426614174000")