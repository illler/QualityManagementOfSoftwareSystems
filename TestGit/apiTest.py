import pytest
from unittest.mock import MagicMock
from client import GitHubAPIClient, User, Repository
import os


def load_env():
    with open('.env') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            key, value = line.strip().split('=', 1)
            os.environ[key] = value


load_env()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


@pytest.fixture
def api_client(mocker):
    mocker.patch.object(GitHubAPIClient, '__init__', return_value=None)
    return GitHubAPIClient()


@pytest.fixture
def new_repo(api_client, mocker):
    mock_response_data = {
        "id": 1234,
        "name": "test-repo",
        "full_name": "test_owner/test-repo",
        "private": True,
        "owner": {"login": "test_owner", "id": 123, "avatar_url": "https://example.com/avatar"}
    }
    mocker.patch.object(api_client, 'create_repo',
                        return_value=MagicMock(status_code=201, json=lambda: mock_response_data))
    mocker.patch.object(api_client, 'delete_repo', return_value=MagicMock(status_code=204))
    return Repository(**mock_response_data)


def test_get_user(api_client, mocker):
    mocker.patch.object(api_client, 'get_user', return_value=MagicMock(status_code=200,
                                                                       json=lambda: {"login": "illler", "id": 123,
                                                                                     "avatar_url": "https://example.com/avatar"}))
    response = api_client.get_user("illler")
    assert response.status_code == 200
    user = User(**response.json())
    assert user.login == "illler"


def test_create_repo(new_repo):
    assert new_repo.name == "test-repo"


def test_update_repo(api_client, mocker):
    update_data = {
        "name": "new-test-repo-name",
        "private": False
    }
    mocker.patch.object(api_client, 'update_repo', return_value=MagicMock(status_code=200, json=lambda: {
        "id": 1234,
        "name": "new-test-repo-name",
        "full_name": "test_owner/new-test-repo-name",
        "private": False,
        "owner": {"login": "test_owner", "id": 123, "avatar_url": "https://example.com/avatar"}
    }))
    response = api_client.update_repo(GITHUB_TOKEN, "test_owner", "test-repo", update_data)
    assert response.status_code == 200
    updated_repo = Repository(**response.json())
    assert updated_repo.name == update_data['name']


def test_delete_repo(api_client, mocker):
    mocker.patch.object(api_client, 'delete_repo', return_value=MagicMock(status_code=204))
    response = api_client.delete_repo(GITHUB_TOKEN, "test_owner", "test-repo")
    assert response.status_code == 204


def test_get_user_failure(api_client, mocker):
    mocker.patch.object(api_client, 'get_user', return_value=MagicMock(status_code=404))
    response = api_client.get_user("non_existing_user")
    assert response.status_code == 404


def test_create_repo_failure(api_client, mocker):
    mocker.patch.object(api_client, 'create_repo', return_value=MagicMock(status_code=400))
    response = api_client.create_repo(GITHUB_TOKEN, {"name": "invalid-repo"})
    assert response.status_code == 400


def test_update_repo_failure(api_client, mocker):
    update_data = {
        "name": "new-test-repo-name",
        "private": False
    }
    mocker.patch.object(api_client, 'update_repo', return_value=MagicMock(status_code=403))
    response = api_client.update_repo(GITHUB_TOKEN, "test_owner", "test-repo", update_data)
    assert response.status_code == 403


def test_delete_repo_failure(api_client, mocker):
    mocker.patch.object(api_client, 'delete_repo', return_value=MagicMock(status_code=403))
    response = api_client.delete_repo(GITHUB_TOKEN, "test_owner", "test-repo")
    assert response.status_code == 403
