import httpx
from pydantic import BaseModel


class User(BaseModel):
    login: str
    id: int
    avatar_url: str


class Repository(BaseModel):
    id: int
    name: str
    full_name: str
    private: bool
    owner: User


class GitHubAPIClient:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.session = httpx.Client()

    def get_user(self, username):
        url = f"{self.BASE_URL}/users/{username}"
        return self.session.get(url)

    def create_repo(self, token, data):
        url = f"{self.BASE_URL}/user/repos"
        headers = {"Authorization": f"token {token}"}
        return self.session.post(url, json=data, headers=headers)

    def update_repo(self, token, username, repo_name, data):
        url = f"{self.BASE_URL}/repos/{username}/{repo_name}"
        headers = {"Authorization": f"token {token}"}
        return self.session.patch(url, json=data, headers=headers)

    def delete_repo(self, token, username, repo_name):
        url = f"{self.BASE_URL}/repos/{username}/{repo_name}"
        headers = {"Authorization": f"token {token}"}
        return self.session.delete(url, headers=headers)
