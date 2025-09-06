from pydantic import BaseModel


class NewRepoCredentialsModel(BaseModel):
    name: str = ""
    username: str = ""
    password: str = ""
    token: str = ""  # Example GitHub token


class RepoCredentialsModel(BaseModel):
    id: str
    name: str
    username: str
    password: str
    token: str


class CreateNewRepoModel(BaseModel):
    url: str = "http://example.com/repo.git"
    branch: str = "main"
    name: str = "example-repo"
    credentials_name: str = ""  # Optional credentials name


class RepositoryModel(BaseModel):
    id: str | None
    url: str | None
    branch: str | None
    name: str | None
    indexed_at: str | None  # ISO formatted datetime string
    updated_at: str | None  # ISO formatted datetime string
    credentials_name: str | None = None  # Optional credentials name


class ReposResponse(BaseModel):
    repos: list[RepositoryModel] = []


class IndexerResponseModel(BaseModel):
    status: int
    message: str


class IndexModel(BaseModel):
    id: str
    repo_id: str
    compose_path: str
    indexed_at: str | None  # ISO formatted datetime string
    updated_at: str | None  # ISO formatted datetime string
