import pytest
from unittest.mock import Mock, patch, mock_open

from basic.dicom import (
    upload_dicom,
    get_dicoms,
    get_dicom,
    download_dicom_file,
    delete_dicom,
    idempotent_dicom_upload
)


class TestDicomFunctions:
    @pytest.fixture
    def mock_env(self):
        with patch.dict('os.environ', {
            'API': 'https://api.example.com',
            'API_TOKEN': 'test-token'
        }):
            yield

    @pytest.fixture
    def sample_dicom(self):
        return {
            "uuid": "456e7890-e89b-12d3-a456-426614174000",
            "created_at": "2024-01-01T00:00:00Z",
            "study": "123e4567-e89b-12d3-a456-426614174000",
            "name": "image.dcm",
            "delta_x": 1.0,
            "delta_y": 1.0,
            "sop_instance_uid": "1.2.3.4.5"
        }

    @patch('httpx.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake dicom data')
    def test_upload_dicom(self, mock_file, mock_post, mock_env, sample_dicom):
        mock_response = Mock()
        mock_response.json.return_value = sample_dicom
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = upload_dicom(
            "123e4567-e89b-12d3-a456-426614174000",
            "/path/to/file.dcm"
        )
        
        assert result["uuid"] == "456e7890-e89b-12d3-a456-426614174000"
        assert result["name"] == "image.dcm"
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args.kwargs["headers"]["Authorization"] == "Bearer test-token"
        assert "https://api.example.com/api/v2/dicoms/" in call_args.args

    @patch('httpx.get')
    def test_get_dicoms(self, mock_get, mock_env, sample_dicom):
        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 1,
            "results": [sample_dicom]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_dicoms(study_uuid="123e4567-e89b-12d3-a456-426614174000")
        
        assert result["count"] == 1
        assert len(result["results"]) == 1
        
        mock_get.assert_called_once_with(
            "https://api.example.com/api/v2/dicoms/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            },
            params={"study": "123e4567-e89b-12d3-a456-426614174000"}
        )

    @patch('httpx.get')
    def test_get_dicom(self, mock_get, mock_env, sample_dicom):
        mock_response = Mock()
        mock_response.json.return_value = sample_dicom
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_dicom("456e7890-e89b-12d3-a456-426614174000")
        
        assert result["uuid"] == "456e7890-e89b-12d3-a456-426614174000"
        assert result["name"] == "image.dcm"
        
        mock_get.assert_called_once_with(
            "https://api.example.com/api/v2/dicoms/456e7890-e89b-12d3-a456-426614174000/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            }
        )

    @patch('httpx.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_download_dicom_file(self, mock_mkdir, mock_file, mock_get, mock_env):
        mock_response = Mock()
        mock_response.content = b'fake dicom content'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = download_dicom_file(
            "456e7890-e89b-12d3-a456-426614174000",
            "image.dcm",
            "/output/path"
        )
        
        assert result == "/output/path/image.dcm"
        
        mock_get.assert_called_once_with(
            "https://api.example.com/api/v2/dicoms/file/456e7890-e89b-12d3-a456-426614174000/image.dcm/",
            headers={"Authorization": "Bearer test-token"},
            follow_redirects=True
        )
        
        mock_file().write.assert_called_once_with(b'fake dicom content')

    @patch('httpx.delete')
    def test_delete_dicom(self, mock_delete, mock_env):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        delete_dicom("456e7890-e89b-12d3-a456-426614174000")
        
        mock_delete.assert_called_once_with(
            "https://api.example.com/api/v2/dicoms/456e7890-e89b-12d3-a456-426614174000/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            }
        )

    @patch('httpx.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake dicom data')
    def test_idempotent_dicom_upload(self, mock_file, mock_post, mock_env):
        mock_response = Mock()
        mock_response.json.return_value = {
            "study": "123e4567-e89b-12d3-a456-426614174000",
            "uuid": "456e7890-e89b-12d3-a456-426614174000"
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = idempotent_dicom_upload("/path/to/file.dcm")
        
        assert result["study"] == "123e4567-e89b-12d3-a456-426614174000"
        assert result["uuid"] == "456e7890-e89b-12d3-a456-426614174000"
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args.kwargs["headers"]["Authorization"] == "Bearer test-token"
        assert "https://api.example.com/api/v2/idempotent_dicom/" in call_args.args