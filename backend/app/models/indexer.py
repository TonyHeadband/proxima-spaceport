from pydantic import BaseModel


class NewRepoCredentials(BaseModel):
    name: str = ""
    username: str = ""
    password: str = ""
    token: str = ""  # Example GitHub token


class RepoCredentials(BaseModel):
    id: str
    name: str
    username: str
    password: str
    token: str


class CreateNewRepo(BaseModel):
    url: str = "http://example.com/repo.git"
    name: str = "example-repo"
    credentials_name: str = ""  # Optional credentials name


class Repository(BaseModel):
    id: str | None
    url: str | None
    name: str | None
    indexed_at: str | None  # ISO formatted datetime string
    updated_at: str | None  # ISO formatted datetime string
    credentials_name: str | None = None  # Optional credentials name


class ReposResponse(BaseModel):
    repos: list[Repository] = []


class IndexerResponse(BaseModel):
    status: int
    message: str
