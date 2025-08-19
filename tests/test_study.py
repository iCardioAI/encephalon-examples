import pytest
from unittest.mock import Mock, patch

from basic.study import (
    get_studies,
    create_study,
    get_study,
    update_study,
    delete_study
)


class TestStudyFunctions:
    @pytest.fixture
    def mock_env(self):
        with patch.dict('os.environ', {
            'API': 'https://api.example.com',
            'API_TOKEN': 'test-token'
        }):
            yield

    @pytest.fixture
    def sample_study(self):
        return {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2024-01-01T00:00:00Z",
            "name": "John Doe",
            "age": 45,
            "height": 72,
            "weight": 180,
            "sex": "MALE"
        }

    @patch('httpx.get')
    def test_get_studies(self, mock_get, mock_env, sample_study):
        mock_response = Mock()
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [sample_study]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_studies(page_size=10)
        
        assert result["count"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["name"] == "John Doe"
        
        mock_get.assert_called_once_with(
            "https://api.example.com/api/v2/studies/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            },
            params={"page_size": 10}
        )

    @patch('httpx.post')
    def test_create_study(self, mock_post, mock_env, sample_study):
        mock_response = Mock()
        mock_response.json.return_value = sample_study
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = create_study(
            name="John Doe",
            age=45,
            height=72,
            weight=180,
            sex="MALE"
        )
        
        assert result["name"] == "John Doe"
        assert result["age"] == 45
        
        mock_post.assert_called_once_with(
            "https://api.example.com/api/v2/studies/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            },
            json={
                "age": 45,
                "name": "John Doe",
                "height": 72,
                "weight": 180,
                "sex": "MALE"
            }
        )

    @patch('httpx.get')
    def test_get_study(self, mock_get, mock_env, sample_study):
        mock_response = Mock()
        mock_response.json.return_value = sample_study
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_study("123e4567-e89b-12d3-a456-426614174000")
        
        assert result["uuid"] == "123e4567-e89b-12d3-a456-426614174000"
        assert result["name"] == "John Doe"
        
        mock_get.assert_called_once_with(
            "https://api.example.com/api/v2/studies/123e4567-e89b-12d3-a456-426614174000/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            }
        )

    @patch('httpx.patch')
    def test_update_study(self, mock_patch, mock_env, sample_study):
        updated_study = {**sample_study, "name": "Jane Doe"}
        mock_response = Mock()
        mock_response.json.return_value = updated_study
        mock_response.raise_for_status = Mock()
        mock_patch.return_value = mock_response

        result = update_study(
            "123e4567-e89b-12d3-a456-426614174000",
            name="Jane Doe",
            weight=175
        )
        
        assert result["name"] == "Jane Doe"
        
        mock_patch.assert_called_once_with(
            "https://api.example.com/api/v2/studies/123e4567-e89b-12d3-a456-426614174000/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            },
            json={"name": "Jane Doe", "weight": 175}
        )

    @patch('httpx.delete')
    def test_delete_study(self, mock_delete, mock_env):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        delete_study("123e4567-e89b-12d3-a456-426614174000")
        
        mock_delete.assert_called_once_with(
            "https://api.example.com/api/v2/studies/123e4567-e89b-12d3-a456-426614174000/",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            }
        )

